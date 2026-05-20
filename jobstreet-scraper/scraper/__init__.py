"""
Main JobStreet scraper module.
Handles scraping of job listings with pagination, infinite scroll, and data extraction.
"""

import asyncio
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import asdict, dataclass
from urllib.parse import urljoin, quote

from playwright.async_api import async_playwright, Page, Browser, BrowserContext, TimeoutError

from config import ScraperConfig
from scraper.salary_parser import parse_salary, SalaryParser
from scraper.stealth import StealthBrowser, ProxyRotator, RateLimiter
from utils import get_logger

logger = get_logger(__name__)


@dataclass
class JobListing:
    """Data class for a single job listing"""
    job_id: Optional[str] = None
    job_title: str = ""
    company_name: str = ""
    location: str = ""
    salary_raw: str = ""
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_average: Optional[float] = None
    salary_currency: str = "MYR"
    salary_type: str = "monthly"
    is_salary_negotiable: bool = False
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    job_description: str = ""
    requirements: str = ""
    skills: List[str] = None
    posting_date: Optional[str] = None
    expiration_date: Optional[str] = None
    job_url: str = ""
    company_industry: Optional[str] = None
    job_link_hash: str = ""  # For deduplication
    scraped_at: str = ""
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if not self.scraped_at:
            self.scraped_at = datetime.now().isoformat()


class JobStreetScraper:
    """
    Main scraper class for JobStreet Indonesia.
    Handles async scraping with anti-detection and pagination support.
    """
    
    BASE_URL = "https://id.jobstreet.com/"
    SEARCH_URL = "https://id.jobstreet.com/en/jobs"
    
    def __init__(self, config: ScraperConfig):
        """
        Initialize scraper with configuration.
        
        Args:
            config: ScraperConfig object
        """
        self.config = config
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.rate_limiter = RateLimiter(requests_per_minute=30)  # Conservative rate
        self.proxy_rotator = None
        self.scraped_job_ids: Set[str] = set()
        
        if config.proxy.enabled and config.proxy.proxy_list:
            self.proxy_rotator = ProxyRotator(config.proxy.proxy_list)
    
    async def initialize(self) -> None:
        """Initialize browser and context"""
        logger.info("Initializing Playwright browser...")
        
        playwright = await async_playwright().start()
        
        # Get browser type
        if self.config.browser_type == "firefox":
            browser_type = playwright.firefox
        elif self.config.browser_type == "webkit":
            browser_type = playwright.webkit
        else:
            browser_type = playwright.chromium
        
        # Launch browser with anti-detection settings
        self.browser = await browser_type.launch(
            headless=self.config.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-first-run",
                "--no-default-browser-check",
            ]
        )
        
        # Create context with stealth settings
        context_options = {
            "user_agent": StealthBrowser.get_random_user_agent(),
            "viewport": StealthBrowser.get_random_viewport(),
        }
        
        # Add proxy if configured
        if self.proxy_rotator:
            proxy_url = self.proxy_rotator.get_next_proxy()
            if proxy_url:
                context_options["proxy"] = {"server": proxy_url}
                logger.info(f"Using proxy: {proxy_url}")
        
        self.context = await self.browser.new_context(**context_options)
        
        # Setup stealth techniques
        await StealthBrowser.setup_stealth_context(self.context, self.config)
        
        logger.info("Browser initialized successfully")
    
    async def close(self) -> None:
        """Close browser and cleanup"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info("Browser closed")
    
    async def search_jobs(
        self,
        keyword: str,
        location: Optional[str] = None,
        max_pages: Optional[int] = None
    ) -> List[JobListing]:
        return await self.scrape_search_page(keyword, location, max_pages)

    async def scrape_search_page(
        self,
        keyword: str,
        location: Optional[str] = None,
        max_pages: Optional[int] = None
    ) -> List[JobListing]:
        """Scrape search results across multiple list pages."""
        if max_pages is None:
            max_pages = self.config.search.max_pages_per_keyword

        jobs = []
        page = await self.context.new_page()

        try:
            await StealthBrowser.inject_stealth_js(page)
            if location:
                loc_fragment = location.replace(' ', '-')
                search_url = f"https://id.jobstreet.com/{quote(keyword)}-jobs/in-{quote(loc_fragment)}"
            else:
                search_url = self._build_search_url(keyword, location)

            logger.info(f"Searching for '{keyword}' in '{location or 'All locations'}' | max_pages={max_pages}")
            await page.goto(search_url, wait_until="networkidle", timeout=self.config.anti_detection.timeout)
            await StealthBrowser.random_delay(
                self.config.anti_detection.min_delay,
                self.config.anti_detection.max_delay
            )
            if self.config.anti_detection.enable_mouse_movements:
                await StealthBrowser.random_mouse_movements(page)

            current_page = 1
            while current_page <= max_pages:
                logger.info(f"Scraping page {current_page}/{max_pages}")

                try:
                    await page.wait_for_selector(
                        "div[data-search-sol-meta], a[data-automation='jobTitle'], a[data-testid='job-card-title'], [data-automation='jobSalary']",
                        timeout=self.config.anti_detection.timeout
                    )
                except TimeoutError:
                    logger.warning(f"Timeout waiting for job listings on page {current_page}")
                    break

                page_jobs = await self._extract_jobs_from_page(page)
                jobs.extend(page_jobs)
                logger.info(f"Loaded {len(page_jobs)} jobs from page {current_page}")

                if current_page >= max_pages:
                    logger.info("Reached user max_pages limit")
                    break

                current_cards = len(await page.query_selector_all("div[data-search-sol-meta]"))
                has_next = await self._handle_pagination(page, current_page, max_pages, current_cards)
                if not has_next:
                    logger.info("No more jobs found after page %s", current_page)
                    break

                current_page += 1
                await asyncio.sleep(random.uniform(3, 7))

        except Exception as e:
            logger.error(f"Error scraping jobs for keyword '{keyword}': {e}", exc_info=True)
        finally:
            await page.close()

        return jobs
    
    async def _extract_jobs_from_page(self, page: Page) -> List[JobListing]:
        """Extract job listings from current page"""
        jobs = []
        
        try:
            job_elements = await page.query_selector_all("div[data-search-sol-meta]")
            logger.debug(f"Found {len(job_elements)} job elements")
            
            for idx, element in enumerate(job_elements):
                try:
                    job_url = await element.get_attribute("href")
                    if not job_url:
                        link = await element.query_selector(
                            "a[data-automation='jobTitle'], a[id^='job-title-'], a[href*='/job/']"
                        )
                        if link:
                            job_url = await link.get_attribute("href")
                    
                    if not job_url or job_url in self.scraped_job_ids:
                        continue
                    
                    if job_url.startswith("/"):
                        job_url = urljoin(self.BASE_URL, job_url)

                    # Extract job metadata from the card wrapper
                    job_title = await self._safe_text_extract(
                        element,
                        "a[data-automation='jobTitle'], a[data-testid='job-card-title'], h1, h2, h3"
                    )
                    company_name = await self._safe_text_extract(
                        element,
                        "a[aria-label^='Jobs at'], [data-automation='jobAdvertiser'], [data-type='company'], span[class*='company']"
                    )
                    location = await self._safe_text_extract(
                        element,
                        "a[data-automation='jobLocation'], span[data-automation='jobCardLocation'], [data-automation*='location'], [class*='location']"
                    )
                    salary_raw = await self._safe_text_extract(
                        element,
                        "[data-automation='jobSalary'], [data-automation*='salary'], [class*='salary'], span[class*='salary']"
                    )
                    job_type = await self._safe_text_extract(
                        element,
                        "[data-testid='work-arrangement'], [data-automation*='type'], [class*='job-type'], span[class*='type']"
                    )
                    job_description = await self._safe_text_extract(
                        element,
                        "[data-automation='jobShortDescription'], [data-testid='job-card-teaser'], [class*='teaser']"
                    )

                    if not location or not salary_raw or not job_title:
                        text_content = (await element.text_content()) or ""
                        location = location or self._extract_location_from_text(text_content)
                        salary_raw = salary_raw or self._extract_salary_from_text(text_content)
                        job_title = job_title or self._extract_title_from_text(text_content)

                    parsed_salary = parse_salary(salary_raw)
                    
                    job_id = await self._extract_job_id_from_card(element)
                    
                    job = JobListing(
                        job_id=job_id,
                        job_title=job_title or "",
                        company_name=company_name or "",
                        location=location or "",
                        salary_raw=salary_raw or "",
                        salary_min=parsed_salary.salary_min,
                        salary_max=parsed_salary.salary_max,
                        salary_average=parsed_salary.salary_average,
                        salary_currency=parsed_salary.currency.value,
                        salary_type=parsed_salary.salary_type.value,
                        is_salary_negotiable=parsed_salary.is_negotiable,
                        job_type=job_type,
                        job_description=job_description,
                        job_url=job_url,
                        job_link_hash=hash(job_url) % ((2 ** 63) - 1),
                    )
                    
                    try:
                        detail_info = await self._extract_job_details(job_url, page)
                        if detail_info:
                            job.job_description = job.job_description or detail_info.get("description", "")
                            job.requirements = detail_info.get("requirements", "")
                            job.skills = detail_info.get("skills", [])
                            job.experience_level = detail_info.get("experience_level", "")
                            job.posting_date = detail_info.get("posting_date", "")
                            job.job_id = job.job_id or detail_info.get("job_id", "")
                    except Exception as e:
                        logger.debug(f"Error extracting job details: {e}")
                    
                    jobs.append(job)
                    self.scraped_job_ids.add(job_url)
                    
                except Exception as e:
                    logger.debug(f"Error extracting job {idx}: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error extracting jobs from page: {e}")
        
        return jobs

    async def _extract_job_id_from_card(self, element) -> Optional[str]:
        """Extract the job id from the card wrapper metadata."""
        try:
            meta = await element.get_attribute("data-search-sol-meta")
            if meta:
                payload = json.loads(meta)
                return payload.get("jobId")
        except Exception:
            pass
        return None
    
    async def _extract_job_details(self, job_url: str, parent_page: Page) -> Optional[Dict]:
        """
        Extract detailed job information from job detail page.
        
        Args:
            job_url: URL of the job listing
            parent_page: Parent page (for context)
            
        Returns:
            Dictionary with job details or None if error
        """
        detail_page = await self.context.new_page()

        try:
            await StealthBrowser.inject_stealth_js(detail_page)
            await detail_page.goto(job_url, wait_until="networkidle", timeout=self.config.anti_detection.timeout)

            # Random delay to look human
            await StealthBrowser.random_delay(
                self.config.anti_detection.min_delay * 0.5,
                self.config.anti_detection.max_delay * 0.5
            )

            # Rich set of selectors for JobStreet detail pages
            title = await self._safe_text_extract(
                detail_page,
                "h1[data-automation='jobTitle'], h1[data-testid='job-title'], h1, [data-automation='jobTitle']"
            )

            description = await self._safe_text_extract(
                detail_page,
                "[data-automation='jobDescription'], [data-automation='jobDetailDescription'], [data-testid='job-description'], div[class*='job-description'], article, section"
            )

            requirements = await self._safe_text_extract(
                detail_page,
                "[data-automation='requirements'], [data-automation='qualifications'], [class*='requirements'], [class*='qualifications'], ul[class*='require'], ol[class*='require']"
            )

            experience_level = await self._safe_text_extract(
                detail_page,
                "[data-automation='experience'], [class*='experience'], [data-automation*='level'], .experience-level, span[aria-label*='experience']"
            )

            posting_date = await self._safe_text_extract(
                detail_page,
                "time[datetime], [data-automation='postingDate'], [aria-label*='Posted']"
            )

            salary = await self._safe_text_extract(
                detail_page,
                "[data-automation='jobSalary'], [data-automation*='salary'], [aria-label^='Salary'], [class*='salary']"
            )

            # Try to extract skills and other structured info
            skills = await self._extract_skills(detail_page)

            # Try meta tags / canonical / URL for job id
            job_id = None
            try:
                meta_id = await detail_page.query_selector("meta[name='jobId'], meta[data-automation='jobId']")
                if meta_id:
                    job_id = await meta_id.get_attribute('content')
            except Exception:
                pass

            if not job_id:
                # Fallback to URL segment
                job_id = job_url.split("/")[-1].split('?')[0]

            return {
                "job_title": title,
                "description": description,
                "requirements": requirements,
                "skills": skills,
                "experience_level": experience_level,
                "job_id": job_id,
                "posting_date": posting_date,
                "salary": salary,
            }

        except TimeoutError:
            logger.warning(f"Timeout loading job detail: {job_url}")
            return None
        except Exception as e:
            logger.debug(f"Error extracting job details from {job_url}: {e}")
            return None
        finally:
            await detail_page.close()
    
    async def _extract_skills(self, page: Page) -> List[str]:
        """Extract skills from job page"""
        skills = []
        try:
            # Look for skill tags, chips, badges, or list items
            skill_elements = await page.query_selector_all(
                "[data-automation='skill'], [data-automation*='skill'], [class*='skill'], [class*='tag'], [class*='badge'], li[class*='skill'], span[class*='tag'], a[class*='tag']"
            )
            
            for element in skill_elements:
                text = await element.text_content()
                if text:
                    skill = text.strip()
                    if skill and len(skill) < 50:  # Filter out long text
                        skills.append(skill)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_skills = []
            for skill in skills:
                if skill.lower() not in seen:
                    seen.add(skill.lower())
                    unique_skills.append(skill)
            
            return unique_skills[:20]  # Return top 20 skills
        
        except Exception as e:
            logger.debug(f"Error extracting skills: {e}")
            return []
    
    async def _handle_pagination(self, page: Page, current_page: int, max_pages: int, current_cards: int) -> bool:
        """Try to load the next batch of jobs using hybrid pagination strategy."""
        logger.info(f"Attempting pagination for page {current_page}/{max_pages}")

        if current_page >= max_pages:
            logger.info("Already reached requested max_pages, no further pagination")
            return False

        old_url = page.url
        next_page_number = current_page + 1

        for attempt in range(1, self.config.retry_attempts + 1):
            logger.debug(
                "Pagination attempt %d/%d | current_url=%s | current_cards=%d",
                attempt,
                self.config.retry_attempts,
                old_url,
                current_cards,
            )

            try:
                if await self._click_load_more(page):
                    new_cards = await self._wait_for_job_card_increase(page, current_cards, timeout=20)
                    if new_cards > current_cards:
                        logger.info("Loaded %d new jobs via Load More", new_cards - current_cards)
                        return True
                    logger.warning("Load More clicked but no new jobs appeared")

                if await self._click_next_page_button(page):
                    new_cards = await self._wait_for_job_card_increase(page, current_cards, timeout=20)
                    if page.url != old_url or new_cards > current_cards:
                        logger.info("Pagination succeeded by Next button")
                        return True
                    logger.warning("Next button clicked but page did not change or add jobs")

                if await self._scroll_to_load_more(page, current_cards):
                    new_cards = await self._wait_for_job_card_increase(page, current_cards, timeout=20)
                    if new_cards > current_cards:
                        logger.info("Loaded %d new jobs via scrolling", new_cards - current_cards)
                        return True
                    logger.warning("Scroll attempt completed but did not add new job cards")

                if await self._navigate_to_page_url(page, next_page_number):
                    logger.info("Navigated directly to page %d", next_page_number)
                    return True

                logger.info("Hybrid pagination attempt %d failed", attempt)
                if attempt < self.config.retry_attempts:
                    wait_seconds = random.uniform(self.config.retry_delay, self.config.retry_delay + 3)
                    logger.debug("Waiting %.1f seconds before retry", wait_seconds)
                    await asyncio.sleep(wait_seconds)
                    continue
                await self._take_page_screenshot(page, f"pagination_fail_page{current_page}")
                return False
            except Exception as e:
                logger.warning("Pagination attempt %d failed: %s", attempt, e)
                if attempt == self.config.retry_attempts:
                    await self._take_page_screenshot(page, f"pagination_fail_page{current_page}")
                    return False
                await asyncio.sleep(random.uniform(self.config.retry_delay, self.config.retry_delay + 2))
        return False

    async def _click_load_more(self, page: Page) -> bool:
        selectors = [
            "button:has-text('Load More')",
            "button:has-text('Load more')",
            "button:has-text('Lihat Lagi')",
            "button:has-text('Muat Lebih')",
            "[data-automation*='loadMore']",
            "[data-automation*='load-more']",
            "[data-testid*='load-more']",
        ]
        for selector in selectors:
            button = await page.query_selector(selector)
            if button and await button.is_visible():
                try:
                    await button.click()
                    logger.info("Clicked Load More button using selector: %s", selector)
                    await asyncio.sleep(random.uniform(1, 2))
                    return True
                except Exception as e:
                    logger.warning("Failed clicking Load More button: %s", e)
                    await self._take_page_screenshot(page, "load_more_click_fail")
                    return False
        return False

    async def _click_next_page_button(self, page: Page) -> bool:
        selectors = [
            "a[rel='nofollow next']",
            "a[rel='next']",
            "button:has-text('Next')",
            "a:has-text('Next')",
            "button:has-text('Selanjutnya')",
            "a:has-text('Selanjutnya')",
            "button:has-text('>')",
            "a:has-text('>')",
            "button[aria-label*='Next']",
            "a[aria-label*='Next']",
            "button[aria-label*='Selanjutnya']",
            "a[aria-label*='Selanjutnya']",
            "button[data-automation*='next']",
            "a[data-automation*='next']",
            "button[data-testid*='next']",
            "a[data-testid*='next']",
            "li.pagination-next a",
            "div.pagination a:has-text('Next')",
            "div.pagination a:has-text('Selanjutnya')",
        ]
        initial_url = page.url

        for selector in selectors:
            button = await page.query_selector(selector)
            if not button:
                continue
            try:
                if not await button.is_visible():
                    continue

                logger.info("Trying next page selector: %s", selector)
                await button.scroll_into_view_if_needed()
                await asyncio.sleep(random.uniform(0.4, 1.0))
                await button.click()

                try:
                    await page.wait_for_load_state("networkidle", timeout=self.config.anti_detection.timeout)
                except TimeoutError:
                    logger.debug("No navigation detected after clicking next page selector %s", selector)

                await asyncio.sleep(random.uniform(1.0, 2.5))

                if page.url != initial_url:
                    logger.info("Next page navigation succeeded via selector %s", selector)
                    return True

                card_count = len(await page.query_selector_all("div[data-search-sol-meta]"))
                if card_count > 0:
                    logger.info("Next page selector %s loaded job cards without URL change", selector)
                    return True

            except Exception as e:
                logger.warning("Next page click failed for selector %s: %s", selector, e)
                continue

        logger.debug("No next page button selector succeeded")
        return False

    async def _scroll_to_load_more(self, page: Page, previous_card_count: int, scroll_attempts: int = 12) -> bool:
        logger.info("Scrolling to load more jobs (up to %d attempts)", scroll_attempts)
        last_count = previous_card_count

        for attempt in range(1, scroll_attempts + 1):
            logger.debug("Scroll attempt %d/%d", attempt, scroll_attempts)
            try:
                job_cards = await page.query_selector_all("div[data-search-sol-meta]")
                if job_cards:
                    await job_cards[-1].scroll_into_view_if_needed()
                else:
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

                await asyncio.sleep(random.uniform(0.8, 1.5))
                await page.evaluate("window.scrollBy(0, window.innerHeight * 0.5)")
                await asyncio.sleep(random.uniform(1.0, 1.8))

                current_count = len(await page.query_selector_all("div[data-search-sol-meta]"))
                if current_count > last_count:
                    logger.info("Detected %d new job cards after scroll", current_count - last_count)
                    return True
                last_count = current_count
            except Exception as e:
                logger.debug("Scroll attempt %d failed: %s", attempt, e)
                await asyncio.sleep(random.uniform(0.5, 1.0))

        logger.debug("Scroll loading did not add any new job cards")
        return False

    async def _navigate_to_page_url(self, page: Page, next_page_number: int) -> bool:
        next_url = self._build_next_search_page_url(page.url, next_page_number)
        if not next_url or next_url == page.url:
            logger.debug("No direct URL fallback available for page %s", page.url)
            return False

        logger.info("Attempting direct page URL fallback: %s", next_url)
        try:
            await page.goto(next_url, wait_until="networkidle", timeout=self.config.anti_detection.timeout)
            await asyncio.sleep(random.uniform(2.0, 4.0))
            card_count = len(await page.query_selector_all("div[data-search-sol-meta]"))
            if card_count > 0:
                logger.info("Direct URL navigation succeeded with %d job cards", card_count)
                return True
            logger.warning("Direct page URL opened but no job cards found")
            return False
        except Exception as e:
            logger.warning("Direct URL navigation failed: %s", e)
            return False

    def _build_next_search_page_url(self, current_url: str, next_page_number: int) -> Optional[str]:
        try:
            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

            parsed = urlparse(current_url)
            query = parse_qs(parsed.query, keep_blank_values=True)

            if "page" in query:
                query["page"] = [str(next_page_number)]
                new_query = urlencode(query, doseq=True)
                return urlunparse(parsed._replace(query=new_query))

            path = parsed.path
            if re.search(r"/page-\d+/?$", path):
                new_path = re.sub(r"/page-\d+/?$", f"/page-{next_page_number}", path)
                return urlunparse(parsed._replace(path=new_path))

            if parsed.query:
                return urlunparse(parsed._replace(query=parsed.query + f"&page={next_page_number}"))

            if path.endswith("/"):
                return urlunparse(parsed._replace(path=f"{path}page-{next_page_number}"))

            return urlunparse(parsed._replace(path=f"{path}/page-{next_page_number}"))
        except Exception as e:
            logger.debug("Failed to build next page URL from %s: %s", current_url, e)
            return None

    async def _wait_for_job_card_increase(self, page: Page, old_count: int, timeout: int = 15) -> int:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            await asyncio.sleep(0.8)
            current_count = len(await page.query_selector_all("div[data-search-sol-meta]"))
            if current_count > old_count:
                return current_count
        return old_count

    async def _take_page_screenshot(self, page: Page, name: str) -> None:
        try:
            screenshot_dir = Path("logs/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=str(screenshot_dir / f"{name}_{timestamp}.png"), full_page=True)
            logger.info("Saved screenshot for pagination issue: %s", screenshot_dir / f"{name}_{timestamp}.png")
        except Exception as e:
            logger.warning("Failed to capture screenshot: %s", e)
    
    def _build_search_url(self, keyword: str, location: Optional[str] = None) -> str:
        """Build search URL with parameters"""
        url = self.SEARCH_URL
        params = []
        
        if keyword:
            params.append(f"q={quote(keyword)}")
        
        if location:
            params.append(f"location={quote(location)}")
        
        # Add common filters
        params.append("sortBy=-DATE")  # Sort by most recent
        
        if params:
            url += "?" + "&".join(params)
        
        return url
    
    async def _safe_text_extract(
        self,
        element,
        selector: str,
        default: str = ""
    ) -> str:
        """Safely extract text from element"""
        try:
            el = await element.query_selector(selector)
            if el:
                text = await el.text_content()
                if text:
                    return text.strip()
        except Exception:
            pass
        return default

    @staticmethod
    def _extract_location_from_text(text: str) -> str:
        """Fallback location extraction from raw job card text."""
        match = re.search(r"([A-Za-zÀ-ÿ0-9 ]+,\s*[A-Za-zÀ-ÿ0-9 ]+)", text)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _extract_salary_from_text(text: str) -> str:
        """Fallback salary extraction from raw job card text."""
        match = re.search(
            r"Rp\s*[\d\.]+(?:\s*[–-]\s*Rp\s*[\d\.]+)?(?:\s*per\s*\w+)?",
            text,
            re.IGNORECASE,
        )
        return match.group(0).strip() if match else ""

    @staticmethod
    def _extract_title_from_text(text: str) -> str:
        """Fallback title extraction from raw job card text."""
        match = re.search(r"([A-Z][A-Za-z0-9 &\-]{4,100})", text)
        return match.group(1).strip() if match else ""


# Import at end to avoid circular imports
import random
