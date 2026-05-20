# Installation & Setup Guide

Complete step-by-step installation guide for the JobStreet Scraper.

## 📋 Prerequisites

Before installing, ensure you have:
- **Python 3.11+** installed
- **pip** package manager
- **Git** (for version control)
- **~500MB free disk space** (for Playwright browsers)
- **Internet connection** (for package downloads)

### Verify Prerequisites

```bash
# Check Python version (must be 3.11+)
python --version
# or
python3 --version

# Check pip
pip --version

# Check git
git --version
```

## 🚀 Installation Methods

### Method 1: Manual Installation (Recommended)

**Step 1: Navigate to project directory**
```bash
cd jobstreet-scraper
```

**Step 2: Create virtual environment**

On Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

**Step 3: Upgrade pip**
```bash
pip install --upgrade pip
```

**Step 4: Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 5: Install Playwright browsers**

This step installs the Chromium browser (~150MB):
```bash
python -m playwright install chromium
```

Or install all browsers:
```bash
python -m playwright install
```

**Step 6: Verify installation**
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
  ...
```

### Method 2: Using Make (Linux/Mac only)

If you have Make installed:

```bash
# Complete setup (venv + install + playwright)
make setup

# Activate venv
source venv/bin/activate

# Run test
make test

# Run scraper
make run
```

### Method 3: Docker (No Python installation required!)

**Step 1: Install Docker**

Download from: https://www.docker.com/products/docker-desktop

**Step 2: Build image**
```bash
docker build -t jobstreet-scraper .
```

**Step 3: Run container**
```bash
docker run -v $(pwd)/data:/app/data jobstreet-scraper
```

Or with docker-compose:
```bash
docker-compose up scraper
```

**Data will be saved in the `data/` directory on your host machine.**

### Method 4: Using Docker Compose

**Step 1: Ensure docker-compose is installed**
```bash
docker-compose --version
```

**Step 2: Start scraper**
```bash
docker-compose up scraper
```

**Step 3: View logs** (in another terminal)
```bash
docker-compose logs -f scraper
```

**Step 4: Stop**
```bash
docker-compose down
```

## ⚙️ Post-Installation Setup

### 1. Create Configuration File

Copy the example config:
```bash
cp config.yaml config.yaml  # Already exists as template
```

Edit for your preferences:
```bash
# Linux/Mac
nano config.yaml

# Or use any editor
```

### 2. Create Data Directory (if not exists)

```bash
mkdir -p data/raw data/processed logs
```

### 3. Optional: Setup Environment File

```bash
cp .env.example .env

# Edit .env with your settings
```

### 4. Optional: Install Development Dependencies

For development/testing:
```bash
pip install -r requirements-dev.txt
```

## ✅ Verification Checklist

After installation, verify everything works:

- [ ] Python 3.11+ installed: `python --version`
- [ ] Virtual environment active: `which python` (shows venv path)
- [ ] Dependencies installed: `pip list` (shows playwright, pandas, etc.)
- [ ] Playwright browsers installed: `python -c "from playwright.async_api import async_playwright; print('OK')"`
- [ ] Test salary parser: `python test_salary_parser.py`
- [ ] Data directories exist: `ls -la data/`

## 🔧 Troubleshooting Installation

### Error: "Python 3.11+ not found"

**Solution:**
```bash
# Install Python 3.11+
# Windows: https://www.python.org/downloads/
# Mac: brew install python@3.11
# Linux: apt-get install python3.11

# Verify installation
python3.11 --version

# Create venv with specific version
python3.11 -m venv venv
```

### Error: "No module named 'playwright'"

**Solution:**
```bash
# Verify venv is activated (should show venv in prompt)
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify
python -c "import playwright; print(playwright.__version__)"
```

### Error: "Browser executable not found"

**Solution:**
```bash
# Install Playwright browsers
python -m playwright install chromium

# Or all browsers
python -m playwright install

# Verify
python -m playwright install --with-deps
```

### Error: "Permission denied" (Linux/Mac)

**Solution:**
```bash
# Make scripts executable
chmod +x main.py

# Or use python explicitly
python main.py
```

### Error: "ModuleNotFoundError: No module named 'loguru'"

**Solution:**
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### Docker Error: "Cannot find image"

**Solution:**
```bash
# Build image first
docker build -t jobstreet-scraper .

# Then run
docker run -v $(pwd)/data:/app/data jobstreet-scraper
```

## 🎯 Quick Start After Installation

### Run basic scrape
```bash
python main.py
```

### Run with custom keywords
```bash
python main.py --keyword "Data Scientist" "Backend Engineer"
```

### Run with configuration file
```bash
python main.py --config config.yaml
```

### View help
```bash
python main.py --help
```

### Check logs
```bash
tail -f logs/scraper.log
```

## 📦 Package Versions

The project uses these key packages:

```
playwright                  >= 1.45.0   (browser automation)
playwright-stealth          >= 1.0.1    (anti-detection)
pydantic                    >= 2.0.0    (data validation)
aiohttp                     >= 3.9.0    (async HTTP)
tenacity                    >= 8.3.0    (retry logic)
pandas                      >= 2.0.0    (data analysis)
pyarrow                     >= 14.0.0   (parquet support)
pyyaml                      >= 6.0.0    (YAML parsing)
python-dotenv               >= 1.0.0    (env variables)
loguru                      >= 0.7.0    (logging)
httpx                       >= 0.25.0   (HTTP client)
```

## 🐍 Python Version Compatibility

| Python Version | Status | Notes |
|---|---|---|
| 3.10 | ⚠️ Not supported | Use 3.11+ |
| 3.11 | ✅ Supported | Recommended |
| 3.12 | ✅ Supported | Latest stable |
| 3.13 | ⚠️ Experimental | May work |
| 2.7 | ❌ Not supported | Too old |

## 🖥️ OS Compatibility

### Linux (Recommended for servers)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

### macOS
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium --with-deps
```

### Windows
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
```

### Docker (All platforms)
```bash
docker build -t jobstreet-scraper .
docker run -v $(pwd)/data:/app/data jobstreet-scraper
```

## 📚 Next Steps

After successful installation:

1. **Read [QUICK_START.md](QUICK_START.md)** - Get scraping in 5 minutes
2. **Read [README.md](README.md)** - Full documentation
3. **Check [BEST_PRACTICES.md](BEST_PRACTICES.md)** - Anti-detection techniques
4. **Review [PAGINATION_GUIDE.md](PAGINATION_GUIDE.md)** - Pagination handling
5. **Read [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Code overview

## 🆘 Still Having Issues?

1. **Check logs**: `cat logs/scraper.log` or `tail -f logs/scraper.log`
2. **Run tests**: `python test_salary_parser.py`
3. **Verify setup**: `python -c "import playwright; print('OK')"`
4. **Check config**: Compare your `config.yaml` with defaults
5. **Enable debug**: Set `log_level: DEBUG` in `config.yaml`

## 💡 Pro Tips

1. **Use virtual environments always** - Prevents package conflicts
2. **Keep dependencies updated** - `pip install -U -r requirements.txt`
3. **Monitor logs** - `tail -f logs/scraper.log` during scraping
4. **Start small** - Test with 1-2 keywords before scaling
5. **Use Docker for servers** - More reproducible environment

## 🔐 Security Notes

1. **Never commit `.env` file** - Contains sensitive data
2. **Use proxies for production** - Distributes traffic
3. **Rotate user agents** - Looks more human
4. **Don't hardcode credentials** - Use environment variables
5. **Review logs for errors** - Catch issues early

## 📞 Support Resources

- **Playwright Docs**: https://playwright.dev/python/
- **Python Docs**: https://docs.python.org/3/
- **JobStreet**: https://id.jobstreet.com/

---

**Installation complete! You're ready to scrape. Start with [QUICK_START.md](QUICK_START.md)** 🚀
