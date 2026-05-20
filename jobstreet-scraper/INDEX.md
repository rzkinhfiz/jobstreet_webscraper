# 📚 Complete Documentation Index

## 🎯 Getting Started

### For First-Time Users
1. **[QUICK_START.md](QUICK_START.md)** ⭐ START HERE
   - 5-minute setup and first run
   - Basic usage examples
   - Troubleshooting quick fixes

2. **[INSTALLATION.md](INSTALLATION.md)**
   - Detailed installation steps
   - Multiple installation methods (pip, Docker, Make)
   - Troubleshooting installation issues
   - OS-specific instructions

3. **[README.md](README.md)**
   - Complete feature overview
   - Full documentation
   - API reference
   - Output examples

## 🔧 Technical Guides

### Core Functionality
- **[Main Entry Point](main.py)** - How to run the scraper
- **[Configuration Guide](config.py)** - Understand config system
- **[config.yaml](config.yaml)** - Configuration file template

### Components
- **[Salary Parser](scraper/salary_parser.py)** - 20+ salary formats supported
- **[Stealth Module](scraper/stealth.py)** - Anti-detection techniques
- **[Main Scraper](scraper/__init__.py)** - Core scraping logic
- **[Data Pipelines](pipelines/__init__.py)** - Export and processing

## 📖 Advanced Topics

### 1. Anti-Detection & Best Practices
**Read: [BEST_PRACTICES.md](BEST_PRACTICES.md)**
- WebDriver detection bypass techniques
- Browser fingerprinting evasion
- Human-like behavior simulation
- Rate limiting strategies
- Proxy rotation patterns
- If you get blocked and recovery steps
- JobStreet-specific tips

### 2. Pagination & Infinite Scroll
**Read: [PAGINATION_GUIDE.md](PAGINATION_GUIDE.md)**
- Different pagination methods on JobStreet
- URL-based pagination handling
- Infinite scroll detection and handling
- Load more button handling
- Performance optimization
- Troubleshooting pagination issues

### 3. Project Structure
**Read: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)**
- File-by-file breakdown
- Code organization
- Module relationships
- Code statistics
- Data flow diagrams

## 🚀 Quick Reference

### Common Commands

```bash
# Setup
pip install -r requirements.txt
python -m playwright install chromium

# Run scraper
python main.py                                          # Default
python main.py --keyword "Data Scientist" --max-pages 5  # Custom
python main.py --config config.yaml                    # With config
python main.py --proxy "http://proxy:8080" --keyword "DevOps"  # With proxy

# Testing
python test_salary_parser.py                           # Test salary parser

# Using Make
make help                                              # Show all commands
make install                                           # Install deps
make run                                               # Run scraper
make test                                              # Run tests
make format                                            # Format code
make docker-build                                      # Build Docker image

# Using Docker
docker build -t jobstreet-scraper .                   # Build
docker run -v $(pwd)/data:/app/data jobstreet-scraper  # Run
docker-compose up scraper                             # With docker-compose

# Logs
tail -f logs/scraper.log                              # Real-time logs
```

### Configuration Reference

```yaml
# Basic search
search:
  keywords: ["Data Scientist", "Backend Engineer"]
  locations: ["Kuala Lumpur"]
  max_pages_per_keyword: 5

# Anti-detection
anti_detection:
  enable_random_delays: true
  min_delay: 1.0
  max_delay: 5.0
  use_stealth: true

# Export
export:
  save_json: true
  save_parquet: true
  save_csv: false

# Proxy (optional)
proxy:
  enabled: true
  proxy_list: ["http://proxy1:8080", "http://proxy2:8080"]
```

## 📁 File Structure

```
jobstreet-scraper/
├── DOCUMENTATION (Read in this order)
│   ├── QUICK_START.md          👈 Start here!
│   ├── INSTALLATION.md
│   ├── README.md
│   ├── BEST_PRACTICES.md       (For anti-detection)
│   ├── PAGINATION_GUIDE.md     (For pagination)
│   ├── PROJECT_STRUCTURE.md    (For architecture)
│   └── INDEX.md                (This file)
│
├── CORE APPLICATION
│   ├── main.py                 (Entry point - python main.py)
│   ├── config.py               (Configuration system)
│   ├── config.yaml             (Configuration file - edit this)
│   ├── scraper/
│   │   ├── __init__.py         (JobStreetScraper class)
│   │   ├── salary_parser.py    (Salary parsing engine)
│   │   └── stealth.py          (Anti-detection)
│   ├── pipelines/__init__.py   (Data export)
│   └── utils/__init__.py       (Utilities & logging)
│
├── CONFIGURATION & BUILD
│   ├── requirements.txt        (Python dependencies)
│   ├── requirements-dev.txt    (Dev dependencies)
│   ├── Dockerfile              (Docker build)
│   ├── docker-compose.yaml     (Docker Compose)
│   ├── .gitignore              (Git ignore)
│   ├── Makefile                (Common commands)
│   └── .env.example            (Environment template)
│
├── DATA STORAGE
│   ├── data/raw/               (Raw scraped data)
│   ├── data/processed/         (Processed data)
│   └── logs/                   (Application logs)
│
└── TESTING
    ├── test_salary_parser.py   (Salary parser tests)
    └── [add more tests as needed]
```

## 🎓 Learning Path

### Beginner (Just want to scrape)
1. Read: [QUICK_START.md](QUICK_START.md) - 10 min
2. Do: `pip install -r requirements.txt`
3. Do: `python -m playwright install chromium`
4. Do: `python main.py`
5. Find data in: `data/raw/`

### Intermediate (Understand the project)
1. Read: [README.md](README.md) - 20 min
2. Read: [config.yaml](config.yaml) - 10 min
3. Read: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 15 min
4. Try: Different configuration options
5. Monitor: `tail -f logs/scraper.log` during runs

### Advanced (Customize & deploy)
1. Read: [BEST_PRACTICES.md](BEST_PRACTICES.md) - 30 min
2. Read: [PAGINATION_GUIDE.md](PAGINATION_GUIDE.md) - 25 min
3. Study: Source code (start with [main.py](main.py))
4. Extend: Add new features to scraper
5. Deploy: Using Docker or scheduled tasks

### Expert (Production deployment)
1. Master all documentation
2. Implement custom middleware
3. Setup database export
4. Configure proxy rotation
5. Deploy to cloud (AWS, GCP, etc.)

## 🆘 Troubleshooting Guide

### Installation Issues
→ See [INSTALLATION.md](INSTALLATION.md) - Troubleshooting section

### Scraping Issues
→ See [README.md](README.md) - Troubleshooting section
→ Check logs: `tail -f logs/scraper.log`

### Getting Blocked
→ See [BEST_PRACTICES.md](BEST_PRACTICES.md) - "If You Get Blocked"

### Salary Parsing Issues
→ Run: `python test_salary_parser.py`
→ Check: [scraper/salary_parser.py](scraper/salary_parser.py)

### Pagination Not Working
→ See [PAGINATION_GUIDE.md](PAGINATION_GUIDE.md) - Troubleshooting

## 🔗 External Resources

- **Playwright Docs**: https://playwright.dev/python/
- **Python Async**: https://docs.python.org/3/library/asyncio.html
- **Pydantic Docs**: https://docs.pydantic.dev/
- **Pandas Docs**: https://pandas.pydata.org/docs/
- **JobStreet**: https://id.jobstreet.com/

## 📞 Common Questions

**Q: How do I run the scraper?**
A: `python main.py` - See [QUICK_START.md](QUICK_START.md)

**Q: How do I customize keywords/locations?**
A: Edit [config.yaml](config.yaml) or use command-line args - See [README.md](README.md)

**Q: How do I avoid getting blocked?**
A: Read [BEST_PRACTICES.md](BEST_PRACTICES.md) for anti-detection tips

**Q: What formats are supported?**
A: JSON, Parquet, CSV - See [README.md](README.md#-data-export)

**Q: Can I use Docker?**
A: Yes! See [INSTALLATION.md](INSTALLATION.md) - Docker section

**Q: How do I handle pagination?**
A: Read [PAGINATION_GUIDE.md](PAGINATION_GUIDE.md) for detailed guide

**Q: What's the salary parser accuracy?**
A: Handles 15+ formats. See [test_salary_parser.py](test_salary_parser.py)

## 📊 Statistics

| Metric | Value |
|--------|-------|
| Total Files | 18 |
| Total Lines of Code | 4,275+ |
| Documentation Lines | 2,000+ |
| Supported Salary Formats | 15+ |
| Supported Export Formats | 3 |
| Python Version | 3.11+ |
| Status | Production-Ready ✅ |

## ✅ Pre-Scraping Checklist

- [ ] Read [QUICK_START.md](QUICK_START.md)
- [ ] Installed Python 3.11+
- [ ] Created virtual environment
- [ ] Installed dependencies: `pip install -r requirements.txt`
- [ ] Installed Playwright: `python -m playwright install chromium`
- [ ] Tested salary parser: `python test_salary_parser.py`
- [ ] Reviewed [config.yaml](config.yaml)
- [ ] Created `data/` directory or let script create it
- [ ] Checked [BEST_PRACTICES.md](BEST_PRACTICES.md) for anti-detection
- [ ] Ready to run: `python main.py`

## 🎯 Next Steps

1. **If you're new**: Start with [QUICK_START.md](QUICK_START.md)
2. **If you want details**: Read [README.md](README.md)
3. **If you're deploying**: Check [INSTALLATION.md](INSTALLATION.md)
4. **If getting blocked**: Study [BEST_PRACTICES.md](BEST_PRACTICES.md)
5. **If debugging pagination**: Refer to [PAGINATION_GUIDE.md](PAGINATION_GUIDE.md)

---

## 🚀 Quick Links

📍 **Documentation**:
- [Quick Start](QUICK_START.md) - 5-minute setup
- [Installation](INSTALLATION.md) - Detailed install guide
- [README](README.md) - Full documentation
- [Best Practices](BEST_PRACTICES.md) - Anti-detection guide
- [Pagination](PAGINATION_GUIDE.md) - Pagination deep dive
- [Project Structure](PROJECT_STRUCTURE.md) - Code overview

📍 **Source Code**:
- [main.py](main.py) - Entry point
- [config.py](config.py) - Configuration
- [scraper/__init__.py](scraper/__init__.py) - Core scraper
- [scraper/salary_parser.py](scraper/salary_parser.py) - Salary parsing
- [scraper/stealth.py](scraper/stealth.py) - Anti-detection

📍 **Configuration**:
- [config.yaml](config.yaml) - Edit this file
- [.env.example](.env.example) - Environment variables
- [requirements.txt](requirements.txt) - Dependencies

---

**Welcome to JobStreet Scraper! 🎉**

Start with [QUICK_START.md](QUICK_START.md) and you'll be scraping in 5 minutes! ⚡
