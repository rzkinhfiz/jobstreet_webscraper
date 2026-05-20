# Best Practices for JobStreet Scraping 🛡️

Advanced techniques and best practices for scraping JobStreet without getting banned or detected.

## 📊 JobStreet-Specific Anti-Detection

### 1. Understanding JobStreet's Defense Mechanisms

JobStreet employs several anti-scraping measures:

- **IP-based rate limiting**: Blocks IPs after ~50-100 requests in short time
- **User agent detection**: Identifies Playwright/Selenium automatically
- **Behavioral analysis**: Detects unnatural scrolling and clicking patterns
- **JavaScript rendering**: Heavy reliance on JS for dynamic content loading
- **Captcha/Bot detection**: Triggered by suspicious patterns

### 2. Request Pattern Optimization

**DO:**
```yaml
anti_detection:
  min_delay: 2.0              # 2-5 seconds between requests
  max_delay: 5.0
  enable_random_delays: true  # Vary delays for human feel
```

**DON'T:**
```yaml
anti_detection:
  min_delay: 0.1              # Too fast = detected immediately
  max_delay: 0.5
  enable_random_delays: false # Robotic pattern
```

### 3. User Agent Strategy

**Good:**
```python
# Current, real browsers
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0"
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0"
```

**Bad:**
```python
# Outdated, obviously fake, or generic
"Mozilla/5.0 (compatible; Playwright)"  # TOO OBVIOUS
"Mozilla/5.0 (Windows NT 5.1)"          # Windows XP - outdated
"curl/7.64.1"                           # Clearly not a browser
```

### 4. Viewport Configuration

**Always randomize viewport** - JobStreet detects consistent sizes:

```yaml
anti_detection:
  random_viewport: true
  # System randomizes from:
  # - 1920x1080 (most common)
  # - 1366x768  (laptops)
  # - 1440x900  (laptops)
  # - 2560x1440 (high-res)
  # - 1280x720  (tablets)
```

**Why randomize?**
```
Detection trigger: Same 1920x1080 every request = bot detected
Pattern: Real browsers have varying viewports based on device
```

### 5. Headers Spoofing

**Implement realistic headers:**

```python
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8",  # Indonesia + English
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",  # Do Not Track
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",  # Critical for modern detection
    "Sec-Fetch-Mode": "navigate",  # Must be set correctly
    "Sec-Fetch-Site": "none",      # First request pattern
}
```

**Why these headers matter:**
- `Sec-Fetch-*` headers are checked for inconsistencies
- Missing headers = bot detected
- Incorrect values = immediately flagged

### 6. JavaScript Injection for WebDriver Bypass

**Always inject stealth.js:**

```python
stealth_js = """
// Hide webdriver property (primary detection)
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined,
});

// Spoof plugins array
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5],  // Non-empty array
});

// Fix permissions API
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) =>
    parameters.name === 'notifications'
        ? Promise.resolve({ state: Notification.permission })
        : originalQuery(parameters);
```

**Detection bypass techniques:**

| Technique | Why It Works |
|-----------|------------|
| Override `navigator.webdriver` | Removes main automation indicator |
| Fake `navigator.plugins` | Looks like real browser |
| Fix `permissions.query` | Returns expected values |
| Spoof `chrome` object | Chrome-specific detection |
| Hide `arguments` callstack | Prevents script detection |

## 🚀 Scaling Strategies

### Single Instance (Conservative)
```yaml
max_concurrent_pages: 1        # One page at a time
max_pages_per_keyword: 5       # Limited pages
anti_detection:
  min_delay: 3.0
  max_delay: 8.0
proxy:
  enabled: false               # No proxy needed
```

**Pros:** Never gets blocked
**Cons:** Slow (1-2 hours per 100 jobs)

### Multiple Instances with Proxies (Recommended)
```yaml
# Instance 1
max_concurrent_pages: 2
max_pages_per_keyword: 10
proxy:
  enabled: true
  proxy_list:
    - "http://proxy1:8080"
    - "http://proxy2:8080"

# Instance 2 (different keywords)
keywords: ["Different keywords"]

# Instance 3 (different time/location)
search:
  locations: ["Different locations"]
```

**Pros:** Fast (100+ jobs per hour), distributed load
**Cons:** Requires proxies

### Enterprise Scale (Maximum Reliability)
```yaml
# Use 5-10 proxies
# Rotate daily
# Different browser types (Chromium, Firefox, Webkit)
# Distributed across regions
# Rate limit: 20 requests/minute per proxy
# Random job sequencing
```

## 🔄 Rotation & Distribution

### Proxy Rotation Strategy

**Bad:**
```python
proxies = ["proxy1", "proxy2"]  # Same order every time
proxy = proxies[i % len(proxies)]  # Sequential = detectable
```

**Good:**
```python
import random
proxies = ["proxy1", "proxy2", "proxy3", "proxy4", "proxy5"]
proxy = random.choice(proxies)  # Random = human-like
```

### Geographic Diversity

```yaml
search:
  locations:
    - "Kuala Lumpur"    # Different times
    - "Selangor"        # Different dates
    - "Penang"          # Different proxies
    - "Johor Bahru"
```

### Keyword Randomization

```python
# Bad: Always search in order
keywords = ["Data Scientist", "Backend Engineer", "Frontend Developer"]
for keyword in keywords:  # Ordered = detectable
    scrape(keyword)

# Good: Random order each time
random.shuffle(keywords)  # Randomized = human-like
for keyword in keywords:
    scrape(keyword)
```

## ⚠️ Red Flags That Trigger Blocking

### 1. **Rapid Fire Requests**
```
❌ Bad: 100 requests in 1 minute
✅ Good: 5-10 requests per minute
```

### 2. **Consistent Patterns**
```
❌ Bad: Same viewport, user agent, delays every time
✅ Good: Randomized across all parameters
```

### 3. **No Human Behavior**
```
❌ Bad: Never scrolls, never hovers, never waits
✅ Good: Random scrolling, hovering, longer waits
```

### 4. **Incomplete Headers**
```
❌ Bad: Missing Sec-Fetch-*, Accept-Language headers
✅ Good: All standard headers present and realistic
```

### 5. **JavaScript Disabled**
```
❌ Bad: Scraping without JavaScript (JobStreet loads via JS)
✅ Good: JavaScript enabled, interacting with rendered content
```

### 6. **No Timezone Matching**
```
❌ Bad: Timezone from US but scraping Malaysia
✅ Good: Accept-Language matches region (id-ID, ms-MY)
```

## 🎯 Test Your Setup

### Verify Anti-Detection is Working

```bash
# Enable headless=false temporarily to watch browser
python main.py

# Observe:
# 1. Real Chrome window opens (not puppeteer devtools)
# 2. Random scrolling behavior
# 3. Variable delays between actions
# 4. Human-like mouse movements
```

### Monitor Headers

```python
# Add this to scraper.py to log headers
page.on("request", lambda request: print(request.headers))
```

### Check for Detection Signs

```
✅ Success Signs:
- Page loads normally
- Jobs are visible
- No "suspicious activity" message
- Consistent with browser behavior

❌ Failure Signs:
- Blank page
- "Please verify you're a human"
- 403/429 errors (rate limit)
- Page redirects to homepage
- Cloudflare error page
```

## 🛡️ If You Get Blocked

### Immediate Actions

```bash
# 1. Stop scraping immediately
pkill -f jobstreet_scraper

# 2. Wait 24-48 hours before resuming
# 3. Switch to fresh IP/proxy
# 4. Increase delays significantly
```

### Prevention for Next Time

```yaml
# Double the delays
anti_detection:
  min_delay: 4.0   # Was 2.0
  max_delay: 10.0  # Was 5.0

# Reduce concurrent pages
max_concurrent_pages: 1  # Was 3

# Add more proxy rotation
proxy:
  proxy_list: ["proxy1", "proxy2", "proxy3", "proxy4", "proxy5"]
  proxy_rotation: true
```

### Recovery Checklist

- [ ] Wait 48+ hours
- [ ] New IP address or fresh proxy
- [ ] Disable browser headless (looks more human)
- [ ] Reduce keywords (start with 1)
- [ ] Reduce max_pages (start with 2)
- [ ] Increase delays (6-10 seconds)
- [ ] Enable all mouse movements
- [ ] Test with minimal config first

## 📈 Monitoring & Maintenance

### Health Checks

```bash
# Check error rate
grep "ERROR" logs/scraper.log | wc -l

# Check timeout rate
grep "TimeoutError\|timeout" logs/scraper.log | wc -l

# Check if getting blocked
grep "403\|429\|verify you're human" logs/scraper.log
```

### Alerts to Watch For

```
WARNING: High error rate detected
ACTION: Increase delays, check IP blocking

WARNING: Timeouts increasing
ACTION: Reduce concurrent pages, increase timeout

WARNING: Suspicious activity message
ACTION: Stop immediately, wait 48 hours
```

## 🔒 Advanced: Residential Proxies

### Why Residential > Datacenter

```
Datacenter Proxy:
- ❌ Same IP ranges as data centers (obviously bot)
- ❌ Easy to block all at once
- ⚠️ Cheaper but detected faster

Residential Proxy:
- ✅ Actual residential ISP IPs (looks human)
- ✅ Hard to block without affecting real users
- ✅ Slower but more reliable
- ✅ Recommended for serious scraping
```

### Setup Residential Proxy

```yaml
proxy:
  enabled: true
  proxy_list:
    # Format: http://api-endpoint.com
    # These usually rotate IPs automatically
    - "http://residential-proxy-api.example.com?session=1"
    - "http://residential-proxy-api.example.com?session=2"
  use_residential: true
  proxy_rotation: true
```

## 📋 Complete Anti-Ban Checklist

### Before Scraping
- [ ] Updated user agents (current Chrome, Firefox versions)
- [ ] Randomized viewports enabled
- [ ] Stealth.js injected
- [ ] Headers spoofed correctly
- [ ] Delays configured (min 2s, max 5s+)
- [ ] Proxies configured if needed
- [ ] Logging enabled for monitoring
- [ ] Test run with single keyword

### During Scraping
- [ ] Monitor logs for errors
- [ ] Watch for 403/429 errors
- [ ] Check delays are working
- [ ] Verify page loads successfully
- [ ] Confirm data extraction is working

### After Scraping
- [ ] Review logs for issues
- [ ] Check success rate
- [ ] Verify data quality
- [ ] Calculate next run timing
- [ ] Adjust config if needed

## 🎓 JobStreet-Specific Tips

### Know Their Timeline

```
Low Activity: 2am - 8am (Best time to scrape)
Peak Activity: 9am - 12pm, 2pm - 5pm (Avoid if possible)
Afternoon: 3pm - 6pm (Moderate)
Evening: 6pm - 11pm (Moderate)
```

### Job Listing Patterns

```
❌ Don't target same jobs repeatedly
✅ Scrape different keywords/locations daily

❌ Don't process all results at once
✅ Spread over time (10-20 jobs per hour)

❌ Don't request job details for every listing
✅ Extract from listing page when possible
```

### LocationSpecific

```
Malaysia (id.jobstreet.com):
- Accept-Language: "ms-MY,id-ID,id;q=0.9,en;q=0.8"
- Timezone: Asia/Kuala_Lumpur
- Common job types: Full-time, Contract, Internship
```

## 🚨 Last Resort: Contact JobStreet

If you need legitimate access:
1. Contact their API team
2. Request official data access
3. Explain your use case
4. May require paid partnership

## 📚 Additional Resources

- Playwright Stealth Plugin: github.com/dipjul/playwright-stealth
- HTTP Header Reference: mdn.io/http/headers
- User Agent Switcher: useragentstring.com

---

**Remember**: Scraping should be:
- ✅ Respectful to server resources
- ✅ Compliant with JobStreet's ToS
- ✅ For legitimate purposes (research, analysis)
- ✅ Not for competing services

**Happy ethical scraping!** 🎯
