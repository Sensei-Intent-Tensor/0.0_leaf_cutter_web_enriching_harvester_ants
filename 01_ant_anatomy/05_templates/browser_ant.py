"""
Browser Ant Template
====================

Scraper for JavaScript-rendered pages using Playwright.

Usage:
    class SPAAnt(BrowserAnt):
        name = "spa_scraper"
        wait_for = ".dynamic-content"
        
        def extract(self, soup):
            return {'title': soup.select_one('h1').text}
    
    with SPAAnt() as ant:
        result = ant.scrape('https://example.com/spa')
"""

from simple_ant import SimpleAnt, ScrapeResult
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import time


class BrowserAnt(SimpleAnt):
    """
    Ant for JavaScript-rendered pages.
    
    Customize:
        - headless: Run browser in headless mode
        - wait_for: CSS selector to wait for before extracting
        - wait_timeout: Maximum wait time in ms
    """
    
    name: str = "browser_ant"
    
    # Browser settings
    headless: bool = True
    wait_for: Optional[str] = None
    wait_timeout: int = 30000
    
    # Playwright objects
    _playwright = None
    _browser = None
    _page = None
    
    def __enter__(self):
        """Set up browser on context entry."""
        self._setup_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up browser on context exit."""
        self._teardown_browser()
    
    def _setup_browser(self):
        """Initialize Playwright browser."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise ImportError("Playwright required. Install with: pip install playwright && playwright install")
        
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self.headless)
        
        # Create page with settings
        context = self._browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=self.headers.get('User-Agent')
        )
        self._page = context.new_page()
    
    def _teardown_browser(self):
        """Clean up Playwright resources."""
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
    
    def scrape(self, url: str) -> ScrapeResult:
        """Scrape URL with browser rendering."""
        if not self._browser:
            self._setup_browser()
        
        start = time.time()
        self._wait_for_rate_limit()
        
        try:
            # Navigate
            self._page.goto(url, timeout=self.wait_timeout)
            
            # Wait for content
            if self.wait_for:
                self._page.wait_for_selector(self.wait_for, timeout=self.wait_timeout)
            else:
                self._page.wait_for_load_state('networkidle')
            
            # Get HTML
            html = self._page.content()
            
            # Parse and extract
            soup = BeautifulSoup(html, 'lxml')
            data = self.extract(soup)
            
            return ScrapeResult(
                success=True,
                url=url,
                data=data,
                status_code=200,
                duration_ms=(time.time() - start) * 1000
            )
            
        except Exception as e:
            return ScrapeResult(
                success=False,
                url=url,
                error=str(e),
                duration_ms=(time.time() - start) * 1000
            )
    
    def click_and_extract(self, selector: str) -> Dict[str, Any]:
        """Click an element and extract after page updates."""
        self._page.click(selector)
        self._page.wait_for_load_state('networkidle')
        
        html = self._page.content()
        soup = BeautifulSoup(html, 'lxml')
        
        return self.extract(soup)
    
    def scroll_and_extract(self, scroll_count: int = 5) -> Dict[str, Any]:
        """Scroll page multiple times for infinite scroll."""
        for _ in range(scroll_count):
            self._page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            self._page.wait_for_timeout(2000)
        
        html = self._page.content()
        soup = BeautifulSoup(html, 'lxml')
        
        return self.extract(soup)


# Example usage
if __name__ == "__main__":
    class ExampleBrowserAnt(BrowserAnt):
        name = "example_browser"
        wait_for = "h1"
        
        selectors = {
            'title': 'h1',
            'content': 'p',
        }
    
    with ExampleBrowserAnt() as ant:
        result = ant.scrape('https://example.com')
        print(f"Success: {result.success}")
        print(f"Data: {result.data}")
