# Error Handling

> **Building Resilient Scrapers That Don't Break**

Web scraping is inherently unreliable. Sites change, connections fail, and unexpected data appears. This document covers strategies for building scrapers that handle errors gracefully.

---

## Error Categories

```
┌─────────────────────────────────────────────────────────────────┐
│                    SCRAPING ERROR TAXONOMY                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  NETWORK ERRORS                                                 │
│  ├── Connection timeout                                         │
│  ├── DNS resolution failure                                     │
│  ├── Connection refused                                         │
│  └── SSL/TLS errors                                             │
│                                                                 │
│  HTTP ERRORS                                                    │
│  ├── 4xx Client errors (400, 403, 404, 429)                     │
│  ├── 5xx Server errors (500, 502, 503)                          │
│  └── Redirect loops                                             │
│                                                                 │
│  PARSING ERRORS                                                 │
│  ├── Invalid HTML/JSON                                          │
│  ├── Missing expected elements                                  │
│  ├── Encoding issues                                            │
│  └── Empty responses                                            │
│                                                                 │
│  EXTRACTION ERRORS                                              │
│  ├── Selector not found                                         │
│  ├── Wrong data type                                            │
│  ├── Unexpected structure                                       │
│  └── Validation failures                                        │
│                                                                 │
│  BLOCKING ERRORS                                                │
│  ├── CAPTCHA challenges                                         │
│  ├── IP blocks                                                  │
│  ├── Rate limiting                                              │
│  └── Access denied                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Custom Exception Hierarchy

```python
class ScrapingError(Exception):
    """Base exception for all scraping errors."""
    
    def __init__(self, message: str, url: str = None, details: dict = None):
        self.message = message
        self.url = url
        self.details = details or {}
        super().__init__(self.message)


# Network Errors
class NetworkError(ScrapingError):
    """Network-level failures."""
    pass

class TimeoutError(NetworkError):
    """Request timed out."""
    pass

class ConnectionError(NetworkError):
    """Failed to connect to server."""
    pass


# HTTP Errors
class HTTPError(ScrapingError):
    """HTTP response errors."""
    
    def __init__(self, message: str, status_code: int, **kwargs):
        self.status_code = status_code
        super().__init__(message, **kwargs)

class NotFoundError(HTTPError):
    """404 - Page not found."""
    pass

class ForbiddenError(HTTPError):
    """403 - Access forbidden."""
    pass

class RateLimitError(HTTPError):
    """429 - Too many requests."""
    
    def __init__(self, message: str, retry_after: int = None, **kwargs):
        self.retry_after = retry_after
        super().__init__(message, status_code=429, **kwargs)

class ServerError(HTTPError):
    """5xx - Server errors."""
    pass


# Parsing/Extraction Errors
class ParsingError(ScrapingError):
    """Failed to parse response."""
    pass

class ExtractionError(ScrapingError):
    """Failed to extract expected data."""
    pass

class ValidationError(ScrapingError):
    """Data validation failed."""
    pass


# Blocking Errors
class BlockedError(ScrapingError):
    """Request was blocked."""
    pass

class CaptchaError(BlockedError):
    """CAPTCHA challenge detected."""
    pass

class IPBlockedError(BlockedError):
    """IP address is blocked."""
    pass
```

---

## Error Detection

### HTTP Status Code Handling

```python
def handle_response(response: requests.Response, url: str) -> None:
    """Check response and raise appropriate errors."""
    
    status = response.status_code
    
    # Success
    if 200 <= status < 300:
        return
    
    # Client errors
    if status == 400:
        raise HTTPError("Bad request", status, url=url)
    
    if status == 401:
        raise ForbiddenError("Authentication required", status, url=url)
    
    if status == 403:
        # Check if it's a block
        if is_blocked(response):
            raise BlockedError("Access blocked", url=url)
        raise ForbiddenError("Forbidden", status, url=url)
    
    if status == 404:
        raise NotFoundError("Page not found", status, url=url)
    
    if status == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        raise RateLimitError(
            "Rate limited",
            retry_after=retry_after,
            url=url
        )
    
    # Server errors
    if 500 <= status < 600:
        raise ServerError(f"Server error: {status}", status, url=url)
    
    # Other
    raise HTTPError(f"Unexpected status: {status}", status, url=url)
```

### Block Detection

```python
def is_blocked(response: requests.Response) -> bool:
    """Detect if response indicates blocking."""
    
    # Status codes
    if response.status_code in [403, 429, 503]:
        block_headers = [
            'cf-ray',  # Cloudflare
            'x-amz-cf-id',  # AWS WAF
            'x-datadome',  # DataDome
        ]
        if any(h in response.headers for h in block_headers):
            return True
    
    # Content patterns
    content = response.text[:5000].lower()
    
    block_patterns = [
        'access denied',
        'access to this page has been denied',
        'blocked',
        'captcha',
        'challenge-form',
        'checking your browser',
        'ddos protection',
        'human verification',
        'please verify you are human',
        'rate limit',
        'too many requests',
        'unusual traffic',
    ]
    
    return any(pattern in content for pattern in block_patterns)


def detect_captcha(response: requests.Response) -> bool:
    """Detect CAPTCHA challenges."""
    content = response.text.lower()
    
    captcha_patterns = [
        'g-recaptcha',
        'h-captcha',
        'captcha-container',
        'challenge-form',
        'verify you are human',
    ]
    
    return any(pattern in content for pattern in captcha_patterns)
```

---

## Retry Strategies

### Simple Retry

```python
import time
from typing import Callable, TypeVar

T = TypeVar('T')

def retry(
    func: Callable[..., T],
    max_attempts: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (Exception,)
) -> T:
    """Simple retry with fixed delay."""
    
    last_error = None
    
    for attempt in range(max_attempts):
        try:
            return func()
        except exceptions as e:
            last_error = e
            if attempt < max_attempts - 1:
                time.sleep(delay)
    
    raise last_error
```

### Exponential Backoff

```python
import time
import random
from typing import Callable, TypeVar

T = TypeVar('T')

def retry_with_backoff(
    func: Callable[..., T],
    max_attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True,
    exceptions: tuple = (Exception,),
    on_retry: Callable = None
) -> T:
    """Retry with exponential backoff and optional jitter."""
    
    last_error = None
    
    for attempt in range(max_attempts):
        try:
            return func()
        except exceptions as e:
            last_error = e
            
            if attempt < max_attempts - 1:
                # Calculate delay
                delay = min(base_delay * (2 ** attempt), max_delay)
                
                # Add jitter (±25%)
                if jitter:
                    delay = delay * (0.75 + random.random() * 0.5)
                
                # Callback
                if on_retry:
                    on_retry(attempt + 1, delay, e)
                
                time.sleep(delay)
    
    raise last_error


# Usage
def fetch_with_retry(url: str) -> str:
    def on_retry(attempt, delay, error):
        print(f"Attempt {attempt} failed: {error}. Retrying in {delay:.1f}s")
    
    return retry_with_backoff(
        lambda: requests.get(url).text,
        max_attempts=5,
        exceptions=(requests.RequestException, TimeoutError),
        on_retry=on_retry
    )
```

### Smart Retry (Error-Specific)

```python
class SmartRetry:
    """Retry strategy that adapts based on error type."""
    
    # Which errors to retry
    RETRYABLE = {
        TimeoutError: {'max_attempts': 3, 'base_delay': 5},
        ConnectionError: {'max_attempts': 3, 'base_delay': 2},
        ServerError: {'max_attempts': 5, 'base_delay': 10},
        RateLimitError: {'max_attempts': 3, 'use_retry_after': True},
    }
    
    # Which errors should not be retried
    NON_RETRYABLE = {
        NotFoundError,
        ForbiddenError,
        ValidationError,
    }
    
    def should_retry(self, error: Exception) -> bool:
        """Check if error is retryable."""
        error_type = type(error)
        
        if error_type in self.NON_RETRYABLE:
            return False
        
        return error_type in self.RETRYABLE
    
    def get_delay(self, error: Exception, attempt: int) -> float:
        """Get delay for this error type and attempt."""
        error_type = type(error)
        config = self.RETRYABLE.get(error_type, {})
        
        # Use Retry-After header if available
        if config.get('use_retry_after') and hasattr(error, 'retry_after'):
            return error.retry_after
        
        base = config.get('base_delay', 1)
        return base * (2 ** attempt)
    
    def execute(self, func: Callable, *args, **kwargs):
        """Execute function with smart retry."""
        last_error = None
        attempt = 0
        
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                
                if not self.should_retry(e):
                    raise
                
                config = self.RETRYABLE.get(type(e), {})
                max_attempts = config.get('max_attempts', 3)
                
                if attempt >= max_attempts:
                    raise
                
                delay = self.get_delay(e, attempt)
                time.sleep(delay)
                attempt += 1
```

---

## Graceful Degradation

### Partial Success Pattern

```python
from dataclasses import dataclass
from typing import List, Optional, Any

@dataclass
class FieldResult:
    """Result of extracting a single field."""
    success: bool
    value: Any = None
    error: Optional[str] = None

class GracefulExtractor:
    """Extracts data with per-field error handling."""
    
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
        self.errors = []
    
    def extract_field(
        self,
        name: str,
        selector: str,
        required: bool = False,
        transform: Callable = None,
        default: Any = None
    ) -> Any:
        """Extract field with error handling."""
        
        try:
            element = self.soup.select_one(selector)
            
            if element is None:
                if required:
                    self.errors.append(f"Required field '{name}' not found")
                return default
            
            value = element.get_text(strip=True)
            
            if transform:
                value = transform(value)
            
            return value
            
        except Exception as e:
            self.errors.append(f"Error extracting '{name}': {e}")
            return default
    
    def extract(self, fields: dict) -> dict:
        """Extract multiple fields."""
        result = {}
        
        for name, config in fields.items():
            if isinstance(config, str):
                # Simple selector
                result[name] = self.extract_field(name, config)
            else:
                # Config dict
                result[name] = self.extract_field(name, **config)
        
        return result
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0


# Usage
def extract_product(soup: BeautifulSoup) -> dict:
    extractor = GracefulExtractor(soup)
    
    data = extractor.extract({
        'title': {'selector': 'h1', 'required': True},
        'price': {
            'selector': '.price',
            'transform': parse_price,
            'default': None
        },
        'description': '.description',
        'stock': {
            'selector': '.stock-status',
            'default': 'unknown'
        }
    })
    
    if extractor.has_errors:
        data['_extraction_errors'] = extractor.errors
    
    return data
```

### Fallback Chain

```python
class FallbackChain:
    """Try multiple extraction strategies until one works."""
    
    def __init__(self):
        self.strategies = []
    
    def add(self, strategy: Callable, name: str = None):
        """Add a strategy to the chain."""
        self.strategies.append({
            'name': name or f'strategy_{len(self.strategies)}',
            'func': strategy
        })
        return self
    
    def execute(self, *args, **kwargs) -> tuple:
        """Execute strategies until one succeeds."""
        errors = []
        
        for strategy in self.strategies:
            try:
                result = strategy['func'](*args, **kwargs)
                
                if result is not None:
                    return result, strategy['name'], None
                    
            except Exception as e:
                errors.append({
                    'strategy': strategy['name'],
                    'error': str(e)
                })
        
        return None, None, errors


# Usage
def extract_price(soup: BeautifulSoup):
    chain = FallbackChain()
    
    chain.add(
        lambda s: s.select_one('.price-current').text,
        'primary_selector'
    )
    chain.add(
        lambda s: s.select_one('[data-price]')['data-price'],
        'data_attribute'
    )
    chain.add(
        lambda s: s.select_one('.product-price span').text,
        'nested_selector'
    )
    
    price, strategy_used, errors = chain.execute(soup)
    
    if price:
        return parse_price(price)
    return None
```

---

## Error Logging & Reporting

### Structured Error Logging

```python
import logging
import json
from datetime import datetime

class ScrapingLogger:
    """Structured logging for scraping operations."""
    
    def __init__(self, name: str, log_file: str = None):
        self.logger = logging.getLogger(name)
        self.errors = []
        
        if log_file:
            handler = logging.FileHandler(log_file)
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(handler)
    
    def log_request(self, url: str, status: int, duration_ms: float):
        """Log a request."""
        self.logger.info(json.dumps({
            'event': 'request',
            'url': url,
            'status': status,
            'duration_ms': duration_ms,
            'timestamp': datetime.utcnow().isoformat()
        }))
    
    def log_error(
        self,
        error: Exception,
        url: str = None,
        context: dict = None
    ):
        """Log an error with context."""
        error_data = {
            'event': 'error',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'url': url,
            'context': context,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.errors.append(error_data)
        self.logger.error(json.dumps(error_data))
    
    def log_extraction_error(
        self,
        field: str,
        selector: str,
        url: str,
        error: Exception
    ):
        """Log extraction-specific error."""
        self.log_error(error, url, {
            'field': field,
            'selector': selector
        })
    
    def get_error_summary(self) -> dict:
        """Get summary of errors."""
        from collections import Counter
        
        error_types = Counter(e['error_type'] for e in self.errors)
        
        return {
            'total_errors': len(self.errors),
            'by_type': dict(error_types),
            'sample_errors': self.errors[:10]
        }
```

### Error Aggregation

```python
from collections import defaultdict
from typing import List, Dict

class ErrorAggregator:
    """Aggregate and analyze scraping errors."""
    
    def __init__(self):
        self.errors: List[Dict] = []
        self.by_url: Dict[str, List] = defaultdict(list)
        self.by_type: Dict[str, List] = defaultdict(list)
    
    def add(self, error: Exception, url: str = None, **context):
        """Record an error."""
        error_data = {
            'type': type(error).__name__,
            'message': str(error),
            'url': url,
            'context': context,
            'timestamp': datetime.utcnow()
        }
        
        self.errors.append(error_data)
        
        if url:
            self.by_url[url].append(error_data)
        
        self.by_type[error_data['type']].append(error_data)
    
    def get_problem_urls(self, threshold: int = 3) -> List[str]:
        """Get URLs with multiple errors."""
        return [
            url for url, errors in self.by_url.items()
            if len(errors) >= threshold
        ]
    
    def get_common_errors(self, top_n: int = 5) -> List[tuple]:
        """Get most common error types."""
        return sorted(
            self.by_type.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:top_n]
    
    def report(self) -> dict:
        """Generate error report."""
        return {
            'total_errors': len(self.errors),
            'unique_urls_with_errors': len(self.by_url),
            'error_types': {k: len(v) for k, v in self.by_type.items()},
            'problem_urls': self.get_problem_urls(),
            'most_common': [
                {'type': t, 'count': len(e)}
                for t, e in self.get_common_errors()
            ]
        }
```

---

## Putting It All Together

```python
class ResilientAnt(BaseAnt):
    """Ant with comprehensive error handling."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.retry = SmartRetry()
        self.error_aggregator = ErrorAggregator()
        self.scraping_logger = ScrapingLogger(self.name)
    
    def scrape(self, url: str) -> ScrapeResult:
        """Scrape with full error handling."""
        start = time.time()
        
        try:
            # Fetch with smart retry
            response = self.retry.execute(self._fetch, url)
            
            # Check for blocks
            if is_blocked(response):
                raise BlockedError("Request blocked", url=url)
            
            if detect_captcha(response):
                raise CaptchaError("CAPTCHA detected", url=url)
            
            # Parse
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract with graceful degradation
            data = self._extract_gracefully(soup, url)
            
            duration = (time.time() - start) * 1000
            self.scraping_logger.log_request(url, response.status_code, duration)
            
            return ScrapeResult(
                success=True,
                url=url,
                data=data,
                duration_ms=duration
            )
            
        except ScrapingError as e:
            self.error_aggregator.add(e, url)
            self.scraping_logger.log_error(e, url)
            
            return ScrapeResult(
                success=False,
                url=url,
                error=str(e),
                duration_ms=(time.time() - start) * 1000
            )
    
    def _extract_gracefully(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract with per-field error handling."""
        extractor = GracefulExtractor(soup)
        
        data = extractor.extract(self.field_config)
        
        # Log any extraction errors
        for error in extractor.errors:
            self.scraping_logger.log_error(
                ExtractionError(error),
                url
            )
        
        return data
    
    def get_health_report(self) -> dict:
        """Get scraper health report."""
        return {
            'metrics': self.metrics.__dict__,
            'errors': self.error_aggregator.report()
        }
```

---

## Summary

| Strategy | Use When |
|----------|----------|
| **Simple Retry** | Transient network issues |
| **Exponential Backoff** | Rate limiting, server overload |
| **Smart Retry** | Mixed error types |
| **Graceful Degradation** | Partial data is acceptable |
| **Fallback Chain** | Multiple extraction strategies |
| **Circuit Breaker** | Protect against down sites |

### Key Principles

1. **Categorize errors** - Different errors need different handling
2. **Retry intelligently** - Not all errors are retryable
3. **Fail gracefully** - Partial success is better than total failure
4. **Log everything** - Debug later, don't block now
5. **Aggregate and analyze** - Find patterns in failures

---

*Next: [05_templates/](05_templates/) - Ready-to-use ant templates*
