"""
Main entry point for JobStreet scraper.
Run this script to start the scraping process.

Usage:
    python main.py
    python main.py --config config.yaml
    python main.py --keyword "Data Scientist" --max-pages 5
"""

import asyncio
import argparse
from pathlib import Path
from typing import Optional

from config import ScraperConfig
from scraper.__init__ import JobStreetScraper
from scraper.salary_parser import SalaryParser
from pipelines import DataPipeline, ExportManager
from utils import get_logger, ensure_directory

logger = get_logger(__name__)


async def main():
    """Main execution function"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="JobStreet Job Scraper - Extract job listings with salary information"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to YAML config file"
    )
    parser.add_argument(
        "--keyword",
        type=str,
        nargs="+",
        default=None,
        help="Job search keywords (e.g., 'Data Scientist' 'Backend Engineer')"
    )
    parser.add_argument(
        "--location",
        type=str,
        nargs="+",
        default=None,
        help="Locations to search (e.g., 'Kuala Lumpur' 'Selangor')"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Maximum pages per keyword"
    )
    parser.add_argument(
        "--headless",
        type=bool,
        default=True,
        help="Run browser in headless mode"
    )
    parser.add_argument(
        "--proxy",
        type=str,
        nargs="+",
        default=None,
        help="Proxy URLs to use (enables proxy rotation)"
    )
    parser.add_argument(
        "--export-only",
        type=str,
        default=None,
        help="Path to JSON file with already-scraped jobs to export"
    )
    
    args = parser.parse_args()
    
    # Ensure data directories exist
    ensure_directory("data/raw")
    ensure_directory("data/processed")
    ensure_directory("logs")
    
    # Load or create configuration
    if args.config and Path(args.config).exists():
        logger.info(f"Loading config from: {args.config}")
        config = ScraperConfig.from_yaml(args.config)
    else:
        logger.info("Using default configuration")
        config = ScraperConfig()
    
    # Override config with command line arguments
    if args.keyword:
        config.search.keywords = args.keyword
    if args.location:
        config.search.locations = args.location
    if args.max_pages:
        config.search.max_pages_per_keyword = args.max_pages
    if args.proxy:
        config.proxy.enabled = True
        config.proxy.proxy_list = args.proxy
    config.headless = args.headless
    
    logger.info("=" * 80)
    logger.info("JobStreet Scraper Started")
    logger.info("=" * 80)
    logger.info(f"Keywords: {config.search.keywords}")
    logger.info(f"Locations: {config.search.locations}")
    logger.info(f"Max pages per keyword: {config.search.max_pages_per_keyword}")
    logger.info(f"Headless mode: {config.headless}")
    logger.info(f"Stealth mode: {config.anti_detection.use_stealth}")
    
    # If export-only mode, skip scraping
    if args.export_only:
        logger.info(f"Export-only mode: Loading jobs from {args.export_only}")
        import json
        with open(args.export_only, "r", encoding="utf-8") as f:
            jobs_data = json.load(f)
        # Convert dict back to JobListing objects
        from scraper.__init__ import JobListing
        jobs = [
            JobListing(
                job_id=j.get("job_id"),
                job_title=j.get("job_title", ""),
                company_name=j.get("company_name", ""),
                location=j.get("location", ""),
                salary_raw=j.get("salary_raw", ""),
                salary_min=j.get("salary_min"),
                salary_max=j.get("salary_max"),
                salary_average=j.get("salary_average"),
                salary_currency=j.get("salary_currency", "MYR"),
                salary_type=j.get("salary_type", "monthly"),
                is_salary_negotiable=j.get("is_salary_negotiable", False),
                job_type=j.get("job_type"),
                experience_level=j.get("experience_level"),
                job_description=j.get("job_description", ""),
                requirements=j.get("requirements", ""),
                skills=j.get("skills", []),
                posting_date=j.get("posting_date"),
                expiration_date=j.get("expiration_date"),
                job_url=j.get("job_url", ""),
                company_industry=j.get("company_industry"),
                scraped_at=j.get("scraped_at", ""),
            )
            for j in jobs_data
        ]
    else:
        # Initialize scraper
        scraper = JobStreetScraper(config)
        jobs = []
        
        try:
            await scraper.initialize()
            
            # Scrape jobs for each keyword
            for keyword in config.search.keywords:
                for location in config.search.locations or [None]:
                    keyword_jobs = await scraper.search_jobs(
                        keyword=keyword,
                        location=location,
                        max_pages=config.search.max_pages_per_keyword
                    )
                    jobs.extend(keyword_jobs)
                    
                    logger.info(f"Scraped {len(keyword_jobs)} jobs for '{keyword}'")
                    
                    # Rate limiting between keywords
                    await asyncio.sleep(2)
            
            logger.info(f"Total jobs scraped: {len(jobs)}")
        
        finally:
            await scraper.close()
    
    # Process data
    logger.info("Processing data...")
    pipeline = DataPipeline(config)
    pipeline.add_jobs(jobs)
    processed_jobs = pipeline.process()
    
    # Export data
    logger.info("Exporting data...")
    export_manager = ExportManager(config)
    exported_files = export_manager.export_all(processed_jobs)
    
    # Print summary
    logger.info("=" * 80)
    logger.info("Scraping Summary")
    logger.info("=" * 80)
    logger.info(f"Total jobs scraped: {len(jobs)}")
    logger.info(f"Jobs after processing: {len(processed_jobs)}")
    
    if processed_jobs:
        # Calculate salary statistics
        salaries_with_min = [j.salary_min for j in processed_jobs if j.salary_min]
        salaries_with_max = [j.salary_max for j in processed_jobs if j.salary_max]
        
        if salaries_with_min:
            logger.info(f"Salary range (min): RM {min(salaries_with_min):,.0f} - RM {max(salaries_with_min):,.0f}")
        if salaries_with_max:
            logger.info(f"Salary range (max): RM {min(salaries_with_max):,.0f} - RM {max(salaries_with_max):,.0f}")
        
        negotiable_count = sum(1 for j in processed_jobs if j.is_salary_negotiable)
        logger.info(f"Negotiable salaries: {negotiable_count}")
    
    logger.info(f"Exported files: {exported_files}")
    logger.info("=" * 80)
    logger.info("Scraping complete!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        exit(1)
