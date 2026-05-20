# Pagination & Infinite Scroll Handling Guide

Comprehensive guide to handling JobStreet's pagination and dynamic loading mechanisms.

## 🔄 Understanding JobStreet's Pagination Methods

JobStreet uses multiple pagination strategies depending on the page type and user behavior:

### 1. URL-Based Pagination (Traditional)

**Pattern:**
```
https://id.jobstreet.com/en/jobs?q=keyword&page=1
https://id.jobstreet.com/en/jobs?q=keyword&page=2
https://id.jobstreet.com/en/jobs?q=keyword&page=3
```

**Detection:**
```python
# Look for page parameter in URL
if "?page=" in response.url or "&page=" in response.url:
    current_page = extract_page_number(response.url)
    next_url = response.url.replace(f"page={current_page}", f"page={current_page + 1}")
```

### 2. Infinite Scroll (Dynamic Loading)

**Pattern:**
- Initial load: ~20 jobs
- User scrolls down
- JavaScript triggers API call
- More jobs loaded via AJAX
- Process repeats until end

**Detection:**
```python
async def handle_infinite_scroll(page):
    """Detect and handle infinite scroll"""
    previous_height = 0
    
    while True:
        current_height = await page.evaluate(
            "document.documentElement.scrollHeight"
        )
        
        if current_height == previous_height:
            break  # No new content loaded
        
        # Scroll down
        await page.evaluate(
            f"window.scrollBy(0, {random.randint(300, 800)})"
        )
        
        # Wait for content to load
        await page.wait_for_timeout(2000)
        
        previous_height = current_height
```

### 3. Load More Button

**Pattern:**
```html
<button id="load-more" class="btn-load-more">
    Load More Jobs
</button>
```

**Detection & Handling:**
```python
async def handle_load_more_button(page):
    """Click 'Load More' button repeatedly"""
    while True:
        try:
            # Look for load more button
            button = await page.query_selector(
                "button:has-text('Load More'), "
                "a:has-text('Show More'), "
                "[class*='load-more']"
            )
            
            if not button or not await button.is_visible():
                break  # No more button
            
            # Click button
            await button.click()
            
            # Wait for jobs to load
            await page.wait_for_timeout(2000)
            
        except Exception as e:
            logger.debug(f"Error clicking load more: {e}")
            break
```

## 🎯 Implementation in Scraper

### Current Implementation

The scraper includes both pagination methods:

```python
async def _navigate_to_next_page(self, page: Page, current_page: int) -> bool:
    """
    Navigate to next page - handles both pagination and infinite scroll
    """
    try:
        # Method 1: Look for "Next" button
        next_button = await page.query_selector(
            "a[rel='next'], button:has-text('Next'), a:has-text('Next')"
        )
        
        if next_button and await next_button.is_visible():
            await next_button.click()
            await asyncio.sleep(random.uniform(2, 4))
            return True
        
        # Method 2: Infinite scroll
        await StealthBrowser.human_like_scroll(page, max_scrolls=3)
        await asyncio.sleep(random.uniform(1, 2))
        return True
    
    except Exception as e:
        logger.debug(f"Error navigating: {e}")
        return False
```

### Enhanced Implementation

For production use, consider extending with:

```python
async def handle_advanced_pagination(self, page: Page) -> bool:
    """
    Advanced pagination handling with multiple strategies
    """
    strategies = [
        self._try_next_button,
        self._try_page_parameter,
        self._try_load_more_button,
        self._try_infinite_scroll,
    ]
    
    for strategy in strategies:
        success = await strategy(page)
        if success:
            return True
    
    return False

async def _try_next_button(self, page: Page) -> bool:
    """Try clicking next button"""
    selectors = [
        "a[rel='next']",
        "button:has-text('Next')",
        "a:has-text('Next')",
        "[class*='next-page']",
        "[aria-label*='Next']",
    ]
    
    for selector in selectors:
        try:
            button = await page.query_selector(selector)
            if button and await button.is_visible():
                await button.click()
                await asyncio.sleep(random.uniform(2, 4))
                return True
        except Exception:
            continue
    
    return False

async def _try_page_parameter(self, page: Page) -> bool:
    """Try updating page parameter in URL"""
    current_url = page.url
    
    # Extract current page
    if "page=" in current_url:
        parts = current_url.split("page=")
        prefix = parts[0] + "page="
        
        try:
            current_page = int(parts[1].split("&")[0])
            next_page = current_page + 1
            next_url = prefix + str(next_page) + (
                "&" + parts[1].split("&", 1)[1] if "&" in parts[1] else ""
            )
            
            await page.goto(next_url, wait_until="networkidle")
            await asyncio.sleep(random.uniform(2, 4))
            return True
        except Exception:
            pass
    
    return False

async def _try_infinite_scroll(self, page: Page) -> bool:
    """Try infinite scroll technique"""
    try:
        # Scroll down
        current_height = await page.evaluate(
            "document.documentElement.scrollHeight"
        )
        
        await page.evaluate(
            f"window.scrollBy(0, {random.randint(500, 1000)})"
        )
        
        # Wait for new content
        await asyncio.sleep(random.uniform(2, 3))
        
        new_height = await page.evaluate(
            "document.documentElement.scrollHeight"
        )
        
        return new_height > current_height
    except Exception:
        return False
```

## 📊 Pagination Detection Guide

### Identifying Pagination Method

```python
async def detect_pagination_method(page: Page) -> str:
    """Detect which pagination method is being used"""
    
    # Check for next button
    next_button = await page.query_selector("a[rel='next'], button:has-text('Next')")
    if next_button:
        return "next_button"
    
    # Check for page parameter
    if "?page=" in page.url:
        return "page_parameter"
    
    # Check for load more button
    load_more = await page.query_selector("[class*='load-more']")
    if load_more:
        return "load_more_button"
    
    # Default to infinite scroll
    return "infinite_scroll"
```

### Maximum Pages Detection

```python
async def detect_max_pages(page: Page) -> int:
    """Detect total number of pages available"""
    
    try:
        # Look for pagination info
        pagination_text = await page.text_content(
            "[class*='pagination'], [class*='page-info']"
        )
        
        if pagination_text:
            # Extract numbers and get max
            import re
            numbers = [int(n) for n in re.findall(r'\d+', pagination_text)]
            if numbers:
                return max(numbers)
        
        # Look for last page link
        last_link = await page.get_attribute(
            "a:last-child[href*='page=']",
            "href"
        )
        
        if last_link:
            match = re.search(r'page=(\d+)', last_link)
            if match:
                return int(match.group(1))
        
    except Exception:
        pass
    
    # Default: use configured max_pages
    return None
```

## ⚙️ Configuration Optimization

### For Maximum Coverage

```yaml
search:
  max_pages_per_keyword: 100  # Get all pages
  
anti_detection:
  min_delay: 1.0
  max_delay: 3.0
  enable_random_scrolling: true
  
# May take longer but gets complete data
```

### For Balanced Speed/Coverage

```yaml
search:
  max_pages_per_keyword: 10   # First 10 pages (usually ~200 jobs)
  
anti_detection:
  min_delay: 1.5
  max_delay: 4.0
```

### For Testing

```yaml
search:
  max_pages_per_keyword: 2    # Just 2-3 pages
  
anti_detection:
  min_delay: 0.5
  max_delay: 2.0
  # Faster for testing
```

## 🚀 Advanced Techniques

### Concurrent Page Loading

```python
async def load_multiple_pages_concurrent(self, page: Page, num_pages: int):
    """Load multiple pages concurrently"""
    
    tasks = []
    for page_num in range(1, num_pages + 1):
        task = self._load_page(page, page_num)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results

async def _load_page(self, page: Page, page_num: int):
    """Load specific page number"""
    
    url = f"{self.SEARCH_URL}?page={page_num}"
    await page.goto(url, wait_until="networkidle")
    
    jobs = await self._extract_jobs_from_page(page)
    return jobs
```

### Smart Scrolling

```python
async def smart_scroll_to_load(self, page: Page, target_jobs: int = 50):
    """
    Scroll intelligently until target number of jobs loaded
    """
    
    jobs_loaded = 0
    scroll_attempts = 0
    max_attempts = 10
    
    while jobs_loaded < target_jobs and scroll_attempts < max_attempts:
        # Get current job count
        current_jobs = len(await page.query_selector_all("a[data-job-id]"))
        
        if current_jobs >= target_jobs:
            break
        
        # Scroll to bottom
        await page.evaluate(
            "window.scrollTo(0, document.documentElement.scrollHeight)"
        )
        
        # Wait for content
        await asyncio.sleep(random.uniform(1, 2))
        
        jobs_loaded = current_jobs
        scroll_attempts += 1
    
    logger.info(f"Loaded {jobs_loaded} jobs after {scroll_attempts} scrolls")
    return jobs_loaded
```

### Batch Processing

```python
async def scrape_with_batching(self, keywords: List[str], batch_size: int = 3):
    """Process keywords in batches"""
    
    all_jobs = []
    
    for i in range(0, len(keywords), batch_size):
        batch = keywords[i:i+batch_size]
        logger.info(f"Processing batch: {batch}")
        
        tasks = [
            self.search_jobs(keyword, max_pages=5)
            for keyword in batch
        ]
        
        batch_results = await asyncio.gather(*tasks)
        all_jobs.extend(sum(batch_results, []))
        
        # Rest between batches
        if i + batch_size < len(keywords):
            await asyncio.sleep(random.uniform(5, 10))
    
    return all_jobs
```

## 🐛 Troubleshooting Pagination Issues

### Issue: "No jobs loaded on page 2"

**Cause**: URL-based pagination not working
**Solution**:
```python
# Debug: Print URL format
logger.info(f"Current URL: {page.url}")

# Try to manually construct next page URL
next_url = page.url.replace("page=1", "page=2")
await page.goto(next_url)
```

### Issue: "Stuck on infinite scroll"

**Cause**: No new content loading
**Solution**:
```python
# Add maximum scroll height limit
max_scroll_height = 100000  # pixels
current_scroll = 0

while current_scroll < max_scroll_height:
    await page.evaluate("window.scrollBy(0, 1000)")
    current_scroll += 1000
    await asyncio.sleep(1)
```

### Issue: "Timeout waiting for content"

**Cause**: Content takes too long to load
**Solution**:
```yaml
anti_detection:
  timeout: 120000  # Increase to 120 seconds
```

### Issue: "Job count not increasing"

**Cause**: Pagination ended but not detected
**Solution**:
```python
# Check if we're at end by comparing heights
previous_height = 0
no_change_count = 0

while no_change_count < 3:
    await page.evaluate("window.scrollBy(0, 500)")
    await asyncio.sleep(1)
    
    new_height = await page.evaluate(
        "document.documentElement.scrollHeight"
    )
    
    if new_height == previous_height:
        no_change_count += 1
    else:
        no_change_count = 0
    
    previous_height = new_height
```

## 📈 Performance Metrics

### Expected Performance

```
Method: Page Parameter URL
- Time per page: 2-4 seconds
- Jobs per page: ~10-20
- Total speed: ~60-100 jobs/minute

Method: Infinite Scroll
- Time per page: 3-5 seconds
- Jobs per page: ~20-30
- Total speed: ~50-80 jobs/minute

Method: Load More Button
- Time per page: 4-6 seconds
- Jobs per page: ~15-25
- Total speed: ~40-60 jobs/minute
```

## ✅ Pagination Best Practices

1. **Always detect pagination method first**
   - Don't assume URL-based pagination
   - Test with headless=false to visualize

2. **Implement fallback strategies**
   - Try multiple detection methods
   - Don't fail on one method

3. **Handle edge cases**
   - Empty results
   - No pagination (single page)
   - Blocking/ratelimit during pagination

4. **Set realistic limits**
   - Don't scrape 1000+ pages in one run
   - Distribute over multiple sessions

5. **Monitor performance**
   - Track pages scraped
   - Monitor errors/timeouts
   - Adjust delays if needed

6. **Test thoroughly**
   - Test with different keywords
   - Test pagination on different dates
   - Monitor for JobStreet changes

---

**Remember**: JobStreet's structure may change. Always test pagination manually before large-scale runs!
