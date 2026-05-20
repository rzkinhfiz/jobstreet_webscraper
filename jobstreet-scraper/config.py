"""
Configuration module for JobStreet scraper.
Manages all settings including search parameters, anti-detection techniques, and data export options.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
import yaml
import os
from pathlib import Path


class SalaryFilterType(str, Enum):
    """Salary filter types"""
    ANY = "Any salary"
    UP_TO_5M = "Up to RM5,000"
    RM5M_TO_10M = "RM5,000 - RM10,000"
    RM10M_TO_15M = "RM10,000 - RM15,000"
    RM15M_TO_20M = "RM15,000 - RM20,000"
    ABOVE_RM20M = "Above RM20,000"


class ExperienceLevel(str, Enum):
    """Experience level filters"""
    ENTRY = "Entry level"
    MID = "Mid level"
    SENIOR = "Senior level"
    EXECUTIVE = "Executive level"


class JobType(str, Enum):
    """Job type filters"""
    FULL_TIME = "Full-time"
    CONTRACT = "Contract"
    PART_TIME = "Part-time"
    TEMPORARY = "Temporary"
    FREELANCE = "Freelance"


@dataclass
class ProxyConfig:
    """Proxy configuration for anti-detection"""
    enabled: bool = False
    proxy_list: List[str] = field(default_factory=list)
    use_residential: bool = False
    proxy_rotation: bool = True
    proxy_timeout: int = 30
    
    @staticmethod
    def from_dict(data: dict) -> "ProxyConfig":
        return ProxyConfig(**data)


@dataclass
class AntiDetectionConfig:
    """Anti-detection techniques configuration"""
    use_stealth: bool = True
    use_playwright_stealth: bool = True
    random_user_agent: bool = True
    random_viewport: bool = True
    disable_images: bool = True  # Faster loading
    disable_css: bool = False
    disable_javascript: bool = False
    
    # Human-like behavior
    enable_random_delays: bool = True
    min_delay: float = 1.0
    max_delay: float = 5.0
    
    enable_random_scrolling: bool = True
    enable_mouse_movements: bool = True
    
    # Connection behavior
    accept_language: str = "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
    timeout: int = 60000  # 60 seconds
    
    @staticmethod
    def from_dict(data: dict) -> "AntiDetectionConfig":
        return AntiDetectionConfig(**data)


@dataclass
class SearchConfig:
    """Search and filter configuration"""
    keywords: List[str] = field(default_factory=lambda: ["Data Scientist", "Backend Engineer", "Frontend Developer"])
    locations: List[str] = field(default_factory=lambda: ["Kuala Lumpur", "Selangor"])
    experience_levels: List[ExperienceLevel] = field(default_factory=list)
    job_types: List[JobType] = field(default_factory=list)
    salary_range: Optional[SalaryFilterType] = None
    
    max_pages_per_keyword: int = 5
    max_results: int = None  # None = unlimited
    
    @staticmethod
    def from_dict(data: dict) -> "SearchConfig":
        if "experience_levels" in data and data["experience_levels"]:
            data["experience_levels"] = [ExperienceLevel(e) for e in data["experience_levels"]]
        if "job_types" in data and data["job_types"]:
            data["job_types"] = [JobType(jt) for jt in data["job_types"]]
        if "salary_range" in data and data["salary_range"]:
            data["salary_range"] = SalaryFilterType(data["salary_range"])
        return SearchConfig(**data)


@dataclass
class DataExportConfig:
    """Data export configuration"""
    save_json: bool = True
    save_parquet: bool = True
    save_csv: bool = False
    
    # Directory paths
    raw_data_dir: str = "data/raw"
    processed_data_dir: str = "data/processed"
    
    # Database (optional)
    use_database: bool = False
    db_type: str = "postgresql"  # postgresql, mysql, sqlite
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "jobstreet_jobs"
    db_user: str = "postgres"
    db_password: str = ""
    
    @staticmethod
    def from_dict(data: dict) -> "DataExportConfig":
        return DataExportConfig(**data)


@dataclass
class ScraperConfig:
    """Main scraper configuration"""
    base_url: str = "https://id.jobstreet.com/"
    
    # Core settings
    headless: bool = True
    browser_type: str = "chromium"  # chromium, firefox, webkit
    max_concurrent_pages: int = 3
    retry_attempts: int = 3
    retry_delay: int = 5
    
    # Subconfigurations
    search: SearchConfig = field(default_factory=SearchConfig)
    anti_detection: AntiDetectionConfig = field(default_factory=AntiDetectionConfig)
    proxy: ProxyConfig = field(default_factory=ProxyConfig)
    export: DataExportConfig = field(default_factory=DataExportConfig)
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/scraper.log"
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> "ScraperConfig":
        """Load configuration from YAML file"""
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        
        # Parse nested configurations
        if "search" in data:
            data["search"] = SearchConfig.from_dict(data["search"])
        if "anti_detection" in data:
            data["anti_detection"] = AntiDetectionConfig.from_dict(data["anti_detection"])
        if "proxy" in data:
            data["proxy"] = ProxyConfig.from_dict(data["proxy"])
        if "export" in data:
            data["export"] = DataExportConfig.from_dict(data["export"])
        
        return cls(**data)
    
    @classmethod
    def from_env(cls) -> "ScraperConfig":
        """Load configuration from environment variables"""
        config = cls()
        
        # Override from environment if set
        if os.getenv("SCRAPER_HEADLESS"):
            config.headless = os.getenv("SCRAPER_HEADLESS").lower() == "true"
        if os.getenv("SCRAPER_LOG_LEVEL"):
            config.log_level = os.getenv("SCRAPER_LOG_LEVEL")
        if os.getenv("SCRAPER_MAX_PAGES"):
            config.search.max_pages_per_keyword = int(os.getenv("SCRAPER_MAX_PAGES"))
        
        return config
    
    def get_raw_data_path(self, filename: str) -> str:
        """Get raw data file path"""
        Path(self.export.raw_data_dir).mkdir(parents=True, exist_ok=True)
        return os.path.join(self.export.raw_data_dir, filename)
    
    def get_processed_data_path(self, filename: str) -> str:
        """Get processed data file path"""
        Path(self.export.processed_data_dir).mkdir(parents=True, exist_ok=True)
        return os.path.join(self.export.processed_data_dir, filename)


# Default configuration instance
DEFAULT_CONFIG = ScraperConfig()
