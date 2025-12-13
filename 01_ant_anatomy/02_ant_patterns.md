# Ant Patterns

> **Reusable Patterns for Common Scraping Scenarios**

This document catalogs common scraping patterns and when to use them. Each pattern solves a specific problem you'll encounter repeatedly.

---

## Pattern Categories

```
┌─────────────────────────────────────────────────────────────────┐
│                     PATTERN CATEGORIES                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  FETCHING PATTERNS                                              │
│  ├── Simple Request                                             │
│  ├── Session Management                                         │
│  ├── Browser Rendering                                          │
│  └── API Consumption                                            │
│                                                                 │
│  NAVIGATION PATTERNS                                            │
│  ├── Pagination                                                 │
│  ├── Infinite Scroll                                            │
│  ├── Category Crawling                                          │
│  └── Search Iteration                                           │
│                                                                 │
│  EXTRACTION PATTERNS                                            │
│  ├── List Page → Detail Page                                    │
│  ├── Nested Data                                                │
│  ├── Tabular Data                                               │
│  └── Multi-source Merge                                         │
│                                                                 │
│  RESILIENCE PATTERNS                                            │
│  ├── Retry with Backoff                                         │
│  ├── Fallback Selectors                                         │
│  ├── Checkpoint/Resume                                          │
│  └── Circuit Breaker                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Fetching Patterns

### Pattern 1: Simple Request

**When:** Static HTML pages, no JavaScript, no authentication.

```python
class SimpleRequestAnt(BaseAnt):
    """Basic HTML fetching with requests."""
    
    def fetch(self, url: str) -> str:
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        return response.text
```

### Pattern 2: Session Management

**When:** Need to maintain cookies, handle login, follow redirects.

```python
class SessionAnt(BaseAnt):
    """Maintains session across requests."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """Initialize session with common settings."""
        self.session.headers.update(self.config.headers)
        
        # Set up retry strategy
        retry = Retry(total=3, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
    
    def login(self, login_url: str, credentials: dict) -> bool:
        """Authenticate the session."""
        # Get CSRF token if needed
        login_page = self.session.get(login_url)
        soup = BeautifulSoup(login_page.text, 'lxml')
        csrf = soup.select_one('input[name="csrf"]')
        
        if csrf:
            credentials['csrf'] = csrf['value']
        
        # Submit login
        response = self.session.post(login_url, data=credentials)
        return 'logout' in response.text.lower()
```

### Pattern 3: Browser Rendering

**When:** JavaScript-rendered content, SPAs, dynamic loading.

```python
class BrowserAnt(BaseAnt):
    """Uses Playwright for JavaScript rendering."""
    
    def __init__(self, *args, headless: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.headless = headless
        self._browser = None
        self._page = None
    
    def setup(self):
        from playwright.sync_api import sync_playwright
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self.headless)
        self._page = self._browser.new_page()
    
    def teardown(self):
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
    
    def fetch(self, url: str, wait_for: str = None) -> str:
        """Fetch page with JavaScript rendering."""
        self._page.goto(url)
        
        if wait_for:
            self._page.wait_for_selector(wait_for, timeout=30000)
        else:
            self._page.wait_for_load_state('networkidle')
        
        return self._page.content()
    
    def click_and_wait(self, selector: str, wait_for: str = None):
        """Click element and wait for result."""
        self._page.click(selector)
        
        if wait_for:
            self._page.wait_for_selector(wait_for)
        else:
            self._page.wait_for_load_state('networkidle')
```

### Pattern 4: API Consumption

**When:** Site has JSON API, data embedded in page as JSON.

```python
class APIAnt(BaseAnt):
    """Consumes JSON APIs."""
    
    def __init__(self, *args, api_key: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = api_key
        
        if api_key:
            self.session.headers['Authorization'] = f'Bearer {api_key}'
        self.session.headers['Accept'] = 'application/json'
    
    def fetch_json(self, url: str, params: dict = None) -> dict:
        """Fetch and parse JSON."""
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def post_json(self, url: str, data: dict) -> dict:
        """POST JSON data."""
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()
```

---

## Navigation Patterns

### Pattern 5: Pagination (Page Numbers)

**When:** Results spread across numbered pages.

```python
class PaginatedAnt(BaseAnt):
    """Handles page-numbered pagination."""
    
    max_pages: int = 100
    items_per_page: int = 20
    
    def build_page_url(self, base_url: str, page: int) -> str:
        """Construct URL for a specific page."""
        # Override in subclass for site-specific patterns
        if '?' in base_url:
            return f"{base_url}&page={page}"
        return f"{base_url}?page={page}"
    
    def scrape_all_pages(self, base_url: str) -> list:
        """Scrape all pages until empty or max reached."""
        all_items = []
        page = 1
        
        while page <= self.max_pages:
            url = self.build_page_url(base_url, page)
            self.logger.info(f"Scraping page {page}")
            
            result = self.scrape(url)
            
            if not result.success:
                self.logger.warning(f"Failed on page {page}")
                break
            
            items = result.data.get('items', [])
            
            if not items:
                self.logger.info("No more items, stopping")
                break
            
            all_items.extend(items)
            
            # Check if this was the last page
            if len(items) < self.items_per_page:
                break
            
            page += 1
        
        return all_items
```

### Pattern 6: Cursor/Token Pagination

**When:** API uses cursor tokens for pagination.

```python
class CursorPaginatedAnt(APIAnt):
    """Handles cursor-based pagination."""
    
    def scrape_all(self, endpoint: str, params: dict = None) -> list:
        """Fetch all pages using cursor pagination."""
        all_items = []
        cursor = None
        params = params or {}
        
        while True:
            if cursor:
                params['cursor'] = cursor
            
            data = self.fetch_json(endpoint, params)
            
            items = data.get('results', data.get('data', []))
            all_items.extend(items)
            
            # Get next cursor
            cursor = data.get('next_cursor') or data.get('pagination', {}).get('next')
            
            if not cursor:
                break
            
            self._apply_rate_limit(endpoint)
        
        return all_items
```

### Pattern 7: Infinite Scroll

**When:** Content loads on scroll, no pagination links.

```python
class InfiniteScrollAnt(BrowserAnt):
    """Handles infinite scroll pages."""
    
    def scrape_infinite(self, url: str, item_selector: str, max_items: int = 1000) -> list:
        """Scroll and collect items."""
        self._page.goto(url)
        self._page.wait_for_selector(item_selector)
        
        items = set()
        last_count = 0
        stale_rounds = 0
        
        while len(items) < max_items and stale_rounds < 3:
            # Get current items
            elements = self._page.query_selector_all(item_selector)
            
            for el in elements:
                item_id = el.get_attribute('data-id') or el.inner_text()[:50]
                items.add(item_id)
            
            # Check if we got new items
            if len(items) == last_count:
                stale_rounds += 1
            else:
                stale_rounds = 0
                last_count = len(items)
            
            # Scroll down
            self._page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            self._page.wait_for_timeout(2000)
        
        return list(items)
```

### Pattern 8: Category Crawling

**When:** Need to traverse category hierarchy.

```python
class CategoryCrawlerAnt(BaseAnt):
    """Crawls through category hierarchies."""
    
    def crawl_categories(self, root_url: str) -> list:
        """Recursively crawl all categories."""
        visited = set()
        all_items = []
        
        def crawl(url: str, depth: int = 0):
            if url in visited or depth > 5:
                return
            
            visited.add(url)
            self.logger.info(f"Crawling category: {url}")
            
            result = self.scrape(url)
            
            if not result.success:
                return
            
            # Collect items from this category
            items = result.data.get('items', [])
            all_items.extend(items)
            
            # Find subcategories
            subcategories = result.data.get('subcategories', [])
            for subcat_url in subcategories:
                self._apply_rate_limit(subcat_url)
                crawl(subcat_url, depth + 1)
        
        crawl(root_url)
        return all_items
```

---

## Extraction Patterns

### Pattern 9: List Page → Detail Page

**When:** Need data from both listing and detail pages.

```python
class ListDetailAnt(BaseAnt):
    """Two-phase scraping: list pages then detail pages."""
    
    list_item_selector: str = '.item'
    detail_link_selector: str = 'a'
    
    def extract_list_items(self, soup: BeautifulSoup) -> list:
        """Extract item URLs from list page."""
        items = soup.select(self.list_item_selector)
        urls = []
        
        for item in items:
            link = item.select_one(self.detail_link_selector)
            if link and link.get('href'):
                urls.append(link['href'])
        
        return urls
    
    def extract_detail(self, soup: BeautifulSoup) -> dict:
        """Extract data from detail page. Override in subclass."""
        raise NotImplementedError
    
    def scrape_list_and_details(self, list_url: str) -> list:
        """Scrape list page then all detail pages."""
        # Phase 1: Get list page
        list_result = self.scrape(list_url)
        
        if not list_result.success:
            return []
        
        soup = BeautifulSoup(list_result.raw_html, 'lxml')
        detail_urls = self.extract_list_items(soup)
        
        # Phase 2: Scrape each detail page
        all_data = []
        
        for url in detail_urls:
            absolute_url = self.make_absolute_url(url, list_url)
            
            result = self.scrape(absolute_url)
            
            if result.success:
                all_data.append(result.data)
            
            self._apply_rate_limit(absolute_url)
        
        return all_data
```

### Pattern 10: Nested Data Extraction

**When:** Data has parent-child relationships.

```python
class NestedDataAnt(BaseAnt):
    """Extracts hierarchical nested data."""
    
    def extract(self, soup: BeautifulSoup) -> dict:
        """Extract nested product data."""
        
        product = {
            'name': self.safe_extract('.product-name', soup),
            'price': self.safe_extract('.price', soup),
            
            # Nested: variants
            'variants': [],
            
            # Nested: reviews
            'reviews': {
                'average_rating': self.safe_extract('.avg-rating', soup),
                'count': self.safe_extract('.review-count', soup),
                'breakdown': self._extract_rating_breakdown(soup),
            },
            
            # Nested: specifications
            'specifications': self._extract_specs(soup),
        }
        
        # Extract variants
        for variant in soup.select('.variant'):
            product['variants'].append({
                'sku': self.safe_extract('.sku', variant),
                'color': self.safe_extract('.color', variant),
                'size': self.safe_extract('.size', variant),
                'price': self.safe_extract('.variant-price', variant),
                'available': 'out-of-stock' not in variant.get('class', []),
            })
        
        return product
    
    def _extract_rating_breakdown(self, soup: BeautifulSoup) -> dict:
        """Extract star rating distribution."""
        breakdown = {}
        for row in soup.select('.rating-row'):
            stars = self.safe_extract('.stars', row)
            count = self.safe_extract('.count', row)
            if stars and count:
                breakdown[stars] = int(count)
        return breakdown
    
    def _extract_specs(self, soup: BeautifulSoup) -> dict:
        """Extract specification table."""
        specs = {}
        for row in soup.select('.spec-row'):
            key = self.safe_extract('.spec-name', row)
            value = self.safe_extract('.spec-value', row)
            if key:
                specs[key] = value
        return specs
```

### Pattern 11: Table Extraction

**When:** Data is in HTML tables.

```python
class TableAnt(BaseAnt):
    """Extracts data from HTML tables."""
    
    def extract_table(self, soup: BeautifulSoup, table_selector: str = 'table') -> list:
        """Convert HTML table to list of dicts."""
        table = soup.select_one(table_selector)
        
        if not table:
            return []
        
        # Get headers
        headers = []
        header_row = table.select_one('thead tr') or table.select_one('tr')
        
        for th in header_row.select('th, td'):
            headers.append(th.get_text(strip=True).lower().replace(' ', '_'))
        
        # Get data rows
        rows = []
        body = table.select_one('tbody') or table
        
        for tr in body.select('tr')[1:] if not table.select_one('thead') else body.select('tr'):
            cells = tr.select('td')
            
            if len(cells) == len(headers):
                row = {}
                for i, cell in enumerate(cells):
                    row[headers[i]] = cell.get_text(strip=True)
                rows.append(row)
        
        return rows
    
    def extract(self, soup: BeautifulSoup) -> dict:
        return {
            'table_data': self.extract_table(soup)
        }
```

---

## Resilience Patterns

### Pattern 12: Retry with Exponential Backoff

**When:** Handling transient failures gracefully.

```python
import time
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1, max_delay=60):
    """Decorator for retry with exponential backoff."""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries - 1:
                        sleep_time = min(delay * (2 ** attempt), max_delay)
                        time.sleep(sleep_time)
            
            raise last_exception
        
        return wrapper
    return decorator

class ResilientAnt(BaseAnt):
    """Ant with enhanced retry capabilities."""
    
    @retry_with_backoff(max_retries=3, base_delay=2)
    def fetch(self, url: str) -> str:
        response = self.session.get(url)
        response.raise_for_status()
        return response.text
```

### Pattern 13: Fallback Selectors

**When:** Site structure varies or changes frequently.

```python
class FallbackAnt(BaseAnt):
    """Uses fallback selectors when primary fails."""
    
    selector_fallbacks = {
        'title': ['h1.title', 'h1', '.product-name', '[data-title]'],
        'price': ['.price-current', '.price', '[data-price]', '.cost'],
        'image': ['img.main', '.gallery img:first-child', 'img[data-main]'],
    }
    
    def safe_extract_with_fallbacks(self, field: str, soup: BeautifulSoup) -> str:
        """Try multiple selectors until one works."""
        selectors = self.selector_fallbacks.get(field, [])
        
        for selector in selectors:
            result = self.safe_extract(selector, soup)
            if result:
                return result
        
        return None
    
    def extract(self, soup: BeautifulSoup) -> dict:
        return {
            field: self.safe_extract_with_fallbacks(field, soup)
            for field in self.selector_fallbacks.keys()
        }
```

### Pattern 14: Checkpoint/Resume

**When:** Long-running scrapes that might be interrupted.

```python
import json
from pathlib import Path

class CheckpointAnt(BaseAnt):
    """Saves progress for resumable scraping."""
    
    checkpoint_file: str = 'checkpoint.json'
    
    def load_checkpoint(self) -> dict:
        """Load previous progress."""
        path = Path(self.checkpoint_file)
        
        if path.exists():
            return json.loads(path.read_text())
        
        return {'completed': [], 'pending': [], 'data': []}
    
    def save_checkpoint(self, state: dict):
        """Save current progress."""
        Path(self.checkpoint_file).write_text(json.dumps(state, indent=2))
    
    def scrape_with_checkpoint(self, urls: list) -> list:
        """Scrape URLs with checkpoint support."""
        state = self.load_checkpoint()
        
        # Filter out already completed URLs
        pending = [u for u in urls if u not in state['completed']]
        
        self.logger.info(f"Resuming: {len(state['completed'])} done, {len(pending)} pending")
        
        for url in pending:
            result = self.scrape(url)
            
            if result.success:
                state['data'].append(result.data)
            
            state['completed'].append(url)
            
            # Save checkpoint periodically
            if len(state['completed']) % 10 == 0:
                self.save_checkpoint(state)
        
        self.save_checkpoint(state)
        return state['data']
```

### Pattern 15: Circuit Breaker

**When:** Prevent cascading failures when site is down.

```python
import time

class CircuitBreaker:
    """Circuit breaker for fault tolerance."""
    
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
    
    def record_success(self):
        self.failures = 0
        self.state = 'closed'
    
    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.failures >= self.failure_threshold:
            self.state = 'open'
    
    def can_execute(self) -> bool:
        if self.state == 'closed':
            return True
        
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = 'half-open'
                return True
            return False
        
        # half-open: allow one request
        return True


class CircuitBreakerAnt(BaseAnt):
    """Ant with circuit breaker protection."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.circuit = CircuitBreaker()
    
    def scrape(self, url: str) -> ScrapeResult:
        if not self.circuit.can_execute():
            return ScrapeResult(
                success=False,
                url=url,
                error="Circuit breaker open - site appears down"
            )
        
        result = super().scrape(url)
        
        if result.success:
            self.circuit.record_success()
        else:
            self.circuit.record_failure()
        
        return result
```

---

## Summary

| Pattern | Use When |
|---------|----------|
| **Simple Request** | Static HTML, no JS |
| **Session Management** | Login, cookies needed |
| **Browser Rendering** | JavaScript content |
| **API Consumption** | JSON APIs |
| **Page Pagination** | Numbered pages |
| **Cursor Pagination** | Token-based pagination |
| **Infinite Scroll** | Scroll-triggered loading |
| **Category Crawling** | Hierarchical structure |
| **List→Detail** | Two-phase extraction |
| **Nested Data** | Hierarchical JSON/HTML |
| **Table Extraction** | HTML tables |
| **Retry Backoff** | Transient failures |
| **Fallback Selectors** | Changing site structure |
| **Checkpoint/Resume** | Long-running jobs |
| **Circuit Breaker** | Site reliability issues |

---

*Next: [03_output_formats.md](03_output_formats.md) - Structuring your scraped data*
