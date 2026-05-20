"""
Data processing pipelines for JobStreet scraper.
Handles data transformation, deduplication, and export to various formats.
"""

import json
import csv
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
import pandas as pd

from scraper.__init__ import JobListing
from config import ScraperConfig
from utils import get_logger, ensure_directory

logger = get_logger(__name__)


class DataPipeline:
    """Base class for data processing pipelines"""
    
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.jobs: List[JobListing] = []
    
    def add_jobs(self, jobs: List[JobListing]) -> None:
        """Add jobs to pipeline"""
        self.jobs.extend(jobs)
    
    def deduplicate(self) -> List[JobListing]:
        """Remove duplicate jobs using job_id primary key, fallback fingerprint.

        Fingerprint: lower(title) || lower(company) || lower(location)
        """
        seen_ids = set()
        seen_fp = set()
        unique_jobs = []

        for job in self.jobs:
            jid = job.job_id
            fp = f"{(job.job_title or '').strip().lower()}||{(job.company_name or '').strip().lower()}||{(job.location or '').strip().lower()}"

            if jid:
                if jid in seen_ids:
                    continue
                seen_ids.add(jid)
                # also add fingerprint to prevent later duplicates
                seen_fp.add(fp)
                unique_jobs.append(job)
            else:
                if fp in seen_fp:
                    continue
                seen_fp.add(fp)
                unique_jobs.append(job)

        logger.info(f"Deduplicated: {len(self.jobs)} -> {len(unique_jobs)} jobs")
        self.jobs = unique_jobs
        return unique_jobs
    
    def filter_salaries(self) -> List[JobListing]:
        """Filter out jobs with missing salary data"""
        original_count = len(self.jobs)
        self.jobs = [job for job in self.jobs if job.salary_min or job.salary_max]
        
        filtered_count = original_count - len(self.jobs)
        logger.info(f"Filtered out {filtered_count} jobs without salary info")
        return self.jobs
    
    def process(self) -> List[JobListing]:
        """Run all processing steps"""
        logger.info(f"Processing {len(self.jobs)} jobs...")
        
        self.deduplicate()
        self.filter_salaries()
        
        logger.info(f"Processing complete: {len(self.jobs)} jobs ready for export")
        return self.jobs


class JSONExporter:
    """Export jobs to JSON format"""
    
    @staticmethod
    def export(jobs: List[JobListing], filepath: str) -> None:
        """
        Export jobs to JSON file.
        
        Args:
            jobs: List of JobListing objects
            filepath: Output file path
        """
        ensure_directory(str(Path(filepath).parent))
        
        data = []
        for job in jobs:
            job_dict = {
                "job_id": job.job_id,
                "job_title": job.job_title,
                "company_name": job.company_name,
                "location": job.location,
                "salary": {
                    "raw": job.salary_raw,
                    "min": job.salary_min,
                    "max": job.salary_max,
                    "average": job.salary_average,
                    "currency": job.salary_currency,
                    "type": job.salary_type,
                    "negotiable": job.is_salary_negotiable,
                },
                "job_type": job.job_type,
                "experience_level": job.experience_level,
                "job_description": job.job_description,
                "requirements": job.requirements,
                "skills": job.skills,
                "posting_date": job.posting_date,
                "expiration_date": job.expiration_date,
                "job_url": job.job_url,
                "company_industry": job.company_industry,
                "scraped_at": job.scraped_at,
            }
            data.append(job_dict)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Exported {len(jobs)} jobs to JSON: {filepath}")


class ParquetExporter:
    """Export jobs to Parquet format (columnar storage)"""
    
    @staticmethod
    def export(jobs: List[JobListing], filepath: str) -> None:
        """
        Export jobs to Parquet file.
        
        Args:
            jobs: List of JobListing objects
            filepath: Output file path
        """
        ensure_directory(str(Path(filepath).parent))
        
        # Convert to DataFrame
        data = []
        for job in jobs:
            data.append({
                "job_id": job.job_id,
                "job_title": job.job_title,
                "company_name": job.company_name,
                "location": job.location,
                "salary_raw": job.salary_raw,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "salary_average": job.salary_average,
                "salary_currency": job.salary_currency,
                "salary_type": job.salary_type,
                "is_salary_negotiable": job.is_salary_negotiable,
                "job_type": job.job_type,
                "experience_level": job.experience_level,
                "job_description": job.job_description,
                "requirements": job.requirements,
                "skills": "|".join(job.skills) if job.skills else "",  # Convert list to string
                "posting_date": job.posting_date,
                "expiration_date": job.expiration_date,
                "job_url": job.job_url,
                "company_industry": job.company_industry,
                "scraped_at": job.scraped_at,
            })
        
        df = pd.DataFrame(data)
        
        # Save to Parquet
        df.to_parquet(filepath, index=False, engine="pyarrow")
        
        logger.info(f"Exported {len(jobs)} jobs to Parquet: {filepath}")


class CSVExporter:
    """Export jobs to CSV format"""
    
    @staticmethod
    def export(jobs: List[JobListing], filepath: str) -> None:
        """
        Export jobs to CSV file.
        
        Args:
            jobs: List of JobListing objects
            filepath: Output file path
        """
        ensure_directory(str(Path(filepath).parent))
        
        fieldnames = [
            "job_id", "job_title", "company_name", "location",
            "salary_raw", "salary_min", "salary_max", "salary_average",
            "salary_currency", "salary_type", "is_salary_negotiable",
            "job_type", "experience_level", "job_description", "requirements",
            "skills", "posting_date", "expiration_date", "job_url",
            "company_industry", "scraped_at"
        ]
        
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for job in jobs:
                writer.writerow({
                    "job_id": job.job_id,
                    "job_title": job.job_title,
                    "company_name": job.company_name,
                    "location": job.location,
                    "salary_raw": job.salary_raw,
                    "salary_min": job.salary_min,
                    "salary_max": job.salary_max,
                    "salary_average": job.salary_average,
                    "salary_currency": job.salary_currency,
                    "salary_type": job.salary_type,
                    "is_salary_negotiable": job.is_salary_negotiable,
                    "job_type": job.job_type,
                    "experience_level": job.experience_level,
                    "job_description": job.job_description,
                    "requirements": job.requirements,
                    "skills": "|".join(job.skills) if job.skills else "",
                    "posting_date": job.posting_date,
                    "expiration_date": job.expiration_date,
                    "job_url": job.job_url,
                    "company_industry": job.company_industry,
                    "scraped_at": job.scraped_at,
                })
        
        logger.info(f"Exported {len(jobs)} jobs to CSV: {filepath}")


class ExportManager:
    """Manage exports to multiple formats"""
    
    def __init__(self, config: ScraperConfig):
        self.config = config
    
    def export_all(self, jobs: List[JobListing]) -> Dict[str, str]:
        """
        Export jobs to all configured formats.
        
        Args:
            jobs: List of JobListing objects
            
        Returns:
            Dictionary with format -> filepath mapping
        """
        exported_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.config.export.save_json:
            filepath = self.config.get_raw_data_path(f"jobs_{timestamp}.json")
            JSONExporter.export(jobs, filepath)
            exported_files["json"] = filepath
        
        if self.config.export.save_parquet:
            filepath = self.config.get_raw_data_path(f"jobs_{timestamp}.parquet")
            ParquetExporter.export(jobs, filepath)
            exported_files["parquet"] = filepath
        
        if self.config.export.save_csv:
            filepath = self.config.get_raw_data_path(f"jobs_{timestamp}.csv")
            CSVExporter.export(jobs, filepath)
            exported_files["csv"] = filepath
        
        logger.info(f"Exported to formats: {list(exported_files.keys())}")
        return exported_files
