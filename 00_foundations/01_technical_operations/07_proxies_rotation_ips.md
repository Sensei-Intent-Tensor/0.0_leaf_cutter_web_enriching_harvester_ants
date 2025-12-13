# Proxies & IP Rotation

> **Distributing Your Requests Across Multiple Identities**

When rate limiting isn't enough, or when you've been IP banned, proxies let you appear as different users from different locations.

---

## Why Use Proxies?

### Problems Proxies Solve

| Problem | Proxy Solution |
|---------|----------------|
| IP banned | Use different IP |
| Rate limited per IP | Distribute across IPs |
| Geo-restricted content | Use IP from allowed region |
| Identity tracking | Change fingerprint |
| ISP blocks | Route around restrictions |

### The Basic Concept

```
Without Proxy:
Your IP ──────────────────────▶ Target Site
(Blocked!)

With Proxy:
Your IP ──▶ Proxy Server ──────▶ Target Site
            (Different IP)       (Sees proxy IP)
```

---

## 1. Proxy Types

### Forward Proxy (What We Use)

```
Client ──▶ Proxy ──▶ Internet
```

You know the proxy, the destination doesn't.

### Proxy Categories

| Type | Description | Detection Risk | Cost | Speed |
|------|-------------|----------------|------|-------|
| **Datacenter** | Server IPs from cloud providers | High | Low | Fast |
| **Residential** | Real home IPs | Low | High | Medium |
| **Mobile** | Cell carrier IPs | Very Low | Very High | Slow |
| **ISP** | Residential IPs in datacenters | Low | Medium | Fast |

### Datacenter Proxies

- IPs from AWS, Google Cloud, DigitalOcean, etc.
- Easy to detect (IP ranges are known)
- Fast and cheap
- Good for sites without strong anti-bot

```python
# Datacenter proxy
proxy = "http://123.45.67.89:8080"
```

### Residential Proxies

- IPs from real home internet connections
- Very hard to detect
- Slower and more expensive
- Essential for heavily protected sites

```python
# Residential proxy (usually via service)
proxy = "http://user:pass@gate.smartproxy.com:7777"
```

### Mobile Proxies

- IPs from cellular carriers (4G/5G)
- Highest trust level (shared by many real users)
- Very expensive
- Use for most difficult targets

---

## 2. Proxy Protocols

### HTTP Proxy

```python
proxies = {
    "http": "http://proxy.example.com:8080",
    "https": "http://proxy.example.com:8080",
}
response = requests.get(url, proxies=proxies)
```

### HTTPS/CONNECT Proxy

Same as HTTP proxy but for HTTPS traffic. Uses CONNECT method.

```python
# Same syntax, proxy handles HTTPS
proxies = {
    "http": "http://proxy.example.com:8080",
    "https": "http://proxy.example.com:8080",
}
```

### SOCKS5 Proxy

Lower-level protocol, works for any traffic.

```python
# Requires requests[socks]
proxies = {
    "http": "socks5://proxy.example.com:1080",
    "https": "socks5://proxy.example.com:1080",
}
response = requests.get(url, proxies=proxies)
```

### Authenticated Proxy

```python
proxies = {
    "http": "http://username:password@proxy.example.com:8080",
    "https": "http://username:password@proxy.example.com:8080",
}
```

---

## 3. Proxy Rotation Strategies

### Round-Robin Rotation

```python
import itertools

class ProxyRotator:
    def __init__(self, proxies):
        self.proxies = proxies
        self.cycle = itertools.cycle(proxies)
    
    def get_proxy(self):
        proxy = next(self.cycle)
        return {"http": proxy, "https": proxy}

# Usage
rotator = ProxyRotator([
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "http://proxy3.example.com:8080",
])

for url in urls:
    response = requests.get(url, proxies=rotator.get_proxy())
```

### Random Selection

```python
import random

class RandomProxySelector:
    def __init__(self, proxies):
        self.proxies = proxies
    
    def get_proxy(self):
        proxy = random.choice(self.proxies)
        return {"http": proxy, "https": proxy}
```

### Weighted Selection (Quality-Based)

```python
import random

class WeightedProxySelector:
    def __init__(self, proxies_with_weights):
        """
        proxies_with_weights: [(proxy, weight), ...]
        Higher weight = more likely to be selected
        """
        self.proxies = proxies_with_weights
    
    def get_proxy(self):
        proxies, weights = zip(*self.proxies)
        proxy = random.choices(proxies, weights=weights, k=1)[0]
        return {"http": proxy, "https": proxy}

# Usage
selector = WeightedProxySelector([
    ("http://fast-proxy:8080", 10),   # Fast, use more
    ("http://slow-proxy:8080", 2),    # Slow, use less
    ("http://premium-proxy:8080", 5), # Balance
])
```

### Sticky Sessions (Same Proxy per Domain)

```python
from urllib.parse import urlparse

class StickyProxySelector:
    """Use same proxy for same domain (maintains sessions)."""
    
    def __init__(self, proxies):
        self.proxies = proxies
        self.domain_map = {}
    
    def get_proxy(self, url):
        domain = urlparse(url).netloc
        
        if domain not in self.domain_map:
            self.domain_map[domain] = random.choice(self.proxies)
        
        proxy = self.domain_map[domain]
        return {"http": proxy, "https": proxy}
```

---

## 4. Smart Proxy Management

### Proxy Health Tracking

```python
import time
from collections import defaultdict

class SmartProxyManager:
    def __init__(self, proxies):
        self.proxies = proxies
        self.stats = defaultdict(lambda: {
            "successes": 0,
            "failures": 0,
            "last_used": 0,
            "banned_until": 0,
        })
    
    def get_proxy(self):
        """Get best available proxy."""
        now = time.time()
        available = []
        
        for proxy in self.proxies:
            stat = self.stats[proxy]
            
            # Skip if temporarily banned
            if stat["banned_until"] > now:
                continue
            
            # Calculate score (higher = better)
            total = stat["successes"] + stat["failures"]
            if total == 0:
                score = 0.5  # Unknown, neutral
            else:
                score = stat["successes"] / total
            
            # Prefer less recently used
            time_bonus = min(0.2, (now - stat["last_used"]) / 60)
            
            available.append((proxy, score + time_bonus))
        
        if not available:
            # All banned, wait for first to unban
            return None
        
        # Select best proxy
        available.sort(key=lambda x: x[1], reverse=True)
        proxy = available[0][0]
        
        self.stats[proxy]["last_used"] = now
        return {"http": proxy, "https": proxy}
    
    def report_success(self, proxy):
        self.stats[proxy]["successes"] += 1
    
    def report_failure(self, proxy, ban_duration=60):
        self.stats[proxy]["failures"] += 1
        
        # Multiple failures = temporary ban
        total = self.stats[proxy]["failures"]
        if total >= 3:
            self.stats[proxy]["banned_until"] = time.time() + ban_duration

# Usage
manager = SmartProxyManager(proxy_list)

for url in urls:
    proxy = manager.get_proxy()
    if not proxy:
        time.sleep(60)  # Wait for proxy to recover
        continue
    
    response = requests.get(url, proxies=proxy)
    
    if response.status_code == 200:
        manager.report_success(list(proxy.values())[0])
    elif response.status_code in [403, 429]:
        manager.report_failure(list(proxy.values())[0])
```

### Proxy Pool with Auto-Refresh

```python
class ProxyPool:
    """Automatically remove bad proxies and add new ones."""
    
    def __init__(self, initial_proxies, proxy_source=None):
        self.proxies = set(initial_proxies)
        self.dead_proxies = set()
        self.proxy_source = proxy_source  # Function to get new proxies
        self.min_pool_size = 10
    
    def get_proxy(self):
        if len(self.proxies) < self.min_pool_size:
            self._refresh_pool()
        
        proxy = random.choice(list(self.proxies))
        return {"http": proxy, "https": proxy}
    
    def mark_dead(self, proxy):
        self.proxies.discard(proxy)
        self.dead_proxies.add(proxy)
    
    def _refresh_pool(self):
        if self.proxy_source:
            new_proxies = self.proxy_source()
            # Add new proxies that aren't known dead
            self.proxies.update(set(new_proxies) - self.dead_proxies)
```

---

## 5. Proxy Services

### Major Providers

| Service | Type | Pricing | Best For |
|---------|------|---------|----------|
| **Bright Data** | All types | $$$ | Enterprise |
| **Smartproxy** | Residential, DC | $$ | Mid-scale |
| **Oxylabs** | All types | $$$ | Enterprise |
| **Proxy-Seller** | Datacenter | $ | Budget |
| **PacketStream** | Residential | $$ | Pay-per-GB |
| **NetNut** | ISP | $$ | Speed + stealth |

### Rotating Proxy Services

Most services offer a single endpoint that automatically rotates IPs:

```python
# Smartproxy example - each request gets different IP
proxy = "http://user:pass@gate.smartproxy.com:7777"

# Bright Data example
proxy = "http://user:pass@brd.superproxy.io:22225"
```

### Geo-Targeting

```python
# Target specific country
proxy = "http://user:pass@us.smartproxy.com:7777"  # US IPs
proxy = "http://user:pass@gb.smartproxy.com:7777"  # UK IPs

# Bright Data geo-targeting
proxy = "http://user-country-us:pass@brd.superproxy.io:22225"
```

### Session Persistence

```python
# Keep same IP for multiple requests (session stickiness)
proxy = "http://user-session-abc123:pass@gate.smartproxy.com:7777"

# All requests with same session ID get same IP
```

---

## 6. Free Proxy Sources

### Warning

Free proxies are:
- Unreliable (often offline)
- Slow
- Potentially malicious (can intercept traffic)
- Often already banned

**Only use for non-sensitive testing.**

### Free Proxy Lists

```python
import requests

def get_free_proxies():
    """Fetch free proxies from public list. Use with caution!"""
    response = requests.get(
        "https://api.proxyscrape.com/v2/?request=getproxies"
        "&protocol=http&timeout=5000&country=all"
    )
    proxies = response.text.strip().split("\n")
    return [f"http://{p}" for p in proxies]
```

### Validating Free Proxies

```python
def validate_proxy(proxy, test_url="http://httpbin.org/ip", timeout=5):
    """Test if proxy works."""
    try:
        response = requests.get(
            test_url,
            proxies={"http": proxy, "https": proxy},
            timeout=timeout
        )
        return response.status_code == 200
    except:
        return False

# Filter to working proxies
free_proxies = get_free_proxies()
working_proxies = [p for p in free_proxies if validate_proxy(p)]
```

---

## 7. Proxy Best Practices

### Match Proxy to Headers

```python
# BAD: US proxy with German headers
proxies = {"http": "http://us-proxy:8080"}
headers = {"Accept-Language": "de-DE"}  # Mismatch!

# GOOD: Consistent identity
proxies = {"http": "http://us-proxy:8080"}
headers = {"Accept-Language": "en-US,en;q=0.9"}
```

### Warm Up Proxies

```python
def warm_up_proxy(proxy, target_domain):
    """Visit site naturally before scraping."""
    session = requests.Session()
    
    # Visit homepage first
    session.get(
        f"https://{target_domain}/",
        proxies=proxy,
        headers=get_headers()
    )
    time.sleep(random.uniform(1, 3))
    
    # Browse a few pages
    for path in ["/about", "/products"]:
        session.get(
            f"https://{target_domain}{path}",
            proxies=proxy,
            headers=get_headers()
        )
        time.sleep(random.uniform(2, 5))
    
    return session  # Return warmed-up session
```

### Handle Proxy Failures Gracefully

```python
def fetch_with_proxy_retry(url, proxy_manager, max_retries=3):
    for attempt in range(max_retries):
        proxy = proxy_manager.get_proxy()
        
        try:
            response = requests.get(
                url,
                proxies=proxy,
                timeout=30
            )
            
            if response.status_code == 200:
                proxy_manager.report_success(proxy)
                return response
            
            elif response.status_code in [403, 429]:
                proxy_manager.report_failure(proxy)
                # Try different proxy
                continue
        
        except (requests.exceptions.ProxyError,
                requests.exceptions.ConnectTimeout) as e:
            proxy_manager.report_failure(proxy)
            continue
    
    raise Exception("All proxy attempts failed")
```

---

## 8. Proxy + Browser Automation

### Playwright with Proxy

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
    page.goto("https://target-site.com")
```

### Selenium with Proxy

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--proxy-server=http://proxy.example.com:8080")

driver = webdriver.Chrome(options=options)
driver.get("https://target-site.com")
```

### Authenticated Proxy with Selenium

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver as wire_webdriver

# Using selenium-wire for authenticated proxies
options = {
    "proxy": {
        "http": "http://user:pass@proxy.example.com:8080",
        "https": "http://user:pass@proxy.example.com:8080",
    }
}

driver = wire_webdriver.Chrome(seleniumwire_options=options)
```

---

## 9. Testing Your Setup

### Check Your Exit IP

```python
def get_exit_ip(proxy=None):
    """Get the IP address seen by target server."""
    response = requests.get(
        "https://api.ipify.org?format=json",
        proxies=proxy,
        timeout=10
    )
    return response.json()["ip"]

# Without proxy
print(f"Real IP: {get_exit_ip()}")

# With proxy
proxy = {"http": "http://proxy:8080", "https": "http://proxy:8080"}
print(f"Proxy IP: {get_exit_ip(proxy)}")
```

### Check Proxy Anonymity

```python
def check_anonymity(proxy):
    """Check if proxy leaks real IP."""
    response = requests.get(
        "https://httpbin.org/headers",
        proxies=proxy
    )
    headers = response.json()["headers"]
    
    # Check for forwarding headers
    leak_headers = [
        "X-Forwarded-For",
        "X-Real-Ip",
        "Via",
        "Forwarded",
    ]
    
    for header in leak_headers:
        if header in headers:
            print(f"Warning: {header} = {headers[header]}")
            return False
    
    return True
```

---

## Summary

| Proxy Type | Use Case | Cost | Detection Risk |
|------------|----------|------|----------------|
| **Datacenter** | Basic scraping, testing | $ | High |
| **Residential** | Protected sites | $$$ | Low |
| **ISP** | Balance of speed/stealth | $$ | Low |
| **Mobile** | Most difficult targets | $$$$ | Very Low |

### Key Takeaways

1. **Start with datacenter proxies** - Upgrade if blocked
2. **Rotate proxies** - Don't hammer one IP
3. **Match proxy location to headers** - Be consistent
4. **Track proxy health** - Remove bad proxies
5. **Use sticky sessions when needed** - For auth flows
6. **Test your setup** - Verify IPs are changing

---

*This completes the Technical Operations section. Next: [../02_anti_scraping_tech/](../02_anti_scraping_tech/) - Understanding anti-bot systems*
