# Quick Start Guide - JobStreet Scraper 🚀

Complete step-by-step guide to get the scraper running in 5 minutes.

## ⚡ 5-Minute Setup

### Step 1: Prerequisites Check (1 minute)

Ensure you have:
- Python 3.11+ installed
- Git installed
- 2GB free disk space

```bash
# Check Python version
python --version  # Should be 3.11+
```

### Step 2: Setup Project (2 minutes)

```bash
# Navigate to project directory
cd jobstreet-scraper

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (this takes ~2 min)
python -m playwright install chromium
```

### Step 3: Test Salary Parser (1 minute)

Verify installation is working:
```bash
python test_salary_parser.py
```

Expected output:
```
================================================================================
SALARY PARSER TEST RESULTS
================================================================================

Input: RM 3,000 - RM 8,000 per month
  └─ Min: 3000.0
  ├─ Max: 8000.0
  ├─ Avg: 5500.0
  ├─ Type: monthly
  ├─ Currency: MYR
  └─ Negotiable: False
```

### Step 4: Run Scraper (1 minute)

```bash
# Basic run with default config
python main.py

# Custom keywords
python main.py --keyword "Data Scientist" "Backend Engineer" --max-pages 3

# Specific locations
python main.py --keyword "DevOps Engineer" --location "Kuala Lumpur" "Penang"

# With proxy
python main.py --proxy "http://proxy1:8080" --max-pages 2
```

## 📊 What You'll Get

After running the scraper, you'll have:

```
data/
└── raw/
    ├── jobs_20260519_100000.json      # Human-readable format
    └── jobs_20260519_100000.parquet   # Analytics-optimized format
logs/
└── scraper.log                         # Full execution log
```

Each job record includes:
- Job title, company, location
- Salary (min, max, average, type, currency)
- Experience level, job type
- Description and requirements
- Job URL and ID
- Scraped timestamp

## 🎯 Common Usage Patterns

### Pattern 1: Quick Search (3 pages)
```bash
python main.py --keyword "Data Scientist" --max-pages 3
```

### Pattern 2: Location-Based (All pages available)
```bash
python main.py --keyword "Backend Engineer" --location "Kuala Lumpur" "Selangor"
```

### Pattern 3: Multiple Keywords with Limited Pages
```bash
python main.py \
  --keyword "Data Scientist" "Machine Learning Engineer" "Backend Engineer" \
  --location "Kuala Lumpur" \
  --max-pages 5
```

### Pattern 4: Using Config File
```bash
# 1. Edit config.yaml with your preferences
# 2. Run:
python main.py --config config.yaml
```

### Pattern 5: Docker Execution
```bash
# Build image
docker build -t jobstreet-scraper .

# Run container
docker run -v $(pwd)/data:/app/data jobstreet-scraper

# Or with docker-compose
docker-compose up scraper
```

## 🔧 Configuration Guide

### Edit config.yaml for:

**Keywords to search:**
```yaml
search:
  keywords:
    - "Data Scientist"
    - "Backend Engineer"
```

**Locations:**
```yaml
search:
  locations:
    - "Kuala Lumpur"
    - "Selangor"
```

**Number of pages per keyword:**
```yaml
search:
  max_pages_per_keyword: 5  # Increase for more results
```

**Anti-detection settings:**
```yaml
anti_detection:
  enable_random_delays: true
  min_delay: 1.0      # Minimum seconds between actions
  max_delay: 5.0      # Maximum seconds between actions
```

**Enable headless mode (recommended for servers):**
```yaml
headless: true   # Set to false to see browser
```

## 📈 Performance Tuning

### For Faster Scraping:
```yaml
anti_detection:
  disable_images: true    # Don't download images
  min_delay: 0.5          # Reduce delays
  max_delay: 2.0

search:
  max_pages_per_keyword: 3
```

### For Anti-Detection (Slower but safer):
```yaml
anti_detection:
  disable_images: false   # Load images
  min_delay: 2.0          # More random behavior
  max_delay: 8.0

search:
  max_pages_per_keyword: 5
```

### With Proxy (Recommended for large-scale):
```yaml
proxy:
  enabled: true
  proxy_list:
    - "http://proxy1:8080"
    - "http://proxy2:8080"
  proxy_rotation: true
```

## 📊 Output Examples

### View Scraped Data (JSON)

```bash
# Pretty print JSON with salary info
python -c "
import json
with open('data/raw/jobs_20260519_100000.json') as f:
    jobs = json.load(f)
    for job in jobs[:3]:
        print(f\"{job['job_title']} @ {job['company_name']}\")
        print(f\"  Salary: RM {job['salary']['min']} - RM {job['salary']['max']}\")
        print()
"
```

### Query with Pandas (Parquet)

```python
import pandas as pd

# Read parquet file
df = pd.read_parquet('data/raw/jobs_20260519_100000.parquet')

# Show first 5 jobs
print(df.head())

# Average salary by company
print(df.groupby('company_name')['salary_average'].mean())

# Jobs with salary above certain amount
high_paying = df[df['salary_min'] > 10000]
print(f"High-paying jobs: {len(high_paying)}")
```

## 🐛 Troubleshooting

### Error: "Browser executable not found"
```bash
# Solution: Install Playwright browsers
python -m playwright install chromium
```

### Error: "TimeoutError: Timeout waiting for job listings"
```
Solution:
1. Increase timeout in config.yaml:
   anti_detection:
     timeout: 120000  # 120 seconds

2. Try with proxy:
   python main.py --proxy "http://proxy:8080"

3. Check internet connection
```

### Error: "No jobs found" or empty results
```
Solution:
1. Check if keywords are specific enough
2. Verify location names are correct
3. Try with one keyword first
4. Check JobStreet website directly

Example:
python main.py --keyword "Python Developer" --location "Kuala Lumpur"
```

### Browser showing (not headless)
Make sure `headless: true` in config.yaml or run:
```bash
python main.py  # Uses headless by default
```

## 📋 Data Quality Checks

### Verify salary parsing worked:
```bash
python -c "
import json
with open('data/raw/jobs_20260519_100000.json') as f:
    jobs = json.load(f)
    with_salary = sum(1 for j in jobs if j['salary']['min'])
    negotiable = sum(1 for j in jobs if j['salary']['negotiable'])
    print(f'Total jobs: {len(jobs)}')
    print(f'With parsed salary: {with_salary}')
    print(f'Negotiable: {negotiable}')
"
```

### Check for duplicates:
```bash
python -c "
import json
with open('data/raw/jobs_20260519_100000.json') as f:
    jobs = json.load(f)
    urls = [j['job_url'] for j in jobs]
    duplicates = len(urls) - len(set(urls))
    print(f'Total: {len(urls)}, Unique: {len(set(urls))}, Duplicates: {duplicates}')
"
```

## 📚 Next Steps

1. **Custom salary parsing**: Edit `scraper/salary_parser.py` if JobStreet changes format
2. **Database export**: Enable PostgreSQL in config for large-scale scraping
3. **Schedule scraping**: Use cron (Linux) or Task Scheduler (Windows)
4. **API integration**: Export to your own API endpoint

## 🔗 Useful Commands Reference

```bash
# View logs in real-time
tail -f logs/scraper.log

# Run with debug logging
python main.py --log-level DEBUG  # TODO: Add this feature if needed

# Export data to different format
python -c "
from pipelines import CSVExporter, JSONExporter
import json
with open('data/raw/jobs_20260519_100000.json') as f:
    jobs_data = json.load(f)
# Convert to JobListing objects and export
"

# Count jobs per company
python -c "
import json
from collections import Counter
with open('data/raw/jobs_20260519_100000.json') as f:
    jobs = json.load(f)
    companies = Counter([j['company_name'] for j in jobs])
    for company, count in companies.most_common(10):
        print(f'{company}: {count} jobs')
"

# Find highest paying jobs
python -c "
import json
with open('data/raw/jobs_20260519_100000.json') as f:
    jobs = json.load(f)
    sorted_jobs = sorted(jobs, key=lambda x: x['salary']['max'] or 0, reverse=True)
    for job in sorted_jobs[:10]:
        print(f\"{job['job_title']} @ {job['company_name']}\")
        print(f\"  Max: RM {job['salary']['max']}\")
"
```

## ✅ Success Criteria

You've successfully set up the scraper when:

- [x] `python test_salary_parser.py` runs without errors
- [x] `python main.py` completes and creates `data/raw/` files
- [x] JSON file contains valid job data
- [x] Salary data is properly parsed
- [x] Log file shows no critical errors

## 🆘 Need Help?

1. **Check logs**: `tail -f logs/scraper.log`
2. **Review config**: Compare your `config.yaml` with defaults
3. **Test salary parser**: `python test_salary_parser.py`
4. **Enable debug**: Set `log_level: DEBUG` in config.yaml
5. **Check README**: See README.md for detailed documentation

## 📞 Tips & Tricks

- **Slow internet?** Set `disable_images: true` in config
- **Getting blocked?** Increase delays or use proxy
- **Want specific jobs?** Use multiple focused keywords instead of generic ones
- **Large-scale scraping?** Use Docker + multiple instances + proxy rotation
- **Data analysis?** Use Parquet format with pandas

---

**Happy Scraping! 🎯**

For full documentation, see [README.md](README.md)
