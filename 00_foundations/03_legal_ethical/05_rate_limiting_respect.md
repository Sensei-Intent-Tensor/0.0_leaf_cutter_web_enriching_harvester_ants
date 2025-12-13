# Rate Limiting Respect

> **Being a Good Citizen of the Web**

Respectful rate limiting is where ethics meets practice. This document covers how to scrape responsibly without harming the websites you access.

---

## Why Rate Limiting Matters

### Server Impact

```
Website Server Capacity
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Normal users:     ████████░░░░░░░░░░░  40% capacity
Background tasks: ██░░░░░░░░░░░░░░░░░  10% capacity
Safety margin:    ░░░░░░░░░░░░░░░░░░░  50% headroom

With aggressive scraper:
Normal users:     ████████░░░░░░░░░░░  40% capacity
Background tasks: ██░░░░░░░░░░░░░░░░░  10% capacity
YOUR SCRAPER:     ██████████████████░  90% capacity
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESULT: 140% = Site crashes or slows for everyone
```

### Real Costs

Every request has a cost:
- **Bandwidth**: Data transfer fees
- **Compute**: Server processing
- **Database**: Query overhead
- **CDN**: Cache misses
- **Monitoring**: Alerting overhead

Small sites can face real bills from aggressive scraping.

---

## Determining Appropriate Rates

### Signals to Consider

| Signal | What It Tells You |
|--------|-------------------|
| **robots.txt Crawl-delay** | Explicit request from site |
| **Response time** | Server health |
| **429 responses** | You're too fast |
| **503 responses** | Server overloaded |
| **Rate limit headers** | Explicit limits |
| **Site size** | Small = go slower |
| **Time of day** | Peak hours = slower |

### Default Rate Recommendations

```python
RATE_GUIDELINES = {
    'small_site': {
        'description': 'Personal blogs, small businesses',
        'requests_per_second': 0.1,  # 1 every 10 seconds
        'concurrent': 1
    },
    'medium_site': {
        'description': 'Medium businesses, popular blogs',
        'requests_per_second': 0.5,  # 1 every 2 seconds
        'concurrent': 1
    },
    'large_site': {
        'description': 'Major websites with infrastructure',
        'requests_per_second': 2.0,
        'concurrent': 2
    },
    'api_with_limits': {
        'description': 'APIs with documented rate limits',
        'requests_per_second': 'Use 80% of stated limit',
        'concurrent': 'As allowed'
    },
    'unknown': {
        'description': 'When in doubt',
        'requests_per_second': 0.2,  # 1 every 5 seconds
        'concurrent': 1
    }
}
```

### Reading Rate Limit Headers

```python
def extract_rate_limits(response):
    """Extract rate limiting info from response headers."""
    
    headers = response.headers
    
    limits = {
        'limit': None,
        'remaining': None,
        'reset': None,
        'retry_after': None
    }
    
    # Standard headers
    limit_headers = [
        'X-RateLimit-Limit',
        'X-Rate-Limit-Limit',
        'RateLimit-Limit'
    ]
    for h in limit_headers:
        if h in headers:
            limits['limit'] = int(headers[h])
            break
    
    remaining_headers = [
        'X-RateLimit-Remaining',
        'X-Rate-Limit-Remaining',
        'RateLimit-Remaining'
    ]
    for h in remaining_headers:
        if h in headers:
            limits['remaining'] = int(headers[h])
            break
    
    reset_headers = [
        'X-RateLimit-Reset',
        'X-Rate-Limit-Reset',
        'RateLimit-Reset'
    ]
    for h in reset_headers:
        if h in headers:
            limits['reset'] = int(headers[h])
            break
    
    if 'Retry-After' in headers:
        limits['retry_after'] = int(headers['Retry-After'])
    
    return limits
```

---

## Implementation Patterns

### Pattern 1: Simple Delay

```python
import time
import random

def respectful_scrape(urls, min_delay=1.0, max_delay=3.0):
    """Scrape with random delays between requests."""
    
    results = []
    for url in urls:
        response = requests.get(url)
        results.append(response)
        
        # Random delay (more human-like)
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    return results
```

### Pattern 2: Adaptive Rate Limiting

```python
class AdaptiveRateLimiter:
    """Adjusts rate based on server responses."""
    
    def __init__(self, initial_delay=1.0):
        self.delay = initial_delay
        self.min_delay = 0.5
        self.max_delay = 30.0
        self.last_request = 0
        self.consecutive_errors = 0
    
    def wait(self):
        """Wait appropriate time before next request."""
        elapsed = time.time() - self.last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request = time.time()
    
    def success(self, response):
        """Update based on successful response."""
        self.consecutive_errors = 0
        
        # Check if we can speed up
        limits = extract_rate_limits(response)
        if limits['remaining'] and limits['remaining'] > 50:
            self.delay = max(self.min_delay, self.delay * 0.9)
    
    def error(self, response):
        """Update based on error response."""
        self.consecutive_errors += 1
        
        if response.status_code == 429:
            # Rate limited - back off significantly
            retry_after = int(response.headers.get('Retry-After', 60))
            self.delay = min(self.max_delay, retry_after)
            time.sleep(retry_after)
        
        elif response.status_code in [500, 502, 503]:
            # Server issues - back off
            self.delay = min(self.max_delay, self.delay * 2)
        
        # Exponential backoff for consecutive errors
        if self.consecutive_errors > 3:
            self.delay = min(self.max_delay, self.delay * 1.5)
```

### Pattern 3: Domain-Aware Rate Limiting

```python
from collections import defaultdict
from urllib.parse import urlparse
import threading

class DomainRateLimiter:
    """Separate rate limits per domain."""
    
    def __init__(self, default_delay=1.0):
        self.default_delay = default_delay
        self.domain_delays = {}
        self.last_requests = defaultdict(float)
        self.locks = defaultdict(threading.Lock)
    
    def set_delay(self, domain, delay):
        """Set custom delay for specific domain."""
        self.domain_delays[domain] = delay
    
    def get_delay(self, domain):
        """Get delay for domain."""
        return self.domain_delays.get(domain, self.default_delay)
    
    def wait(self, url):
        """Wait before making request to URL."""
        domain = urlparse(url).netloc
        delay = self.get_delay(domain)
        
        with self.locks[domain]:
            elapsed = time.time() - self.last_requests[domain]
            if elapsed < delay:
                time.sleep(delay - elapsed)
            self.last_requests[domain] = time.time()

# Usage
limiter = DomainRateLimiter(default_delay=2.0)
limiter.set_delay('api.fast-site.com', 0.5)  # Fast API
limiter.set_delay('slow-blog.com', 5.0)       # Small site

for url in urls:
    limiter.wait(url)
    response = requests.get(url)
```

### Pattern 4: Time-of-Day Awareness

```python
from datetime import datetime, time as dt_time

class TimeAwareRateLimiter:
    """Slower during peak hours."""
    
    def __init__(self, base_delay=1.0):
        self.base_delay = base_delay
    
    def get_delay(self, timezone='UTC'):
        """Get delay based on time of day."""
        hour = datetime.utcnow().hour
        
        # Peak hours (9 AM - 6 PM) - go slower
        if 9 <= hour <= 18:
            return self.base_delay * 2
        
        # Off-peak - can be faster
        return self.base_delay
    
    def wait(self):
        time.sleep(self.get_delay())
```

---

## Handling 429 Responses

### Basic Handler

```python
def handle_429(response, attempt=1, max_attempts=5):
    """Handle rate limit response."""
    
    if attempt >= max_attempts:
        raise Exception("Max retry attempts exceeded")
    
    # Get retry delay
    retry_after = response.headers.get('Retry-After')
    
    if retry_after:
        if retry_after.isdigit():
            wait_time = int(retry_after)
        else:
            # HTTP date format
            from email.utils import parsedate_to_datetime
            retry_date = parsedate_to_datetime(retry_after)
            wait_time = (retry_date - datetime.utcnow()).total_seconds()
    else:
        # Exponential backoff
        wait_time = 60 * (2 ** (attempt - 1))
    
    print(f"Rate limited. Waiting {wait_time}s (attempt {attempt})")
    time.sleep(wait_time)
    
    return wait_time
```

### Automatic Retry

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_respectful_session():
    """Create session with automatic retry on rate limits."""
    
    session = requests.Session()
    
    retry_strategy = Retry(
        total=5,
        backoff_factor=2,  # 2, 4, 8, 16, 32 seconds
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
        respect_retry_after_header=True
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session
```

---

## Monitoring Your Impact

### Track Your Requests

```python
import logging
from collections import Counter
from datetime import datetime

class RequestMonitor:
    """Monitor scraping impact."""
    
    def __init__(self):
        self.requests = []
        self.errors = Counter()
        self.domains = Counter()
    
    def log_request(self, url, response):
        domain = urlparse(url).netloc
        self.domains[domain] += 1
        
        self.requests.append({
            'url': url,
            'status': response.status_code,
            'time': datetime.now(),
            'response_time': response.elapsed.total_seconds()
        })
        
        if response.status_code >= 400:
            self.errors[response.status_code] += 1
    
    def report(self):
        print(f"Total requests: {len(self.requests)}")
        print(f"Domains accessed: {dict(self.domains)}")
        print(f"Errors: {dict(self.errors)}")
        
        if self.requests:
            avg_time = sum(r['response_time'] for r in self.requests) / len(self.requests)
            print(f"Average response time: {avg_time:.2f}s")
        
        # Warning signs
        if self.errors.get(429, 0) > 0:
            print("⚠️ Rate limited - slow down!")
        if self.errors.get(503, 0) > 0:
            print("⚠️ Server issues - consider stopping")
```

### Response Time Tracking

```python
def check_server_health(response_times, threshold=2.0):
    """Check if server is struggling based on response times."""
    
    if len(response_times) < 5:
        return True  # Not enough data
    
    recent = response_times[-10:]
    avg_recent = sum(recent) / len(recent)
    
    baseline = response_times[:10]
    avg_baseline = sum(baseline) / len(baseline)
    
    # If recent requests are much slower, server may be struggling
    if avg_recent > avg_baseline * threshold:
        print(f"⚠️ Response times increasing: {avg_baseline:.2f}s → {avg_recent:.2f}s")
        return False
    
    return True
```

---

## Best Practices Checklist

### Before Scraping

- [ ] Check robots.txt for Crawl-delay
- [ ] Research any documented rate limits
- [ ] Start with conservative rates
- [ ] Plan for off-peak hours if possible

### During Scraping

- [ ] Monitor response times
- [ ] Track error rates
- [ ] Respect 429 responses
- [ ] Adjust rates if site seems slow

### If Problems Occur

- [ ] Stop immediately if 503s increase
- [ ] Double delay after any 429
- [ ] Consider contacting site owner
- [ ] Document the issue

---

## Summary

| Situation | Recommended Rate | Rationale |
|-----------|------------------|-----------|
| Unknown site | 1 req/5 sec | Conservative default |
| Small/personal site | 1 req/10 sec | Minimal impact |
| Medium site | 1 req/2 sec | Reasonable balance |
| Large site | 2-5 req/sec | Has infrastructure |
| API with limits | 80% of limit | Leave headroom |
| Receiving 429s | Stop + backoff | Respect the signal |
| Response time increasing | Slow down 50% | Server is struggling |

### Key Takeaways

1. **Start slow** - You can always speed up
2. **Watch the signals** - Response times, error rates
3. **Respect 429s** - They're telling you something
4. **Be adaptive** - Adjust based on feedback
5. **Consider the operator** - Your traffic has real costs

---

*This completes the Legal & Ethical section. Next: [../04_tools_ecosystem/](../04_tools_ecosystem/) - Tools and libraries*
