# Proxies & IP Rotation

> **Scaling Scraping Through Multiple Identities**

Your IP address is your identity online. When scraping at scale, a single IP quickly gets rate-limited or blocked. Proxies let you distribute requests across many IP addresses.

---

## Why Use Proxies

```
Single IP:
┌─────────────┐                    ┌─────────────┐
│   Scraper   │───── All reqs ────▶│   Target    │
│  1.2.3.4    │                    │   Server    │
└─────────────┘                    └─────────────┘
     │                                    │
     └──── Gets blocked after N requests ─┘

With Proxies:
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Scraper   │────▶│  Proxy A    │────▶│             │
│             │     │  5.6.7.8    │     │   Target    │
│             │────▶│  Proxy B    │────▶│   Server    │
│             │     │  9.10.11.12 │     │             │
│             │────▶│  Proxy C    │────▶│             │
│             │     │  13.14.15.16│     │             │
└─────────────┘     └─────────────┘     └─────────────┘
                         │
                         └── Each IP has its own rate limit quota
```

---

## Types of Proxies

### 1. Datacenter Proxies

IP addresses from data centers (AWS, Google Cloud, etc.)

| Pros | Cons |
|------|------|
| Fast | Easily detected |
| Cheap | Often pre-blocked |
| Reliable uptime | Not residential |
| Unlimited bandwidth | Same IP ranges as other bots |

**Best for**: High volume, less protected sites

### 2. Residential Proxies

IP addresses from real ISPs (Comcast, AT&T, etc.)

| Pros | Cons |
|------|------|
| Look like real users | Expensive |
| Hard to detect | Slower |
| Bypass geo-restrictions | May be unstable |
| Fresh IPs | Bandwidth limited |

**Best for**: Protected sites, geo-specific scraping

### 3. Mobile Proxies

IP addresses from mobile carriers (4G/5G)

| Pros | Cons |
|------|------|
| Highest trust level | Most expensive |
| Shared IPs are normal | Very limited availability |
| Rarely blocked | Slowest |

**Best for**: Most aggressive anti-bot systems

### 4. ISP Proxies

Static residential IPs (dedicated)

| Pros | Cons |
|------|------|
| Stable, same IP | Expensive |
| Residential trust | Limited locations |
| Fast | Can still be fingerprinted |

**Best for**: When you need consistent identity

### Comparison Table

| Type | Trust Level | Speed | Cost | Best Use |
|------|-------------|-------|------|----------|
| **Datacenter** | Low | Fast | $ | Bulk scraping |
| **Residential** | High | Medium | $$$ | Protected sites |
| **Mobile** | Highest | Slow | $$$$ | Hardest targets |
| **ISP/Static** | High | Fast | $$$ | Account work |

---

## Proxy Protocols

### HTTP Proxy

Most common, works for HTTP/HTTPS traffic.

```python
proxies = {
    "http": "http://user:pass@proxy.example.com:8080",
    "https": "http://user:pass@proxy.example.com:8080",
}

response = requests.get(url, proxies=proxies)
```

### SOCKS5 Proxy

Lower level, more versatile, supports UDP.

```python
# Requires requests[socks] or PySocks
proxies = {
    "http": "socks5://user:pass@proxy.example.com:1080",
    "https": "socks5://user:pass@proxy.example.com:1080",
}

response = requests.get(url, proxies=proxies)
```

### Comparison

| Feature | HTTP Proxy | SOCKS5 Proxy |
|---------|------------|--------------|
| Protocol support | HTTP/HTTPS only | Any TCP/UDP |
| Speed | Fast | Slightly slower |
| Setup | Simple | Needs library |
| Use case | Web scraping | General traffic |

---

## Using Proxies in Python

### With requests

```python
import requests

# Single proxy
proxy = "http://user:pass@proxy.example.com:8080"
proxies = {"http": proxy, "https": proxy}

response = requests.get(url, proxies=proxies)

# Verify proxy is being used
response = requests.get("https://httpbin.org/ip", proxies=proxies)
print(response.json())  # Should show proxy IP
```

### With requests Session

```python
session = requests.Session()
session.proxies = {
    "http": "http://user:pass@proxy.example.com:8080",
    "https": "http://user:pass@proxy.example.com:8080",
}

# All requests use proxy
response = session.get(url)
```

### With aiohttp (Async)

```python
import aiohttp

async def fetch_with_proxy(url, proxy):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, proxy=proxy) as response:
            return await response.text()

# Usage
proxy = "http://user:pass@proxy.example.com:8080"
html = await fetch_with_proxy(url, proxy)
```

### With Playwright

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        proxy={
            "server": "http://proxy.example.com:8080",
            "username": "user",
            "password": "pass",
        }
    )
    page = browser.new_page()
    page.goto("https://httpbin.org/ip")
    print(page.content())  # Shows proxy IP
```

### With Scrapy

```python
# settings.py
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
}

# In spider
def start_requests(self):
    yield scrapy.Request(
        url,
        meta={'proxy': 'http://user:pass@proxy.example.com:8080'}
    )
```

---

## Proxy Rotation

### Simple Round-Robin

```python
import itertools

class ProxyRotator:
    def __init__(self, proxies):
        self.proxy_cycle = itertools.cycle(proxies)
    
    def get_proxy(self):
        return next(self.proxy_cycle)

# Usage
proxies = [
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "http://proxy3.example.com:8080",
]
rotator = ProxyRotator(proxies)

for url in urls:
    proxy = rotator.get_proxy()
    response = requests.get(url, proxies={"http": proxy, "https": proxy})
```

### Random Selection

```python
import random

class RandomProxyRotator:
    def __init__(self, proxies):
        self.proxies = proxies
    
    def get_proxy(self):
        return random.choice(self.proxies)
```

### Weighted Selection (By Quality)

```python
import random

class WeightedProxyRotator:
    def __init__(self, proxies_with_weights):
        # [(proxy, weight), ...]
        self.proxies = [p[0] for p in proxies_with_weights]
        self.weights = [p[1] for p in proxies_with_weights]
    
    def get_proxy(self):
        return random.choices(self.proxies, weights=self.weights)[0]

# Usage - prefer faster proxies
rotator = WeightedProxyRotator([
    ("http://fast-proxy:8080", 10),    # 10x more likely
    ("http://medium-proxy:8080", 5),   # 5x more likely
    ("http://slow-proxy:8080", 1),     # baseline
])
```

### Smart Rotation with Health Tracking

```python
import time
from collections import defaultdict

class SmartProxyRotator:
    def __init__(self, proxies):
        self.proxies = proxies
        self.failures = defaultdict(int)
        self.last_used = defaultdict(float)
        self.cooldown = 60  # seconds
    
    def get_proxy(self):
        now = time.time()
        available = []
        
        for proxy in self.proxies:
            # Skip if too many failures
            if self.failures[proxy] >= 3:
                continue
            
            # Skip if used too recently
            if now - self.last_used[proxy] < self.cooldown:
                continue
            
            available.append(proxy)
        
        if not available:
            # Reset failures if all proxies exhausted
            self.failures.clear()
            available = self.proxies
        
        proxy = random.choice(available)
        self.last_used[proxy] = now
        return proxy
    
    def report_success(self, proxy):
        self.failures[proxy] = max(0, self.failures[proxy] - 1)
    
    def report_failure(self, proxy):
        self.failures[proxy] += 1

# Usage
rotator = SmartProxyRotator(proxies)

for url in urls:
    proxy = rotator.get_proxy()
    try:
        response = requests.get(url, proxies={"http": proxy, "https": proxy}, timeout=10)
        if response.status_code == 200:
            rotator.report_success(proxy)
        else:
            rotator.report_failure(proxy)
    except:
        rotator.report_failure(proxy)
```

---

## Proxy Providers

### Types of Services

| Service Type | How It Works | Examples |
|--------------|--------------|----------|
| **Proxy List** | You manage rotation | Free lists, purchased lists |
| **Rotating Proxy** | Provider rotates for you | Bright Data, Oxylabs |
| **API-based** | Get proxy per request | ScraperAPI, Crawlbase |

### Popular Providers

| Provider | Type | Specialty |
|----------|------|-----------|
| **Bright Data** | All types | Enterprise, largest pool |
| **Oxylabs** | Residential, DC | High quality residential |
| **Smartproxy** | Residential, DC | Good value |
| **IPRoyal** | Residential | Budget option |
| **ScraperAPI** | API service | Handles everything |
| **Crawlbase** | API service | Simple integration |

### API-Based Services

These handle proxies, rotation, and often JavaScript rendering:

```python
# ScraperAPI example
api_key = "YOUR_API_KEY"
url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}"
response = requests.get(url)

# Crawlbase example
token = "YOUR_TOKEN"
url = f"https://api.crawlbase.com/?token={token}&url={target_url}"
response = requests.get(url)
```

---

## Testing Proxies

### Verify Proxy Works

```python
def test_proxy(proxy):
    """Test if proxy is working and return response time."""
    test_url = "https://httpbin.org/ip"
    proxies = {"http": proxy, "https": proxy}
    
    try:
        start = time.time()
        response = requests.get(test_url, proxies=proxies, timeout=10)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            ip = response.json()["origin"]
            return {"working": True, "ip": ip, "latency": elapsed}
    except Exception as e:
        return {"working": False, "error": str(e)}
    
    return {"working": False, "status": response.status_code}

# Test all proxies
for proxy in proxies:
    result = test_proxy(proxy)
    print(f"{proxy}: {result}")
```

### Verify IP Changed

```python
def get_current_ip(proxy=None):
    proxies = {"http": proxy, "https": proxy} if proxy else None
    response = requests.get("https://api.ipify.org?format=json", proxies=proxies)
    return response.json()["ip"]

# Test rotation
for _ in range(5):
    proxy = rotator.get_proxy()
    ip = get_current_ip(proxy)
    print(f"Proxy: {proxy} -> IP: {ip}")
```

### Check for Proxy Detection

```python
def check_proxy_detection(proxy):
    """Check if a site detects proxy usage."""
    proxies = {"http": proxy, "https": proxy}
    
    # Sites that detect proxies
    test_sites = [
        "https://whatismyipaddress.com/",
        "https://www.ipqualityscore.com/",
    ]
    
    for site in test_sites:
        response = requests.get(site, proxies=proxies)
        if "proxy" in response.text.lower() or "vpn" in response.text.lower():
            return True
    
    return False
```

---

## Geo-Targeting

### Why Location Matters

- Different prices by region
- Region-locked content
- Local search results
- Compliance with local laws

### Setting Location

```python
# Most proxy providers support geo-targeting
# Format varies by provider

# Bright Data format
proxy = "http://user-country-us:pass@proxy.brightdata.com:22225"

# Oxylabs format
proxy = "http://user:pass@us-pr.oxylabs.io:10000"

# With session/sticky IP
proxy = "http://user-country-us-session-abc123:pass@proxy.example.com:8080"
```

### Common Geo-Target Parameters

| Parameter | Example | Use |
|-----------|---------|-----|
| Country | `country-us` | Target US IPs |
| State | `state-california` | Target California |
| City | `city-newyork` | Target NYC |
| Session | `session-abc123` | Keep same IP |

---

## Common Issues & Solutions

### Issue: Proxy Not Working

```python
# Check if proxy is reachable
import socket

def check_proxy_reachable(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect((host, port))
        return True
    except:
        return False
    finally:
        sock.close()
```

### Issue: SSL Errors

```python
# Some proxies have SSL issues
# Option 1: Disable verification (not recommended for production)
response = requests.get(url, proxies=proxies, verify=False)

# Option 2: Use proxy's SSL certificate
response = requests.get(url, proxies=proxies, verify="/path/to/proxy-ca.crt")
```

### Issue: Timeout

```python
# Increase timeout for slow proxies
response = requests.get(
    url, 
    proxies=proxies, 
    timeout=(10, 30)  # 10s connect, 30s read
)
```

### Issue: Proxy Authentication Failed

```python
# URL-encode special characters in password
from urllib.parse import quote

username = "user"
password = "p@ss:word"  # Has special chars
encoded_password = quote(password, safe="")

proxy = f"http://{username}:{encoded_password}@proxy.example.com:8080"
```

### Issue: IP Ban Across All Proxies

This usually means detection is based on something other than IP:
- Browser fingerprint
- Cookies
- Request patterns
- Headers

---

## Best Practices

### Do's

```python
# ✅ Test proxies before using
working_proxies = [p for p in proxies if test_proxy(p)["working"]]

# ✅ Implement health tracking
rotator.report_failure(proxy)

# ✅ Match proxy type to target site protection level
# Simple site → Datacenter proxy
# Protected site → Residential proxy

# ✅ Use sessions for related requests
session = requests.Session()
session.proxies = {"http": proxy, "https": proxy}

# ✅ Rotate proxies based on target's rate limits
```

### Don'ts

```python
# ❌ Use free proxy lists for serious work
# They're unreliable, slow, and potentially malicious

# ❌ Use datacenter proxies for heavily protected sites
# They're easily detected

# ❌ Use the same proxy for thousands of requests
# It will get rate limited/blocked

# ❌ Ignore proxy failures
if not response:
    continue  # Wrong - should track and rotate
```

---

## Summary

| Concept | Key Points |
|---------|------------|
| **Datacenter Proxies** | Fast, cheap, easily detected |
| **Residential Proxies** | High trust, expensive, slower |
| **Mobile Proxies** | Highest trust, most expensive |
| **Rotation** | Essential for scale, many strategies |
| **Testing** | Always verify proxies work |
| **Geo-targeting** | Match proxy location to needs |

### Quick Start Template

```python
import requests
import random

class SimpleProxyRotator:
    def __init__(self, proxies):
        self.proxies = proxies
        self.bad_proxies = set()
    
    def get_proxy(self):
        available = [p for p in self.proxies if p not in self.bad_proxies]
        if not available:
            self.bad_proxies.clear()
            available = self.proxies
        return random.choice(available)
    
    def mark_bad(self, proxy):
        self.bad_proxies.add(proxy)

def scrape_with_proxies(urls, proxies):
    rotator = SimpleProxyRotator(proxies)
    results = []
    
    for url in urls:
        proxy = rotator.get_proxy()
        try:
            response = requests.get(
                url,
                proxies={"http": proxy, "https": proxy},
                timeout=15
            )
            results.append(response.text)
        except:
            rotator.mark_bad(proxy)
    
    return results
```

---

*This completes the Technical Operations section. Next: [../02_anti_scraping_tech/](../02_anti_scraping_tech/) - Understanding what you're up against*
