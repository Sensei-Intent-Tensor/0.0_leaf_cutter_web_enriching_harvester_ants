"""
BaseAnt - The Foundation of All Scrapers
========================================

This module provides the BaseAnt class, which serves as the foundation
for all scraping "ants" in the Leaf Cutter framework.

Usage:
    from base_ant import BaseAnt
    
    class MyAnt(BaseAnt):
        def extract(self, soup):
            return {'title': soup.select_one('h1').text}
    
    ant = MyAnt()
    result = ant.scrape('https://example.com')
"""

import time
import random
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class AntConfig:
    """Configuration for an Ant scraper."""
    
    # Request settings
    headers: Dict[str, str] = field(default_factory=lambda: {
        'User-Agent': 'LeafCutterAnt/1.0 (https://github.com/Sensei-Intent-Tensor)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    })
    timeout: int = 30
    
    # Rate limiting
    delay_min: float = 1.0
    delay_max: float = 3.0
    
    # Retry settings
    retry_count: int = 3
    retry_delay: float = 5.0
    retry_backoff: float = 2.0
    
    # Proxy settings
    proxy: Optional[str] = None
    proxy_rotation: bool = False
    
    # Parser settings
    parser: str = 'lxml'  # 'html.parser', 'lxml', 'html5lib'
    
    # Output settings
    include_metadata: bool = True
    include_raw_html: bool = False


# =============================================================================
# Result Classes
# =============================================================================

@dataclass
class ScrapeResult:
    """Result of a scraping operation."""
    
    success: bool
    url: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    scraped_at: datetime = field(default_factory=datetime.utcnow)
    duration_ms: Optional[float] = None
    raw_html: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        result = {
            'success': self.success,
            'url': self.url,
            'scraped_at': self.scraped_at.isoformat(),
        }
        
        if self.data:
            result['data'] = self.data
        if self.error:
            result['error'] = self.error
        if self.status_code:
            result['status_code'] = self.status_code
        if self.duration_ms:
            result['duration_ms'] = self.duration_ms
        if self.raw_html:
            result['raw_html'] = self.raw_html
            
        return result


@dataclass
class AntMetrics:
    """Metrics collected during scraping."""
    
    requests_made: int = 0
    requests_succeeded: int = 0
    requests_failed: int = 0
    total_duration_ms: float = 0
    retries: int = 0
    
    def record_request(self, success: bool, duration_ms: float):
        """Record a request."""
        self.requests_made += 1
        self.total_duration_ms += duration_ms
        
        if success:
            self.requests_succeeded += 1
        else:
            self.requests_failed += 1
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.requests_made == 0:
            return 0.0
        return self.requests_succeeded / self.requests_made
    
    @property
    def avg_duration_ms(self) -> float:
        """Calculate average request duration."""
        if self.requests_made == 0:
            return 0.0
        return self.total_duration_ms / self.requests_made


# =============================================================================
# Base Ant Class
# =============================================================================

class BaseAnt(ABC):
    """
    Base class for all scraping ants.
    
    Subclasses must implement the `extract` method to define
    how data is extracted from the parsed HTML.
    
    Example:
        class ProductAnt(BaseAnt):
            def extract(self, soup):
                return {
                    'title': soup.select_one('h1').get_text(strip=True),
                    'price': soup.select_one('.price').get_text(strip=True),
                }
        
        ant = ProductAnt()
        result = ant.scrape('https://example.com/product/123')
    """
    
    # Class-level configuration (can be overridden in subclasses)
    name: str = "BaseAnt"
    allowed_domains: List[str] = []
    
    def __init__(self, config: Optional[AntConfig] = None, **kwargs):
        """
        Initialize the ant.
        
        Args:
            config: AntConfig instance or None for defaults
            **kwargs: Override specific config values
        """
        self.config = config or AntConfig()
        
        # Apply kwargs overrides
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Setup session
        self.session = requests.Session()
        self.session.headers.update(self.config.headers)
        
        # Setup logging
        self.logger = logging.getLogger(f"ant.{self.name}")
        
        # Initialize metrics
        self.metrics = AntMetrics()
        
        # Track last request time for rate limiting
        self._last_request_time: Dict[str, float] = {}
    
    # -------------------------------------------------------------------------
    # Abstract Methods (must be implemented by subclasses)
    # -------------------------------------------------------------------------
    
    @abstractmethod
    def extract(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract data from parsed HTML.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Dictionary of extracted data
        """
        pass
    
    # -------------------------------------------------------------------------
    # Core Scraping Methods
    # -------------------------------------------------------------------------
    
    def scrape(self, url: str) -> ScrapeResult:
        """
        Scrape a single URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            ScrapeResult with data or error
        """
        start_time = time.time()
        
        # Validate URL
        if not self._validate_url(url):
            return ScrapeResult(
                success=False,
                url=url,
                error=f"URL not allowed: {url}"
            )
        
        # Apply rate limiting
        self._apply_rate_limit(url)
        
        # Fetch with retries
        response = self._fetch_with_retry(url)
        
        if response is None:
            duration_ms = (time.time() - start_time) * 1000
            return ScrapeResult(
                success=False,
                url=url,
                error="Failed to fetch after retries",
                duration_ms=duration_ms
            )
        
        # Check for blocks
        if self._is_blocked(response):
            duration_ms = (time.time() - start_time) * 1000
            return ScrapeResult(
                success=False,
                url=url,
                error="Blocked by website",
                status_code=response.status_code,
                duration_ms=duration_ms
            )
        
        # Parse HTML
        soup = BeautifulSoup(response.text, self.config.parser)
        
        # Extract data
        try:
            data = self.extract(soup)
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(f"Extraction error for {url}: {e}")
            return ScrapeResult(
                success=False,
                url=url,
                error=f"Extraction failed: {str(e)}",
                status_code=response.status_code,
                duration_ms=duration_ms
            )
        
        # Build result
        duration_ms = (time.time() - start_time) * 1000
        self.metrics.record_request(True, duration_ms)
        
        result = ScrapeResult(
            success=True,
            url=url,
            data=data,
            status_code=response.status_code,
            duration_ms=duration_ms
        )
        
        if self.config.include_raw_html:
            result.raw_html = response.text
        
        return result
    
    def scrape_many(self, urls: List[str]) -> List[ScrapeResult]:
        """
        Scrape multiple URLs sequentially.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of ScrapeResults
        """
        results = []
        
        for i, url in enumerate(urls):
            self.logger.info(f"Scraping {i+1}/{len(urls)}: {url}")
            result = self.scrape(url)
            results.append(result)
        
        return results
    
    # -------------------------------------------------------------------------
    # HTTP Methods
    # -------------------------------------------------------------------------
    
    def _fetch_with_retry(self, url: str) -> Optional[requests.Response]:
        """Fetch URL with retry logic."""
        
        delay = self.config.retry_delay
        
        for attempt in range(self.config.retry_count):
            try:
                response = self._fetch(url)
                
                # Success
                if response.status_code == 200:
                    return response
                
                # Retry on server errors
                if response.status_code >= 500:
                    self.logger.warning(
                        f"Server error {response.status_code} for {url}, "
                        f"attempt {attempt + 1}/{self.config.retry_count}"
                    )
                    self.metrics.retries += 1
                    time.sleep(delay)
                    delay *= self.config.retry_backoff
                    continue
                
                # Don't retry client errors (except 429)
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', delay))
                    self.logger.warning(f"Rate limited, waiting {retry_after}s")
                    self.metrics.retries += 1
                    time.sleep(retry_after)
                    continue
                
                # Other status codes - return as-is
                return response
                
            except requests.RequestException as e:
                self.logger.warning(
                    f"Request error for {url}: {e}, "
                    f"attempt {attempt + 1}/{self.config.retry_count}"
                )
                self.metrics.retries += 1
                time.sleep(delay)
                delay *= self.config.retry_backoff
        
        self.metrics.record_request(False, 0)
        return None
    
    def _fetch(self, url: str) -> requests.Response:
        """Make HTTP request."""
        
        proxies = None
        if self.config.proxy:
            proxies = {
                'http': self.config.proxy,
                'https': self.config.proxy
            }
        
        response = self.session.get(
            url,
            timeout=self.config.timeout,
            proxies=proxies
        )
        
        return response
    
    # -------------------------------------------------------------------------
    # Rate Limiting
    # -------------------------------------------------------------------------
    
    def _apply_rate_limit(self, url: str):
        """Apply rate limiting based on domain."""
        
        domain = urlparse(url).netloc
        
        if domain in self._last_request_time:
            elapsed = time.time() - self._last_request_time[domain]
            delay = random.uniform(self.config.delay_min, self.config.delay_max)
            
            if elapsed < delay:
                sleep_time = delay - elapsed
                self.logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)
        
        self._last_request_time[domain] = time.time()
    
    # -------------------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------------------
    
    def _validate_url(self, url: str) -> bool:
        """Check if URL is allowed."""
        
        if not self.allowed_domains:
            return True
        
        domain = urlparse(url).netloc
        return any(
            domain == allowed or domain.endswith(f'.{allowed}')
            for allowed in self.allowed_domains
        )
    
    def _is_blocked(self, response: requests.Response) -> bool:
        """Check if response indicates blocking."""
        
        # Status code checks
        if response.status_code in [403, 429, 503]:
            return True
        
        # Content checks (common block indicators)
        content_lower = response.text.lower()[:2000]
        block_indicators = [
            'access denied',
            'blocked',
            'captcha',
            'robot check',
            'unusual traffic',
            'rate limit',
        ]
        
        return any(indicator in content_lower for indicator in block_indicators)
    
    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------
    
    def safe_extract(
        self, 
        selector: str, 
        soup: BeautifulSoup,
        attribute: Optional[str] = None,
        default: Any = None
    ) -> Any:
        """
        Safely extract data with fallback.
        
        Args:
            selector: CSS selector
            soup: BeautifulSoup object
            attribute: Optional attribute to extract (e.g., 'href')
            default: Default value if not found
            
        Returns:
            Extracted value or default
        """
        element = soup.select_one(selector)
        
        if element is None:
            return default
        
        if attribute:
            return element.get(attribute, default)
        
        return element.get_text(strip=True) or default
    
    def safe_extract_all(
        self,
        selector: str,
        soup: BeautifulSoup,
        attribute: Optional[str] = None
    ) -> List[Any]:
        """
        Safely extract multiple elements.
        
        Args:
            selector: CSS selector
            soup: BeautifulSoup object
            attribute: Optional attribute to extract
            
        Returns:
            List of extracted values
        """
        elements = soup.select(selector)
        
        if attribute:
            return [el.get(attribute) for el in elements if el.get(attribute)]
        
        return [el.get_text(strip=True) for el in elements if el.get_text(strip=True)]
    
    def make_absolute_url(self, url: str, base_url: str) -> str:
        """Convert relative URL to absolute."""
        return urljoin(base_url, url)
    
    # -------------------------------------------------------------------------
    # Lifecycle Methods
    # -------------------------------------------------------------------------
    
    def setup(self):
        """Called before scraping begins. Override for custom setup."""
        pass
    
    def teardown(self):
        """Called after scraping ends. Override for custom cleanup."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        self.setup()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.teardown()


# =============================================================================
# Specialized Ant Types
# =============================================================================

class SimpleAnt(BaseAnt):
    """
    Simple ant for basic single-page scraping.
    
    Example:
        class ProductAnt(SimpleAnt):
            selectors = {
                'title': 'h1.product-title',
                'price': '.price-current',
                'description': '.product-description',
            }
        
        ant = ProductAnt()
        result = ant.scrape('https://example.com/product')
    """
    
    selectors: Dict[str, str] = {}
    
    def extract(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract data using defined selectors."""
        data = {}
        
        for field, selector in self.selectors.items():
            data[field] = self.safe_extract(selector, soup)
        
        return data


class PaginatedAnt(BaseAnt):
    """
    Ant for scraping paginated results.
    
    Example:
        class SearchAnt(PaginatedAnt):
            item_selector = '.search-result'
            next_page_selector = 'a.next-page'
            
            def extract_item(self, item):
                return {
                    'title': item.select_one('h3').get_text(strip=True),
                    'url': item.select_one('a')['href'],
                }
    """
    
    item_selector: str = ""
    next_page_selector: str = ""
    max_pages: int = 10
    
    @abstractmethod
    def extract_item(self, item: BeautifulSoup) -> Dict[str, Any]:
        """Extract data from a single item."""
        pass
    
    def extract(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract all items from the page."""
        items = soup.select(self.item_selector)
        
        return {
            'items': [self.extract_item(item) for item in items],
            'count': len(items)
        }
    
    def scrape_all_pages(self, start_url: str) -> List[Dict[str, Any]]:
        """Scrape all pages starting from the given URL."""
        all_items = []
        current_url = start_url
        page = 1
        
        while current_url and page <= self.max_pages:
            self.logger.info(f"Scraping page {page}: {current_url}")
            
            result = self.scrape(current_url)
            
            if not result.success:
                self.logger.error(f"Failed to scrape page {page}")
                break
            
            all_items.extend(result.data.get('items', []))
            
            # Find next page
            response = self.session.get(current_url)
            soup = BeautifulSoup(response.text, self.config.parser)
            next_link = soup.select_one(self.next_page_selector)
            
            if next_link and next_link.get('href'):
                current_url = self.make_absolute_url(next_link['href'], current_url)
                page += 1
            else:
                break
        
        return all_items


class APIAnt(BaseAnt):
    """
    Ant for consuming JSON APIs.
    
    Example:
        class ProductAPIAnt(APIAnt):
            def extract(self, data):
                return {
                    'id': data['product']['id'],
                    'name': data['product']['name'],
                    'price': data['product']['price'],
                }
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session.headers['Accept'] = 'application/json'
    
    def scrape(self, url: str) -> ScrapeResult:
        """Scrape JSON API endpoint."""
        start_time = time.time()
        
        self._apply_rate_limit(url)
        response = self._fetch_with_retry(url)
        
        if response is None:
            duration_ms = (time.time() - start_time) * 1000
            return ScrapeResult(
                success=False,
                url=url,
                error="Failed to fetch after retries",
                duration_ms=duration_ms
            )
        
        try:
            json_data = response.json()
        except ValueError as e:
            duration_ms = (time.time() - start_time) * 1000
            return ScrapeResult(
                success=False,
                url=url,
                error=f"Invalid JSON: {e}",
                status_code=response.status_code,
                duration_ms=duration_ms
            )
        
        try:
            data = self.extract(json_data)
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return ScrapeResult(
                success=False,
                url=url,
                error=f"Extraction failed: {e}",
                status_code=response.status_code,
                duration_ms=duration_ms
            )
        
        duration_ms = (time.time() - start_time) * 1000
        self.metrics.record_request(True, duration_ms)
        
        return ScrapeResult(
            success=True,
            url=url,
            data=data,
            status_code=response.status_code,
            duration_ms=duration_ms
        )
    
    @abstractmethod
    def extract(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from JSON response."""
        pass


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Example: Simple product scraper
    class ExampleProductAnt(SimpleAnt):
        name = "ExampleProductAnt"
        selectors = {
            'title': 'h1',
            'description': 'p',
        }
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Use the ant
    with ExampleProductAnt() as ant:
        result = ant.scrape('https://example.com')
        print(f"Success: {result.success}")
        print(f"Data: {result.data}")
        print(f"Duration: {result.duration_ms:.2f}ms")
