"""
Anti-detection and stealth techniques for Playwright.
Implements best practices for 2026 to avoid bot detection on JobStreet.
"""

import asyncio
import random
from typing import Optional, List
from playwright.async_api import Page, BrowserContext
import user_agents  # python-user-agents package


class StealthBrowser:
    """
    Implements stealth techniques to bypass anti-bot detection.
    Includes human-like behavior, randomization, and various evasion techniques.
    """
    
    # User agents for desktop browsers
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    ]
    
    # Viewport sizes for different devices
    VIEWPORTS = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1440, "height": 900},
        {"width": 2560, "height": 1440},
        {"width": 1280, "height": 720},
    ]
    
    @staticmethod
    def get_random_user_agent() -> str:
        """Get a random desktop user agent"""
        return random.choice(StealthBrowser.USER_AGENTS)
    
    @staticmethod
    def get_random_viewport() -> dict:
        """Get a random viewport size"""
        return random.choice(StealthBrowser.VIEWPORTS)
    
    @staticmethod
    async def inject_stealth_js(page: Page) -> None:
        """
        Inject JavaScript to bypass webdriver detection.
        This is the new approach for 2026 anti-detection.
        """
        stealth_js = """
        // Override navigator.webdriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        // Override navigator.plugins to avoid detection
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        // Override navigator.languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en', 'id-ID', 'id'],
        });
        
        // Spoof chrome object
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
        };
        
        // Remove headless chrome indicators
        Object.defineProperty(navigator, 'userAgentData', {
            get: () => ({
                brands: [
                    { brand: 'Not_A Brand', version: '99' },
                    { brand: 'Google Chrome', version: '125' },
                ],
                mobile: false,
                platform: 'Windows',
            }),
        });
        
        // Fix permissions API
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) =>
            parameters.name === 'notifications'
                ? Promise.resolve({ state: Notification.permission })
                : originalQuery(parameters);
        
        // Override toString of functions to hide automation
        const handler = {
            get: (target, prop) => {
                if (prop === 'toString') {
                    return () => 'function() { [native code] }';
                }
                return Reflect.get(target, prop);
            },
        };
        
        window.Promise = new Proxy(window.Promise, handler);
        
        // Remove headless indicators in WebGL
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) {
                return 'Intel Inc.';
            }
            if (parameter === 37446) {
                return 'Intel Iris OpenGL Engine';
            }
            return getParameter(parameter);
        };
        """
        
        await page.add_init_script(stealth_js)
    
    @staticmethod
    async def setup_stealth_context(context: BrowserContext, config) -> None:
        """
        Setup stealth context with anti-detection headers and settings.
        
        Args:
            context: BrowserContext from Playwright
            config: ScraperConfig object
        """
        # Set extra HTTP headers
        await context.set_extra_http_headers({
            "Accept-Language": config.anti_detection.accept_language,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        })
    
    @staticmethod
    async def human_like_scroll(page: Page, max_scrolls: Optional[int] = None) -> None:
        """
        Scroll page in a human-like manner with random delays and movements.
        
        Args:
            page: Playwright page object
            max_scrolls: Maximum number of scrolls (None = scroll to bottom)
        """
        scroll_count = 0
        previous_height = 0
        
        while True:
            # Get current scroll height
            current_height = await page.evaluate("document.documentElement.scrollHeight")
            
            if current_height == previous_height:
                break  # Reached end of page
            
            if max_scrolls and scroll_count >= max_scrolls:
                break
            
            # Random scroll distance
            scroll_distance = random.randint(300, 800)
            await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
            
            # Random delay between scrolls (human-like behavior)
            delay = random.uniform(0.5, 2.0)
            await asyncio.sleep(delay)
            
            previous_height = current_height
            scroll_count += 1
    
    @staticmethod
    async def random_mouse_movements(page: Page, count: int = 3) -> None:
        """
        Perform random mouse movements to simulate human presence.
        
        Args:
            page: Playwright page object
            count: Number of random movements
        """
        viewport = page.viewport_size
        if not viewport:
            return
        
        for _ in range(count):
            # Random position
            x = random.randint(0, viewport["width"])
            y = random.randint(0, viewport["height"])
            
            # Move mouse
            await page.mouse.move(x, y)
            
            # Random delay
            await asyncio.sleep(random.uniform(0.2, 0.8))
    
    @staticmethod
    async def random_delay(min_delay: float = 1.0, max_delay: float = 5.0) -> None:
        """
        Random delay to simulate human reading time.
        
        Args:
            min_delay: Minimum delay in seconds
            max_delay: Maximum delay in seconds
        """
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)
    
    @staticmethod
    async def simulate_typing(page: Page, selector: str, text: str, delay: float = 0.05) -> None:
        """
        Simulate human typing with character-by-character delays.
        
        Args:
            page: Playwright page object
            selector: CSS selector for input field
            text: Text to type
            delay: Delay between characters in seconds
        """
        await page.focus(selector)
        
        for char in text:
            await page.keyboard.type(char)
            await asyncio.sleep(random.uniform(delay * 0.5, delay * 1.5))
    
    @staticmethod
    async def random_click_on_page(page: Page) -> None:
        """
        Perform random clicks on the page to simulate user interaction.
        """
        try:
            # Get all clickable elements
            clickables = await page.query_selector_all("a, button, input[type='text']")
            
            if clickables and random.random() > 0.7:  # 30% chance
                element = random.choice(clickables[:min(5, len(clickables))])
                # Scroll element into view
                await element.scroll_into_view_if_needed()
                await asyncio.sleep(random.uniform(0.1, 0.3))
                await element.hover()
                await asyncio.sleep(random.uniform(0.05, 0.15))
        except Exception:
            pass  # Silently ignore any clicking errors


class ProxyRotator:
    """Handle proxy rotation for distributed scraping"""
    
    def __init__(self, proxy_list: List[str]):
        """
        Initialize proxy rotator.
        
        Args:
            proxy_list: List of proxy URLs (e.g., ['http://proxy1:8080', ...])
        """
        self.proxy_list = proxy_list
        self.current_index = 0
    
    def get_next_proxy(self) -> Optional[str]:
        """Get next proxy in rotation"""
        if not self.proxy_list:
            return None
        
        proxy = self.proxy_list[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxy_list)
        return proxy
    
    def get_random_proxy(self) -> Optional[str]:
        """Get random proxy from list"""
        if not self.proxy_list:
            return None
        return random.choice(self.proxy_list)


class RateLimiter:
    """Implement rate limiting to avoid overwhelming the server"""
    
    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute
        """
        self.requests_per_minute = requests_per_minute
        self.min_delay = 60 / requests_per_minute
        self.last_request_time = 0
    
    async def wait_if_needed(self) -> None:
        """Wait if necessary to respect rate limit"""
        import time
        
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            await asyncio.sleep(self.min_delay - time_since_last)
        
        self.last_request_time = time.time()
