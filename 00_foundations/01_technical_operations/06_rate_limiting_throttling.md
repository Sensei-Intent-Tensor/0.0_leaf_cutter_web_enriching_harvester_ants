# Rate Limiting & Throttling

> **The Art of Not Getting Blocked**

Scraping too fast will get you blocked. Too slow wastes time. This document covers how rate limiting works and how to find the optimal speed.

---

## Why Rate Limiting Matters

### From the Website's Perspective

```
Normal traffic:    ▪️ ▪️ ▪️ ▪️ ▪️ ▪️ ▪️ ▪️       (spread out)
Scraper traffic:   ▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️ (hammering)
```

Aggressive scraping:
- Overloads servers
- Increases hosting costs
- Degrades experience for real users
- Looks like a DDoS attack

### From Your Perspective

| Scraping Speed | Result |
|----------------|--------|
| Way too fast | Immediate IP ban |
| Too fast | Rate limited (429s), eventual ban |
| Optimal | Sustained access, good throughput |
| Too slow | Wasted time, same data |

---

## 1. Understanding Rate Limits

### How Sites Implement Rate Limits

```
                     ┌─────────────────┐
Request ───────────▶ │  Rate Limiter   │ ───────▶ Server
                     │                 │
                     │  Counter: 95    │
                     │  Window: 60s    │
                     │  Limit: 100     │
                     └─────────────────┘
                            │
                     If counter > limit:
                     Return 429 Too Many Requests
```

### Common Rate Limit Strategies

| Strategy | How It Works | Example |
|----------|--------------|---------|
| **Fixed Window** | X requests per minute/hour | 100 req/min |
| **Sliding Window** | X requests in rolling window | 100 req in last 60s |
| **Token Bucket** | Tokens regenerate over time | 10 tokens/sec |
| **Leaky Bucket** | Requests drain at fixed rate | 5 req/sec max |
| **Concurrent Limit** | Max simultaneous connections | 10 parallel |

### Rate Limit Headers

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705312800

-- OR for 429 --

HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1705312800
```

---

## 2. Basic Throttling

### Simple Delay

```python
import time
import requests

def scrape_with_delay(urls, delay=1.0):
    results = []
    for url in urls:
        response = requests.get(url)
        results.append(response)
        time.sleep(delay)  # Wait between requests
    return results
```

### Random Delay (More Natural)

```python
import random
import time

def scrape_with_random_delay(urls, min_delay=0.5, max_delay=2.0):
    results = []
    for url in urls:
        response = requests.get(url)
        results.append(response)
        
        # Random delay looks more human
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    return results
```

### Exponential Backoff on Errors

```python
import time
import random
import requests

def fetch_with_backoff(url, max_retries=5):
    for attempt in range(max_retries):
        response = requests.get(url)
        
        if response.status_code == 200:
            return response
        
        if response.status_code == 429:  # Rate limited
            # Get retry delay from header, or calculate
            retry_after = int(response.headers.get("Retry-After", 0))
            if retry_after:
                wait_time = retry_after
            else:
                # Exponential backoff: 1, 2, 4, 8, 16...
                wait_time = (2 ** attempt) + random.uniform(0, 1)
            
            print(f"Rate limited. Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
        
        elif response.status_code >= 500:  # Server error
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            print(f"Server error. Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
        
        else:
            return response
    
    raise Exception(f"Failed after {max_retries} retries")
```

---

## 3. Rate Limiter Class

### Token Bucket Implementation

```python
import time
import threading

class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, rate, burst=None):
        """
        Args:
            rate: Requests per second
            burst: Maximum burst size (default: rate)
        """
        self.rate = rate
        self.burst = burst or rate
        self.tokens = self.burst
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def acquire(self):
        """Wait until a request can be made."""
        with self.lock:
            now = time.time()
            
            # Add tokens based on time passed
            elapsed = now - self.last_update
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return 0  # No wait needed
            
            # Calculate wait time
            wait_time = (1 - self.tokens) / self.rate
            return wait_time
    
    def wait(self):
        """Blocking wait until rate limit allows."""
        wait_time = self.acquire()
        if wait_time > 0:
            time.sleep(wait_time)

# Usage
limiter = RateLimiter(rate=2)  # 2 requests per second

for url in urls:
    limiter.wait()  # Blocks if needed
    response = requests.get(url)
```

### Per-Domain Rate Limiter

```python
from collections import defaultdict
import time
from urllib.parse import urlparse

class DomainRateLimiter:
    """Rate limit per domain."""
    
    def __init__(self, default_rate=1.0, domain_rates=None):
        """
        Args:
            default_rate: Requests per second for unknown domains
            domain_rates: Dict of domain -> rate
        """
        self.default_rate = default_rate
        self.domain_rates = domain_rates or {}
        self.last_request = defaultdict(float)
    
    def wait(self, url):
        domain = urlparse(url).netloc
        rate = self.domain_rates.get(domain, self.default_rate)
        min_interval = 1.0 / rate
        
        elapsed = time.time() - self.last_request[domain]
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        
        self.last_request[domain] = time.time()

# Usage
limiter = DomainRateLimiter(
    default_rate=1.0,  # 1 req/sec default
    domain_rates={
        "api.example.com": 5.0,   # 5 req/sec for API
        "slow-site.com": 0.5,     # 1 req per 2 seconds
    }
)

for url in urls:
    limiter.wait(url)
    response = requests.get(url)
```

---

## 4. Adaptive Rate Limiting

### Adjust Based on Response

```python
class AdaptiveRateLimiter:
    """Automatically adjust rate based on responses."""
    
    def __init__(self, initial_rate=2.0, min_rate=0.1, max_rate=10.0):
        self.rate = initial_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.last_request = 0
        self.consecutive_success = 0
        self.consecutive_errors = 0
    
    def wait(self):
        interval = 1.0 / self.rate
        elapsed = time.time() - self.last_request
        if elapsed < interval:
            time.sleep(interval - elapsed)
        self.last_request = time.time()
    
    def success(self):
        """Call after successful request."""
        self.consecutive_success += 1
        self.consecutive_errors = 0
        
        # Speed up after consistent success
        if self.consecutive_success >= 10:
            self.rate = min(self.max_rate, self.rate * 1.2)
            self.consecutive_success = 0
            print(f"Rate increased to {self.rate:.1f} req/s")
    
    def rate_limited(self, retry_after=None):
        """Call when rate limited (429)."""
        self.consecutive_success = 0
        self.consecutive_errors += 1
        
        # Slow down significantly
        self.rate = max(self.min_rate, self.rate * 0.5)
        print(f"Rate limited! Decreased to {self.rate:.1f} req/s")
        
        if retry_after:
            time.sleep(retry_after)
    
    def error(self):
        """Call on other errors."""
        self.consecutive_success = 0
        self.consecutive_errors += 1
        
        if self.consecutive_errors >= 3:
            self.rate = max(self.min_rate, self.rate * 0.8)
            print(f"Multiple errors. Rate now {self.rate:.1f} req/s")

# Usage
limiter = AdaptiveRateLimiter(initial_rate=2.0)

for url in urls:
    limiter.wait()
    response = requests.get(url)
    
    if response.status_code == 200:
        limiter.success()
    elif response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 30))
        limiter.rate_limited(retry_after)
    else:
        limiter.error()
```

---

## 5. Concurrent Throttling

### Async with Rate Limiting

```python
import asyncio
import aiohttp
from asyncio import Semaphore

class AsyncRateLimiter:
    def __init__(self, rate):
        self.rate = rate
        self.interval = 1.0 / rate
        self.last_request = 0
        self.lock = asyncio.Lock()
    
    async def wait(self):
        async with self.lock:
            now = asyncio.get_event_loop().time()
            elapsed = now - self.last_request
            if elapsed < self.interval:
                await asyncio.sleep(self.interval - elapsed)
            self.last_request = asyncio.get_event_loop().time()

async def scrape_with_async_rate_limit(urls, rate=5, max_concurrent=10):
    limiter = AsyncRateLimiter(rate)
    semaphore = Semaphore(max_concurrent)
    
    async def fetch(session, url):
        async with semaphore:
            await limiter.wait()
            async with session.get(url) as response:
                return await response.text()
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)

# Usage
results = asyncio.run(scrape_with_async_rate_limit(urls, rate=5))
```

### Threading with Rate Limit

```python
from concurrent.futures import ThreadPoolExecutor
import threading
import time

class ThreadSafeRateLimiter:
    def __init__(self, rate):
        self.interval = 1.0 / rate
        self.last_request = 0
        self.lock = threading.Lock()
    
    def wait(self):
        with self.lock:
            now = time.time()
            wait_time = self.last_request + self.interval - now
            if wait_time > 0:
                time.sleep(wait_time)
            self.last_request = time.time()

limiter = ThreadSafeRateLimiter(rate=5)

def fetch(url):
    limiter.wait()
    return requests.get(url)

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(fetch, urls))
```

---

## 6. Respecting robots.txt

### Crawl-Delay Directive

```
# robots.txt
User-agent: *
Crawl-delay: 10  # Wait 10 seconds between requests
```

### Parsing robots.txt

```python
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

def get_crawl_delay(url):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    
    rp = RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    
    # Get crawl delay for our bot
    delay = rp.crawl_delay("*")
    return delay or 0

# Usage
delay = get_crawl_delay("https://example.com/")
time.sleep(delay)
```

---

## 7. Handling 429 Responses

### Basic 429 Handler

```python
def request_with_retry(url, session=None, max_retries=3):
    client = session or requests
    
    for attempt in range(max_retries):
        response = client.get(url)
        
        if response.status_code != 429:
            return response
        
        # Parse retry information
        retry_after = response.headers.get("Retry-After")
        
        if retry_after:
            if retry_after.isdigit():
                wait = int(retry_after)
            else:
                # HTTP date format
                from email.utils import parsedate_to_datetime
                retry_time = parsedate_to_datetime(retry_after)
                wait = (retry_time - datetime.now()).total_seconds()
        else:
            wait = 60  # Default wait
        
        print(f"429 received. Waiting {wait}s...")
        time.sleep(wait)
    
    raise Exception("Max retries exceeded")
```

### Using requests Retry Adapter

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retry():
    session = requests.Session()
    
    retries = Retry(
        total=5,
        backoff_factor=1,  # 0, 1, 2, 4, 8 seconds
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
        respect_retry_after_header=True,  # Honor Retry-After
    )
    
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

session = create_session_with_retry()
response = session.get(url)  # Automatically retries on 429
```

---

## 8. Finding the Right Rate

### Method 1: Start Slow, Speed Up

```python
# Start conservative, increase until 429s appear
rates_to_test = [0.5, 1, 2, 3, 5, 10]

for rate in rates_to_test:
    limiter = RateLimiter(rate)
    errors = 0
    
    for url in test_urls[:20]:
        limiter.wait()
        response = requests.get(url)
        if response.status_code == 429:
            errors += 1
    
    print(f"Rate {rate}: {errors} rate limits")
    if errors > 0:
        optimal_rate = rates_to_test[rates_to_test.index(rate) - 1]
        print(f"Optimal rate: {optimal_rate}")
        break
```

### Method 2: Check Headers

```python
def determine_rate_from_headers(response):
    limit = int(response.headers.get("X-RateLimit-Limit", 0))
    reset = int(response.headers.get("X-RateLimit-Reset", 0))
    
    if limit and reset:
        window = reset - time.time()
        if window > 0:
            rate = limit / window
            # Use 80% of allowed rate as safety margin
            return rate * 0.8
    
    return None
```

### Method 3: Honor robots.txt

```python
def get_safe_rate(domain):
    # Check robots.txt first
    crawl_delay = get_crawl_delay(f"https://{domain}/")
    if crawl_delay:
        return 1.0 / crawl_delay
    
    # Default conservative rates by site type
    default_rates = {
        "api": 5.0,      # APIs usually faster
        "search": 0.5,   # Search pages often protected
        "default": 1.0,  # 1 req/sec is safe default
    }
    
    return default_rates.get("default")
```

---

## 9. Rate Limit Best Practices

### DO

✅ Start slow and speed up gradually
✅ Use random delays (looks more human)
✅ Respect Retry-After headers
✅ Implement exponential backoff
✅ Honor robots.txt crawl-delay
✅ Monitor for 429 responses
✅ Different rates for different endpoints

### DON'T

❌ Hammer sites with parallel requests from start
❌ Ignore rate limit responses
❌ Use fixed, predictable intervals
❌ Retry immediately after 429
❌ Assume all pages can be hit at same rate

---

## Summary

| Technique | Use Case | Complexity |
|-----------|----------|------------|
| **Simple delay** | Quick scripts | Low |
| **Random delay** | Better disguise | Low |
| **Token bucket** | Precise control | Medium |
| **Per-domain** | Multi-site scraping | Medium |
| **Adaptive** | Unknown rate limits | High |
| **Async + rate limit** | High throughput | High |

### Quick Reference

```python
# Conservative default
time.sleep(random.uniform(1, 3))

# API scraping
rate_limiter = RateLimiter(rate=5)  # 5 req/sec

# Aggressive (if allowed)
rate_limiter = RateLimiter(rate=20, burst=50)

# Unknown site
adaptive_limiter = AdaptiveRateLimiter(initial_rate=1.0)
```

---

*Next: [07_proxies_rotation_ips.md](07_proxies_rotation_ips.md) - Managing IP addresses and proxies*
