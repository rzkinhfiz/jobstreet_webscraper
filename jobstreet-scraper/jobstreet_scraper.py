"""
Production-ready JobStreet scraper using async Playwright.

- Two-stage scraping (list -> detail)
- Concurrency control (configurable semaphore)
- Retries, human-like behaviour, screenshots on error
- YAML or dataclass configuration

Usage (example):
python jobstreet_scraper.py --keyword "Data Scientist" --location "Jakarta Raya" --max-pages 3 --headless True

"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import random
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

import yaml
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from playwright.async_api import async_playwright, Page, Browser, TimeoutError

from scraper.salary_parser import parse_salary
from scraper.stealth import StealthBrowser

LOG = logging.getLogger("jobstreet_scraper")


@dataclass
class ScraperConfig:
    headless: bool = True
    max_pages_per_keyword: int = 3
    concurrency: int = 4
    timeout: int = 30000
    min_delay: float = 0.5
    max_delay: float = 2.0
    screenshots_dir: str = "logs/screenshots"

    @classmethod
    def from_yaml(cls, path: Optional[str]):
        if not path:
            return cls()
        data = yaml.safe_load(Path(path).read_text())
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class JobRecord:
    job_id: Optional[str]
    job_title: str
    company_name: str
    location: str
    salary_raw: str
    salary_parsed: Dict
    job_type: Optional[str]
    experience_level: Optional[str]
    job_description: str
    requirements: str
    skills: List[str]
    posting_date: Optional[str]
    job_url: str
    scraped_at: str


class JobStreetScraper:
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.browser: Optional[Browser] = None
        self.semaphore = asyncio.Semaphore(config.concurrency)

    async def initialize(self) -> None:
        LOG.info("Starting Playwright browser (headless=%s)", self.config.headless)
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.config.headless, args=["--disable-blink-features=AutomationControlled"]) 

    async def close(self) -> None:
        if self.browser:
            await self.browser.close()

    def _make_search_url(self, keyword: str, location: Optional[str]) -> str:
        # Use JobStreet friendly path when location provided
        base = "https://id.jobstreet.com/"
        if location:
            loc_fragment = location.replace(" ", "-")
            return f"{base}{keyword.replace(' ', '%20')}-jobs/in-{loc_fragment}"
        return f"{base}en/jobs?q={keyword.replace(' ', '%20')}"

    async def _open_page(self) -> Page:
        assert self.browser, "Browser not initialized"
        ctx = await self.browser.new_context(user_agent=StealthBrowser.get_random_user_agent(), viewport=StealthBrowser.get_random_viewport())
        await StealthBrowser.setup_stealth_context(ctx, self.config)
        page = await ctx.new_page()
        return page

    async def scrape(self, keywords: List[str], locations: List[str]) -> List[JobRecord]:
        results: List[JobRecord] = []
        await self.initialize()

        try:
            for keyword in keywords:
                for location in (locations or [None]):
                    url = self._make_search_url(keyword, location)
                    LOG.info("Searching: %s | %s -> %s", keyword, location or 'All', url)
                    page = await self._open_page()
                    try:
                        await StealthBrowser.inject_stealth_js(page)
                        await page.goto(url, wait_until="networkidle", timeout=self.config.timeout)
                        await StealthBrowser.random_delay(self.config.min_delay, self.config.max_delay)
                        if self.config.concurrency > 1:
                            await StealthBrowser.random_mouse_movements(page)

                        list_stage = await self._extract_listings_from_page(page)
                        LOG.info("Found %d preliminary listings", len(list_stage))

                        # Stage 2: detail pages with concurrency control
                        tasks = [self._bounded_extract_detail(item) for item in list_stage]
                        details = await asyncio.gather(*tasks)
                        results.extend([d for d in details if d])

                    except Exception as e:
                        LOG.exception("Error during search for %s in %s: %s", keyword, location, e)
                    finally:
                        try:
                            await page.context.close()
                        except Exception:
                            pass

        finally:
            await self.close()

        return results

    async def _extract_listings_from_page(self, page: Page) -> List[Dict]:
        """Extract preliminary listing info (stage 1). Returns list of dicts containing job_url and preliminary fields."""
        items: List[Dict] = []
        # Wait for job card wrapper
        try:
            await page.wait_for_selector("div[data-search-sol-meta]", timeout=self.config.timeout)
        except TimeoutError:
            LOG.warning("No job cards found on list page")
            return items

        elements = await page.query_selector_all("div[data-search-sol-meta]")
        for el in elements:
            try:
                link = await el.query_selector("a[data-automation='jobTitle'], a[data-testid='job-card-title']")
                href = None
                if link:
                    href = await link.get_attribute('href')
                if not href:
                    continue
                if href.startswith('/'):
                    href = 'https://id.jobstreet.com' + href

                title = (await (link.get_property('innerText') if link else el.get_property('innerText'))).json_value() if link else ""
                company = await self._safe_text(el, "a[aria-label^='Jobs at'], [data-automation='jobAdvertiser']")
                location = await self._safe_text(el, "a[data-automation='jobLocation'], span[data-automation='jobCardLocation']")
                salary_raw = await self._safe_text(el, "[data-automation='jobSalary'], [data-automation*='salary']")

                items.append({
                    'job_url': href,
                    'title': (title or '').strip(),
                    'company': company,
                    'location': location,
                    'salary_raw': salary_raw,
                })
            except Exception:
                LOG.exception("Failed to parse card element")
        return items

    async def _safe_text(self, element, selector: str) -> str:
        try:
            el = await element.query_selector(selector)
            if not el:
                return ""
            txt = await el.text_content()
            return (txt or "").strip()
        except Exception:
            return ""

    async def _bounded_extract_detail(self, item: Dict) -> Optional[JobRecord]:
        async with self.semaphore:
            return await self._extract_job_detail_with_retries(item)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10), retry=retry_if_exception_type(Exception))
    async def _extract_job_detail_with_retries(self, item: Dict) -> Optional[JobRecord]:
        page = await self._open_page()
        url = item['job_url']
        try:
            await StealthBrowser.inject_stealth_js(page)
            await page.goto(url, wait_until='networkidle', timeout=self.config.timeout)
            await StealthBrowser.random_delay(self.config.min_delay, self.config.max_delay)
            await StealthBrowser.human_like_scroll(page, max_scrolls=3)

            title = item.get('title') or await self._safe_text(page, "h1[data-automation='jobTitle'], h1")
            company = item.get('company') or await self._safe_text(page, "a[aria-label^='Jobs at'], [data-automation='jobAdvertiser']")
            location = item.get('location') or await self._safe_text(page, "[data-automation='jobLocation'], [class*='location']")
            salary_raw = item.get('salary_raw') or await self._safe_text(page, "[data-automation='jobSalary'], [data-automation*='salary']")

            description = await self._safe_text(page, "[data-automation='jobDescription'], [data-automation='jobDetailDescription'], [data-testid='job-description']")
            requirements = await self._safe_text(page, "[data-automation='requirements'], [class*='qualifications'], ul, ol")
            experience = await self._safe_text(page, "[data-automation='experience'], .experience-level, [aria-label*='experience']")
            job_type = await self._safe_text(page, "[data-automation*='type'], [data-automation='jobType'], [class*='job-type']")
            posting = await self._safe_text(page, "time[datetime], [data-automation='postingDate'], [aria-label*='Posted']")

            # Skills extraction - conservative selectors
            skills = []
            try:
                chips = await page.query_selector_all("[data-automation='skill'], [class*='skill'], [class*='tag'], [class*='badge']")
                for c in chips:
                    t = await c.text_content()
                    if t:
                        skills.append(t.strip())
            except Exception:
                pass

            parsed = parse_salary(salary_raw)

            job_id = None
            try:
                meta = await page.query_selector("div[data-search-sol-meta]")
                if meta:
                    raw = await meta.get_attribute('data-search-sol-meta')
                    if raw:
                        import json as _json
                        payload = _json.loads(raw)
                        job_id = payload.get('jobId')
            except Exception:
                pass

            if not job_id:
                # Fallback to last path segment
                job_id = url.split('/')[-1].split('?')[0]

            rec = JobRecord(
                job_id=job_id,
                job_title=title or "",
                company_name=company or "",
                location=location or "",
                salary_raw=salary_raw or "",
                salary_parsed=asdict(parsed),
                job_type=job_type,
                experience_level=experience,
                job_description=description or "",
                requirements=requirements or "",
                skills=list(dict.fromkeys([s for s in skills if s])),
                posting_date=posting or "",
                job_url=url,
                scraped_at=datetime.utcnow().isoformat(),
            )
            return rec

        except Exception as e:
            LOG.exception("Error extracting detail %s: %s", url, e)
            # screenshot
            try:
                Path(self.config.screenshots_dir).mkdir(parents=True, exist_ok=True)
                ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                await page.screenshot(path=f"{self.config.screenshots_dir}/error_{ts}.png", full_page=True)
            except Exception:
                pass
            raise
        finally:
            try:
                await page.context.close()
            except Exception:
                pass


def save_results_json(results: List[JobRecord], outpath: str) -> None:
    Path(outpath).parent.mkdir(parents=True, exist_ok=True)
    data = [asdict(r) for r in results]
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    LOG.info("Saved %d records to %s", len(results), outpath)


def parse_args(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--keyword', '-k', nargs='+', required=True)
    p.add_argument('--location', '-l', nargs='*', default=[])
    p.add_argument('--max-pages', type=int, default=3)
    p.add_argument('--headless', action='store_true')
    p.add_argument('--config', type=str, default=None)
    p.add_argument('--out', type=str, default='data/raw/jobs_output.json')
    return p.parse_args(argv)


async def main(argv=None):
    args = parse_args(argv)
    cfg = ScraperConfig.from_yaml(args.config)
    cfg.headless = args.headless if args.config is None else cfg.headless
    cfg.max_pages_per_keyword = args.max_pages
    cfg.concurrency = max(1, cfg.concurrency)

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(name)s:%(lineno)d - %(message)s')

    scraper = JobStreetScraper(cfg)
    results = await scraper.scrape(args.keyword, args.location)
    save_results_json(results, args.out)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOG.info('Interrupted')
