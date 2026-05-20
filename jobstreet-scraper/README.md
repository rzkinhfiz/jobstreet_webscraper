# JobStreet Indonesia Job Scraper 🎯

A production-ready web scraper for extracting job listings from **https://id.jobstreet.com/** using Playwright with advanced anti-detection techniques and robust salary parsing.

## 🌟 Features

- **Anti-Detection (2026 Best Practices)**
  - Stealth.js injection with webdriver detection bypass
  - Random user agents and viewports
  - Human-like behavior: random delays, scrolling, mouse movements
  - Residential proxy support with automatic rotation
  - Header spoofing and browser fingerprint randomization

- **Smart Salary Parsing**
  - Handles multiple salary formats: "RM 3,000 - RM 8,000", "5K-10K", negotiable, etc.
  - Automatic currency detection (MYR, SGD, USD, IDR)
  - Salary type inference (monthly, yearly, hourly)
  - Robust number parsing with error handling

- **Flexible Search & Filtering**
  - Multiple keyword support
  - Location-based filtering
  - Experience level filters
  - Job type filters
  - Salary range filtering

- **Dynamic Content Handling**
  - Pagination support
  - Infinite scroll handling
  - JavaScript-rendered content support
  - Network idle detection

- **Multiple Export Formats**
  - JSON (human-readable with nested structure)
  - Parquet (columnar storage for analytics)
  - CSV (for spreadsheets)
  - Database support (optional PostgreSQL)

- **Comprehensive Data Extraction**
  - Job title, company name, location
  - Salary (min, max, average, currency, type)
  - Experience level, job type, employment details
  - Job description and requirements
  - Skills extraction
  - Posting/expiration dates
  - Job URLs and IDs

## 📋 Requirements

- Python 3.11+
- Playwright browser automation
- pandas & pyarrow (for Parquet export)
- loguru (for advanced logging)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to project directory
cd jobstreet-scraper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Run Scraper

**Basic usage (with default keywords):**
```bash
python main.py
```

**Custom keywords and locations:**
```bash
python main.py --keyword "Data Scientist" "Backend Engineer" --location "Kuala Lumpur" "Selangor" --max-pages 5
```

**Using config file:**
```bash
python main.py --config config.yaml
```

**With proxy:**
```bash
python main.py --proxy "http://proxy1:8080" "http://proxy2:8080"
```

**Export existing data:**
```bash
python main.py --export-only data/raw/jobs_20260519_100000.json
```

### 3. Configuration

Edit `config.yaml` to customize:

```yaml
search:
  keywords:
    - "Data Scientist"
    - "Backend Engineer"
  locations:
    - "Kuala Lumpur"
  max_pages_per_keyword: 5

anti_detection:
  enable_random_delays: true
  min_delay: 1.0
  max_delay: 5.0

export:
  save_json: true
  save_parquet: true
```

## 🛡️ Anti-Detection Techniques

### 1. **Browser Fingerprint Spoofing**
- Random user agents from real Chrome, Firefox, Safari versions
- Random viewport sizes (1920x1080, 1366x768, etc.)
- Fake browser capabilities (plugins, languages)
- WebGL rendering spoofing

### 2. **WebDriver Detection Bypass**
- Removes `navigator.webdriver` property
- Injects custom `window.chrome` object
- Masks automation indicators
- Fixes `navigator.permissions` API

### 3. **Human-Like Behavior**
- Random delays between actions (1-5 seconds)
- Random scrolling with variable distances
- Mouse movement simulation
- Typing simulation with character delays
- Random page interactions

### 4. **Network Behavior**
- Custom HTTP headers matching real browsers
- DNT (Do Not Track) headers
- Realistic Accept-Language headers
- Proper Sec-* fetch headers

### 5. **Proxy Support**
- Residential proxy rotation
- Sequential and random proxy selection
- Proxy timeout handling
- Failed proxy skipping

## 📊 Salary Parsing Examples

The parser handles various JobStreet salary formats:

```python
from scraper.salary_parser import parse_salary

# Various input formats
formats = [
    "RM 3,000 - RM 8,000 per month",
    "RM 5000/month",
    "Negotiable",
    "Up to RM 15,000",
    "RM 50,000 - RM 100,000 per year",
    "RM5K - RM10K",
    "RM 100K - RM 150K per annum",
    "$3,000 - $8,000",
]

for salary_text in formats:
    result = parse_salary(salary_text)
    print(f"Input: {salary_text}")
    print(f"Min: {result.salary_min}, Max: {result.salary_max}")
    print(f"Type: {result.salary_type}, Currency: {result.currency}")
    print(f"Average: {result.salary_average}")
    print()
```

## 📁 Project Structure

```
jobstreet-scraper/
├── main.py                 # Entry point
├── config.py              # Configuration management
├── config.yaml            # Configuration file
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container image
├── README.md             # This file
├── scraper/
│   ├── __init__.py       # Main scraper class (JobStreetScraper, JobListing)
│   ├── salary_parser.py  # Robust salary parsing
│   └── stealth.py        # Anti-detection techniques
├── utils/
│   └── __init__.py       # Logging and utilities
├── pipelines/
│   └── __init__.py       # Data processing (dedup, export)
└── data/
    ├── raw/              # Raw scraped data (JSON, Parquet)
    └── processed/        # Processed data
```

## 🎯 Best Practices for JobStreet

### Rate Limiting
- Default: 30 requests per minute
- Use random delays between requests
- Don't scrape the same keyword repeatedly in short time

### Detection Avoidance
- Always use headless mode with stealth enabled
- Rotate user agents and viewports
- Enable image loading (looks more human than disabling)
- Use residential proxies for large-scale scraping
- Vary your scraping patterns

### Handling Dynamic Content
- Wait for network idle state
- Scroll smoothly with random distances
- Handle infinite scroll gracefully
- Implement retry logic with exponential backoff

### Data Quality
- Deduplicate by job URL
- Validate salary parsing with regex patterns
- Clean up text data (trim whitespace)
- Store raw data before processing

## 💾 Data Export

### JSON Format
Clean, nested structure perfect for APIs:
```json
{
  "job_title": "Data Scientist",
  "salary": {
    "min": 3000,
    "max": 8000,
    "average": 5500,
    "currency": "MYR",
    "type": "monthly"
  }
}
```

### Parquet Format
Columnar storage for efficient analytics:
- Smaller file size than JSON
- Better for pandas/SQL analysis
- Compression support
- Schema validation

### CSV Format
Standard spreadsheet format:
- Skills stored as pipe-separated values
- Compatible with Excel, Google Sheets
- Easy data transfer

## 🐳 Docker Usage

### Build image:
```bash
docker build -t jobstreet-scraper .
```

### Run container:
```bash
docker run -v $(pwd)/data:/app/data jobstreet-scraper
```

### With custom config:
```bash
docker run -v $(pwd)/data:/app/data -v $(pwd)/config.yaml:/app/config.yaml \
  jobstreet-scraper python main.py --config config.yaml
```

## 🔧 Advanced Configuration

### Enable Database Export (PostgreSQL)
```yaml
export:
  use_database: true
  db_type: postgresql
  db_host: localhost
  db_port: 5432
  db_name: jobstreet_jobs
  db_user: postgres
  db_password: "your_password"
```

### Use Residential Proxies
```yaml
proxy:
  enabled: true
  proxy_list:
    - "http://proxy-api.example.com?session=1"
    - "http://proxy-api.example.com?session=2"
  use_residential: true
  proxy_rotation: true
```

### Disable Images for Faster Scraping
```yaml
anti_detection:
  disable_images: true  # Faster but may miss content
  disable_css: false    # Keep CSS for layout
```

## 📊 Output Example

```
jobstreet-scraper main.py
================================================================================
JobStreet Scraper Started
================================================================================
Keywords: ['Data Scientist', 'Backend Engineer']
Locations: ['Kuala Lumpur', 'Selangor']
Max pages per keyword: 3
Headless mode: True
Stealth mode: True

Searching for: Data Scientist in Kuala Lumpur
Scraping page 1 for keyword: Data Scientist
Found 10 jobs on page 1
...

================================================================================
Scraping Summary
================================================================================
Total jobs scraped: 45
Jobs after processing: 42
Salary range (min): RM 2,500 - RM 50,000
Salary range (max): RM 5,000 - RM 120,000
Negotiable salaries: 5
Exported files: {'json': 'data/raw/jobs_20260519_100000.json', 'parquet': 'data/raw/jobs_20260519_100000.parquet'}
================================================================================
Scraping complete!
```

## 🚨 Troubleshooting

### Browser Launch Error
```bash
playwright install chromium
# or
python -m playwright install
```

### Timeout Errors
- Increase `timeout` in config (default 60000ms)
- Check internet connection
- Try with proxy if ISP blocks traffic

### No Salary Parsed
- Check JobStreet HTML structure (they update frequently)
- Update salary parser regex patterns
- Enable logging to debug

### Getting Blocked
- Add random delays: increase `min_delay` and `max_delay`
- Use residential proxies
- Reduce `max_concurrent_pages`
- Scrape different keywords/times

## 📝 Logging

Logs are stored in `logs/scraper.log`:
```
2026-05-19 10:30:45 | INFO     | main:main:45 - JobStreet Scraper Started
2026-05-19 10:30:46 | INFO     | scraper:initialize:78 - Initializing Playwright browser...
2026-05-19 10:31:02 | INFO     | scraper:search_jobs:156 - Searching for: Data Scientist in Kuala Lumpur
```

Change log level in `config.yaml`:
```yaml
log_level: DEBUG  # DEBUG, INFO, WARNING, ERROR
```

## 🔐 Ethical Scraping

- **Respect robots.txt** (JobStreet may block scrapers)
- **Rate limiting**: Don't overwhelm servers
- **Check ToS**: Review JobStreet terms of service
- **Use responsibly**: For research/analysis, not competing services
- **User-Agent honesty**: Identify your scraper appropriately
- **Data privacy**: Don't store or share personal information

## 🤝 Contributing

Improvements welcome! Areas for enhancement:
- Database export pipeline
- Async concurrent scraping optimization
- Additional salary format patterns
- Company profile scraping
- Review/rating extraction

## 📄 License

MIT License - Use freely in your projects

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Users are responsible for:
- Complying with JobStreet's Terms of Service
- Adhering to local laws and regulations
- Respecting server resources
- Proper attribution if data is shared

## 📞 Support

For issues, questions, or improvements:
1. Check logs: `tail -f logs/scraper.log`
2. Review config: Validate `config.yaml`
3. Test salary parser: Run salary parser unit tests
4. Enable debug logging: Set `log_level: DEBUG`

---

**Last Updated**: May 2026
**Version**: 1.0.0
**Status**: Production-Ready ✅
