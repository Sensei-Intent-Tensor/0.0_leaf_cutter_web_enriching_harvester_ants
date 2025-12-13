# Rate Limiting & Throttling

> **The Art of Being a Polite Scraper**

Rate limiting is how websites protect themselves from being overwhelmed. Understanding and respecting these limits is both ethically important and practically necessary—aggressive scrapers get blocked.

---

## Why Rate Limiting Matters

### For the Website

```
Without Rate Limiting:
┌─────────────┐     1000 req/sec     ┌─────────────┐
│   Scraper   │─────────────────────▶│   Server    │
│             │                      │   💀 Dead   │
└─────────────┘                      └─────────────┘

With Rate Limiting:
┌─────────────┐     10 req/sec       ┌─────────────┐
│   Scraper   │─────────────────────▶│   Server    │
│             │◀─────────────────────│   ✓ Happy   │
└─────────────┘     429 if exceeded  └─────────────┘
```

### For the Scraper

| Aggressive | Respectful |
|------------|------------|
| Fast initially | Sustainable speed |
| Gets blocked quickly | Long-term access |
| IP banned | Under the radar |
| Wastes time retrying | Consistent results |

---

## Types of Rate Limits

### 1. Request-Based Limits

Limit on number of requests per time period.

```
100 requests per minute
1000 requests per hour
10000 requests per day
```

### 2. Bandwidth-Based Limits

Limit on data transferred.

```
10 MB per minute
100 MB per hour
```

### 3. Concurrent Connection Limits

Limit on simultaneous requests.

```
Maximum 5 concurrent connections
```

### 4. Per-Endpoint Limits

Different limits for different URLs.

```
/api/search: 10 requests/minute
/api/data: 100 requests/minute
```

---

## Detecting Rate Limits

### HTTP 429 Too Many Requests

The standard rate limit response:

```python
response = requests.get(url)

if response.status_code == 429:
    print("Rate limited!")
    
    # Check for retry information
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        print(f"Retry after: {retry_after} seconds")
```

### Rate Limit Headers

Many APIs provide rate limit info in headers:

```python
# Common rate limit headers
response.headers.get("X-RateLimit-Limit")      # Total allowed
response.headers.get("X-RateLimit-Remaining")  # Remaining
response.headers.get("X-RateLimit-Reset")      # When it resets
response.headers.get("Retry-After")            # Seconds to wait

# Example values
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 23
X-RateLimit-Reset: 1640000000  # Unix timestamp
Retry-After: 60  # Seconds
```

### Other Signs of Rate Limiting

| Sign | What It Looks Like |
|------|-------------------|
| **Soft block** | CAPTCHAs appear |
| **Content changes** | Different page served |
| **Slow responses** | Artificially delayed |
| **Empty responses** | 200 OK but no content |
| **Redirect** | Sent to block page |

---

## Throttling Strategies

### 1. Fixed Delay

Simplest approach—wait between each request.

```python
import time

for url in urls:
    response = requests.get(url)
    process(response)
    time.sleep(1)  # 1 second between requests
```

### 2. Random Delay

More human-like—vary the wait time.

```python
import random
import time

for url in urls:
    response = requests.get(url)
    process(response)
    
    # Random delay between 0.5 and 2 seconds
    delay = random.uniform(0.5, 2.0)
    time.sleep(delay)
```

### 3. Exponential Backoff

Increase delay after failures.

```python
import time

def fetch_with_backoff(url, max_retries=5):
    for attempt in range(max_retries):
        response = requests.get(url)
        
        if response.status_code == 200:
            return response
        
        if response.status_code == 429:
            # Exponential backoff: 1, 2, 4, 8, 16 seconds
            wait_time = 2 ** attempt
            print(f"Rate limited, waiting {wait_time}s...")
            time.sleep(wait_time)
        else:
            break
    
    return None
```

### 4. Token Bucket

Allow bursts while maintaining average rate.

```python
import time
from threading import Lock

class TokenBucket:
    def __init__(self, tokens_per_second, max_tokens):
        self.tokens_per_second = tokens_per_second
        self.max_tokens = max_tokens
        self.tokens = max_tokens
        self.last_update = time.time()
        self.lock = Lock()
    
    def acquire(self):
        with self.lock:
            now = time.time()
            # Add tokens based on elapsed time
            elapsed = now - self.last_update
            self.tokens = min(
                self.max_tokens,
                self.tokens + elapsed * self.tokens_per_second
            )
            self.last_update = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            
            # Calculate wait time
            wait_time = (1 - self.tokens) / self.tokens_per_second
            return wait_time

# Usage
bucket = TokenBucket(tokens_per_second=1, max_tokens=5)

for url in urls:
    wait = bucket.acquire()
    if wait is not True:
        time.sleep(wait)
    response = requests.get(url)
```

### 5. Adaptive Rate Limiting

Adjust speed based on response.

```python
class AdaptiveThrottler:
    def __init__(self, initial_delay=1.0, min_delay=0.1, max_delay=60.0):
        self.delay = initial_delay
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.consecutive_success = 0
    
    def success(self):
        """Call after successful request."""
        self.consecutive_success += 1
        if self.consecutive_success >= 10:
            # Speed up after 10 consecutive successes
            self.delay = max(self.min_delay, self.delay * 0.9)
            self.consecutive_success = 0
    
    def rate_limited(self):
        """Call after 429 response."""
        self.consecutive_success = 0
        self.delay = min(self.max_delay, self.delay * 2)
    
    def wait(self):
        time.sleep(self.delay)

# Usage
throttler = AdaptiveThrottler()

for url in urls:
    response = requests.get(url)
    
    if response.status_code == 429:
        throttler.rate_limited()
    else:
        throttler.success()
        process(response)
    
    throttler.wait()
```

---

## Implementing Rate Limiters

### Simple Rate Limiter Class

```python
import time
from collections import deque
from threading import Lock

class RateLimiter:
    """Limit requests to N per time window."""
    
    def __init__(self, max_requests, time_window):
        self.max_requests = max_requests
        self.time_window = time_window  # seconds
        self.requests = deque()
        self.lock = Lock()
    
    def wait_if_needed(self):
        with self.lock:
            now = time.time()
            
            # Remove old requests outside the window
            while self.requests and self.requests[0] < now - self.time_window:
                self.requests.popleft()
            
            if len(self.requests) >= self.max_requests:
                # Need to wait
                sleep_time = self.requests[0] + self.time_window - now
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            self.requests.append(time.time())

# Usage: 60 requests per minute
limiter = RateLimiter(max_requests=60, time_window=60)

for url in urls:
    limiter.wait_if_needed()
    response = requests.get(url)
```

### Async Rate Limiter

```python
import asyncio
import time

class AsyncRateLimiter:
    def __init__(self, rate_limit, time_period=1.0):
        self.rate_limit = rate_limit
        self.time_period = time_period
        self.tokens = rate_limit
        self.last_update = time.monotonic()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        async with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            self.tokens = min(
                self.rate_limit,
                self.tokens + elapsed * (self.rate_limit / self.time_period)
            )
            self.last_update = now
            
            if self.tokens < 1:
                wait_time = (1 - self.tokens) * (self.time_period / self.rate_limit)
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1

# Usage with aiohttp
import aiohttp

limiter = AsyncRateLimiter(rate_limit=10, time_period=1.0)  # 10 req/sec

async def fetch(session, url):
    await limiter.acquire()
    async with session.get(url) as response:
        return await response.text()

async def main(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

---

## Respecting robots.txt Crawl-Delay

```python
from urllib.robotparser import RobotFileParser
import time

def get_crawl_delay(base_url, user_agent="*"):
    rp = RobotFileParser()
    rp.set_url(f"{base_url}/robots.txt")
    rp.read()
    
    delay = rp.crawl_delay(user_agent)
    return delay if delay else 1.0  # Default to 1 second

# Usage
base_url = "https://example.com"
delay = get_crawl_delay(base_url)
print(f"Crawl delay: {delay} seconds")

for url in urls:
    response = requests.get(url)
    time.sleep(delay)
```

---

## Handling 429 Responses

### Basic Handler

```python
def make_request(url, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url)
        
        if response.status_code == 429:
            # Get retry time from header or use default
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"Rate limited. Waiting {retry_after}s...")
            time.sleep(retry_after)
            continue
        
        return response
    
    raise Exception(f"Failed after {max_retries} retries")
```

### Advanced Handler with Jitter

```python
import random

def make_request_with_jitter(url, max_retries=5):
    base_delay = 1
    
    for attempt in range(max_retries):
        response = requests.get(url)
        
        if response.status_code == 429:
            # Exponential backoff with jitter
            delay = base_delay * (2 ** attempt)
            jitter = random.uniform(0, delay * 0.1)  # 10% jitter
            total_delay = delay + jitter
            
            # Check Retry-After header
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                total_delay = max(total_delay, int(retry_after))
            
            print(f"Attempt {attempt + 1}: Waiting {total_delay:.1f}s...")
            time.sleep(total_delay)
            continue
        
        return response
    
    return None
```

---

## Distributed Rate Limiting

When running multiple scrapers, coordinate rate limits:

### Using Redis

```python
import redis
import time

class DistributedRateLimiter:
    def __init__(self, redis_client, key, max_requests, window_seconds):
        self.redis = redis_client
        self.key = key
        self.max_requests = max_requests
        self.window = window_seconds
    
    def acquire(self):
        pipe = self.redis.pipeline()
        now = time.time()
        window_start = now - self.window
        
        # Remove old entries
        pipe.zremrangebyscore(self.key, 0, window_start)
        # Count current entries
        pipe.zcard(self.key)
        # Add new entry
        pipe.zadd(self.key, {str(now): now})
        # Set expiry
        pipe.expire(self.key, self.window)
        
        results = pipe.execute()
        current_count = results[1]
        
        if current_count < self.max_requests:
            return True
        
        # Calculate wait time
        oldest = self.redis.zrange(self.key, 0, 0, withscores=True)
        if oldest:
            wait_time = oldest[0][1] + self.window - now
            return wait_time
        
        return self.window

# Usage
r = redis.Redis()
limiter = DistributedRateLimiter(r, "scraper:example.com", 60, 60)

wait = limiter.acquire()
if wait is True:
    # Proceed with request
    pass
else:
    time.sleep(wait)
```

---

## Best Practices

### Do's

```python
# ✅ Start slow and speed up if no issues
delay = 2.0
for url in urls:
    response = requests.get(url)
    if response.status_code == 200:
        delay = max(0.5, delay * 0.95)  # Gradually speed up
    time.sleep(delay)

# ✅ Respect Retry-After headers
if response.status_code == 429:
    wait = int(response.headers.get("Retry-After", 60))
    time.sleep(wait)

# ✅ Add randomization
time.sleep(random.uniform(1, 3))

# ✅ Monitor rate limit headers
remaining = int(response.headers.get("X-RateLimit-Remaining", 100))
if remaining < 10:
    time.sleep(10)  # Slow down when low
```

### Don'ts

```python
# ❌ No delay at all
for url in urls:
    requests.get(url)  # Will get blocked fast

# ❌ Fixed tiny delay
time.sleep(0.01)  # Still too fast

# ❌ Ignoring 429 responses
if response.status_code == 429:
    continue  # Wrong! Will keep getting blocked

# ❌ Same delay pattern (detectable)
time.sleep(1.000)  # Exactly 1 second every time = bot pattern
```

---

## Recommended Delays by Site Type

| Site Type | Recommended Delay | Notes |
|-----------|-------------------|-------|
| **Small sites** | 2-5 seconds | Be extra careful |
| **Medium sites** | 1-2 seconds | Standard scraping |
| **Large sites** | 0.5-1 second | Can handle more load |
| **APIs with limits** | Per their documentation | Respect stated limits |
| **Your own site** | As needed | You control it |

---

## Summary

### Quick Reference

```python
# Minimum viable throttling
import time
import random

for url in urls:
    response = requests.get(url)
    
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 60))
        time.sleep(retry_after)
        response = requests.get(url)
    
    process(response)
    time.sleep(random.uniform(1, 2))
```

### Key Principles

1. **Start slow** - Begin with conservative delays
2. **Adapt to feedback** - Speed up if no issues, slow down on errors
3. **Respect headers** - Honor `Retry-After` and rate limit headers
4. **Add randomness** - Don't use exact intervals
5. **Handle 429s gracefully** - Retry with backoff
6. **Think long-term** - Sustainable speed > fast blocking

---

*Next: [07_proxies_rotation_ips.md](07_proxies_rotation_ips.md) - Managing IP addresses at scale*
