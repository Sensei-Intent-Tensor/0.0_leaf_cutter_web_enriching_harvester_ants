"""
Simple Ant Template
===================

A basic scraper for static HTML pages.

Usage:
    class MyAnt(SimpleAnt):
        name = "my_scraper"
        selectors = {
            'title': 'h1',
            'content': '.main-content',
        }
    
    ant = MyAnt()
    result = ant.scrape('https://example.com')
"""

import logging
import time
import random
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

import requests
from bs4 import BeautifulSoup


@dataclass
class ScrapeResult:
    success: bool
    url: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    scraped_at: datetime = None
    duration_ms: float = 0
    
    def __post_init__(self):
        if self.scraped_at is None:
            self.scraped_at = datetime.utcnow()


class SimpleAnt:
    """
    Simple ant for scraping static HTML pages.
    
    Customize by setting:
        - name: Identifier for this scraper
        - selectors: Dict mapping field names to CSS selectors
        - headers: Custom HTTP headers
        - delay: Seconds to wait between requests
    """
    
    name: str = "simple_ant"
    
    # Override in subclass
    selectors: Dict[str, str] = {}
    
    # Default headers
    headers: Dict[str, str] = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    # Rate limiting
    delay_min: float = 1.0
    delay_max: float = 3.0
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 5.0
    
    def __init__(self, **kwargs):
        """Initialize ant with optional overrides."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.logger = logging.getLogger(f"ant.{self.name}")
        self._last_request = 0
    
    def scrape(self, url: str) -> ScrapeResult:
        """Scrape a single URL."""
        start = time.time()
        
        # Rate limiting
        self._wait_for_rate_limit()
        
        # Fetch
        try:
            response = self._fetch(url)
        except Exception as e:
            return ScrapeResult(
                success=False,
                url=url,
                error=str(e),
                duration_ms=(time.time() - start) * 1000
            )
        
        if response.status_code != 200:
            return ScrapeResult(
                success=False,
                url=url,
                error=f"HTTP {response.status_code}",
                status_code=response.status_code,
                duration_ms=(time.time() - start) * 1000
            )
        
        # Parse and extract
        soup = BeautifulSoup(response.text, 'lxml')
        data = self.extract(soup)
        
        return ScrapeResult(
            success=True,
            url=url,
            data=data,
            status_code=response.status_code,
            duration_ms=(time.time() - start) * 1000
        )
    
    def extract(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract data from soup using selectors.
        Override for custom extraction logic.
        """
        data = {}
        
        for field, selector in self.selectors.items():
            element = soup.select_one(selector)
            data[field] = element.get_text(strip=True) if element else None
        
        return data
    
    def _fetch(self, url: str) -> requests.Response:
        """Fetch URL with retries."""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=30)
                return response
            except requests.RequestException as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
        
        raise last_error
    
    def _wait_for_rate_limit(self):
        """Wait to respect rate limit."""
        elapsed = time.time() - self._last_request
        delay = random.uniform(self.delay_min, self.delay_max)
        
        if elapsed < delay:
            time.sleep(delay - elapsed)
        
        self._last_request = time.time()


# Example usage
if __name__ == "__main__":
    class ExampleAnt(SimpleAnt):
        name = "example"
        selectors = {
            'title': 'h1',
            'content': 'p',
        }
    
    ant = ExampleAnt()
    result = ant.scrape('https://example.com')
    print(f"Success: {result.success}")
    print(f"Data: {result.data}")
