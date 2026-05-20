# Project Structure & File Guide

Complete overview of the JobStreet Scraper project structure and all files included.

## 📁 Directory Structure

```
jobstreet-scraper/
│
├── Core Files
│   ├── main.py                      # Entry point - run this to start scraping
│   ├── config.py                    # Configuration management & dataclasses
│   └── config.yaml                  # Configuration file (edit this to customize)
│
├── scraper/                         # Core scraping logic
│   ├── __init__.py                  # Main scraper class & JobListing dataclass
│   ├── salary_parser.py             # Robust salary parsing (~500+ lines)
│   └── stealth.py                   # Anti-detection techniques
│
├── utils/                           # Utility functions
│   └── __init__.py                  # Logging setup
│
├── pipelines/                       # Data processing
│   └── __init__.py                  # Data export (JSON, Parquet, CSV)
│
├── data/                            # Data storage
│   ├── raw/                         # Raw scraped data
│   └── processed/                   # Processed data
│
├── logs/                            # Logs directory (auto-created)
│   └── scraper.log
│
├── Documentation
│   ├── README.md                    # Full documentation
│   ├── QUICK_START.md               # 5-minute setup guide
│   ├── BEST_PRACTICES.md            # Anti-ban & detection techniques
│   ├── PAGINATION_GUIDE.md          # Pagination & infinite scroll
│   ├── PROJECT_STRUCTURE.md         # This file
│   └── .env.example                 # Environment variables template
│
├── Configuration & Build
│   ├── requirements.txt             # Python dependencies
│   ├── requirements-dev.txt         # Dev dependencies (testing, linting)
│   ├── Dockerfile                   # Docker image definition
│   ├── docker-compose.yaml          # Docker Compose setup
│   ├── .gitignore                   # Git ignore patterns
│   ├── Makefile                     # Common commands
│   └── test_salary_parser.py        # Salary parser tests
│
└── Version Control
    └── .git/                        # Git repository
```

## 📄 File Descriptions

### Entry Point

**`main.py`** (320 lines)
- Main execution entry point
- Handles command-line arguments
- Orchestrates scraping, processing, and export
- Features:
  - Config loading (YAML or CLI args)
  - Multi-keyword scraping
  - Export to multiple formats
  - Summary statistics
- Usage: `python main.py --keyword "Data Scientist" --max-pages 5`

### Configuration

**`config.py`** (250+ lines)
- Complete configuration management
- Dataclasses for type safety
- Nested config objects:
  - `ScraperConfig`: Main configuration
  - `SearchConfig`: Search parameters
  - `AntiDetectionConfig`: Stealth settings
  - `ProxyConfig`: Proxy configuration
  - `DataExportConfig`: Export settings
- Features:
  - YAML loading
  - Environment variable override
  - Path helpers
  - Enums for common values

**`config.yaml`** (80+ lines)
- Sample configuration file
- All settings documented with comments
- Ready-to-edit template
- Covers all features (search, anti-detection, proxy, export)

### Core Scraper

**`scraper/__init__.py`** (400+ lines)
- `JobStreetScraper`: Main scraper class
- `JobListing`: Job data model (dataclass)
- Features:
  - Async page management
  - Stealth browser initialization
  - Job extraction from listings
  - Pagination handling
  - Proxy rotation
  - Rate limiting
- Key methods:
  - `initialize()`: Setup browser
  - `search_jobs()`: Main scraping method
  - `_extract_jobs_from_page()`: Extract jobs
  - `_extract_job_details()`: Get job details
  - `_navigate_to_next_page()`: Handle pagination

**`scraper/salary_parser.py`** (520+ lines)
- Comprehensive salary parsing engine
- `SalaryParser`: Main parsing class
- `ParsedSalary`: Salary data model
- Handles 15+ different salary formats:
  - "RM 3,000 - RM 8,000 per month"
  - "RM5K - RM10K"
  - "Negotiable"
  - "Up to RM 15,000"
  - And many more...
- Features:
  - Currency detection
  - Salary type inference (monthly, yearly, hourly)
  - Average calculation
  - Normalization to monthly rate
  - Dict conversion
- Test file: `test_salary_parser.py`

**`scraper/stealth.py`** (450+ lines)
- Anti-detection & stealth techniques
- `StealthBrowser`: Main stealth class
- `ProxyRotator`: Proxy management
- `RateLimiter`: Request rate limiting
- Features:
  - WebDriver detection bypass
  - JavaScript injection (stealth.js)
  - Browser fingerprint spoofing
  - Human-like behavior:
    - Random delays
    - Mouse movements
    - Scrolling simulation
    - Typing simulation
  - Header spoofing
  - Viewport randomization
  - 15+ realistic user agents

### Utilities

**`utils/__init__.py`** (30+ lines)
- `get_logger()`: Configured logger instance
- `ensure_directory()`: Directory creation helper
- Features:
  - File + console logging
  - Log rotation
  - Color-coded output
  - Timestamps

### Data Pipelines

**`pipelines/__init__.py`** (350+ lines)
- `DataPipeline`: Main pipeline orchestrator
- `JSONExporter`: JSON export
- `ParquetExporter`: Parquet (columnar) export
- `CSVExporter`: CSV export
- `ExportManager`: Export orchestration
- Features:
  - Deduplication
  - Salary filtering
  - Multiple format support
  - Automatic directory creation

### Testing

**`test_salary_parser.py`** (150+ lines)
- Comprehensive salary parser tests
- Functions:
  - `test_salary_parsing()`: 20+ test cases
  - `test_salary_normalization()`: Type normalization
  - `test_salary_dict_conversion()`: Output format
- Run: `python test_salary_parser.py`

### Documentation

**`README.md`** (550+ lines)
- Complete user documentation
- Features overview
- Installation guide
- Usage examples
- Configuration reference
- Anti-detection overview
- Output examples
- Troubleshooting guide
- Docker instructions

**`QUICK_START.md`** (400+ lines)
- 5-minute setup guide
- Step-by-step instructions
- Common usage patterns
- Configuration tips
- Data access examples
- Troubleshooting quick fixes
- Useful commands

**`BEST_PRACTICES.md`** (550+ lines)
- Advanced anti-detection techniques
- JobStreet-specific defense mechanisms
- Rate limiting strategies
- Proxy rotation patterns
- Detection signs & recovery
- Monitoring & alerting
- Scaling strategies
- Ethical scraping guidelines

**`PAGINATION_GUIDE.md`** (400+ lines)
- Complete pagination handling guide
- Pagination methods (URL, infinite scroll, load more)
- Implementation details
- Detection algorithms
- Performance metrics
- Troubleshooting common issues
- Advanced techniques

### Build & Deployment

**`requirements.txt`** (12 packages)
```
playwright >= 1.45.0      # Browser automation
playwright-stealth        # Stealth plugin
pydantic >= 2.0.0        # Data validation
aiohttp >= 3.9.0         # Async HTTP
tenacity >= 8.3.0        # Retry logic
pandas >= 2.0.0          # Data analysis
pyarrow >= 14.0.0        # Parquet support
pyyaml >= 6.0.0          # YAML parsing
python-dotenv            # Env variables
loguru >= 0.7.0          # Advanced logging
httpx >= 0.25.0          # HTTP client
```

**`requirements-dev.txt`** (12+ packages)
- Development dependencies
- Testing tools (pytest)
- Code quality (black, flake8, mypy)
- Documentation (sphinx)

**`Dockerfile`** (30+ lines)
- Multi-stage Docker build
- Base: Python 3.11 slim
- Playwright browsers pre-installed
- Optimized for production

**`docker-compose.yaml`** (30+ lines)
- Service: scraper
- Optional: PostgreSQL database
- Volume mounts for data persistence
- Environment configuration

**`Makefile`** (60+ lines)
- Common development commands
- `make help`: Show available commands
- `make install`: Install dependencies
- `make run`: Run scraper
- `make test`: Test salary parser
- `make docker-build`: Build Docker image
- `make format`: Format code
- `make clean`: Clean cache

**`.gitignore`** (35 lines)
- Python cache files
- Virtual environment
- IDE configurations
- Data files
- Logs
- OS files

**`.env.example`** (35+ lines)
- Environment variable template
- Copy to `.env` and customize
- Includes all major settings

## 🔗 Module Relationships

```
main.py (entry point)
    ↓
config.py (load configuration)
    ↓
scraper/__init__.py (JobStreetScraper)
    ├→ scraper/stealth.py (StealthBrowser, ProxyRotator, RateLimiter)
    ├→ scraper/salary_parser.py (SalaryParser - extract salary)
    ├→ utils/__init__.py (logging)
    └→ pipelines/__init__.py (data processing)
        ├→ JSONExporter
        ├→ ParquetExporter
        └→ CSVExporter
```

## 📊 Code Statistics

| Component | Lines | Purpose |
|-----------|-------|---------|
| main.py | 320 | Entry point & orchestration |
| config.py | 280 | Configuration management |
| scraper/__init__.py | 420 | Core scraping logic |
| scraper/salary_parser.py | 520 | Salary parsing |
| scraper/stealth.py | 450 | Anti-detection |
| utils/__init__.py | 35 | Utilities |
| pipelines/__init__.py | 350 | Data export |
| Documentation | 1900+ | README, guides, etc. |
| **Total** | **4275+** | **Production-ready** |

## 🚀 Feature Breakdown

### Scraping Features
- ✅ Multi-keyword search
- ✅ Location filtering
- ✅ Pagination handling
- ✅ Infinite scroll support
- ✅ Dynamic content (JavaScript)
- ✅ Job detail extraction

### Anti-Detection Features
- ✅ WebDriver detection bypass
- ✅ Browser fingerprint spoofing
- ✅ User agent randomization
- ✅ Viewport randomization
- ✅ Human-like delays
- ✅ Mouse movement simulation
- ✅ Scrolling simulation
- ✅ Header spoofing
- ✅ Proxy rotation
- ✅ Rate limiting

### Data Extraction
- ✅ Job title, company, location
- ✅ Salary (min, max, average)
- ✅ Salary type (monthly, yearly, hourly)
- ✅ Salary currency detection
- ✅ Negotiable salary detection
- ✅ Experience level
- ✅ Job type
- ✅ Job description
- ✅ Requirements & skills
- ✅ Dates
- ✅ Company industry

### Export Formats
- ✅ JSON (nested, readable)
- ✅ Parquet (columnar, analytics)
- ✅ CSV (spreadsheet compatible)
- ✅ Database (optional PostgreSQL)

### Configuration
- ✅ YAML config file
- ✅ Command-line arguments
- ✅ Environment variables
- ✅ Type-safe dataclasses
- ✅ Sensible defaults

## 🔄 Data Flow

```
Configuration (config.yaml)
    ↓
Search Keywords
    ↓
JobStreetScraper.search_jobs()
    ├→ Navigate to search URL
    ├→ Inject stealth JavaScript
    ├→ Extract job listings
    ├→ Handle pagination
    └→ Extract job details
    ↓
SalaryParser.parse() (for each job)
    ├→ Detect currency
    ├→ Extract salary values
    ├→ Detect salary type
    └→ Calculate average
    ↓
JobListing objects created
    ↓
DataPipeline processing
    ├→ Deduplicate
    └→ Filter
    ↓
ExportManager.export_all()
    ├→ JSONExporter → jobs_TIMESTAMP.json
    ├→ ParquetExporter → jobs_TIMESTAMP.parquet
    └→ CSVExporter → jobs_TIMESTAMP.csv
    ↓
data/raw/ directory
```

## 🎯 Usage Scenarios

### Quick Test
```bash
python test_salary_parser.py
python main.py --keyword "Data Scientist" --max-pages 2
```

### Production Scraping
```bash
python main.py --config config.yaml
# Or with custom settings:
python main.py \
  --keyword "Data Scientist" "Backend Engineer" \
  --location "Kuala Lumpur" "Selangor" \
  --max-pages 10 \
  --proxy "http://proxy1:8080" "http://proxy2:8080"
```

### Docker
```bash
docker build -t jobstreet-scraper .
docker run -v $(pwd)/data:/app/data jobstreet-scraper
```

### Development
```bash
make install-dev  # Install with dev dependencies
make format       # Format code
make lint         # Check code quality
make test         # Run tests
```

---

**This is a production-ready, well-structured, and thoroughly documented web scraping project.** ✅
