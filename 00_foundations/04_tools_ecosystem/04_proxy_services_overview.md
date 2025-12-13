# Proxy Services Overview

> **Commercial Proxy Providers and How to Choose**

When you need IPs beyond your own, proxy services provide the infrastructure. This document covers the major providers and selection criteria.

---

## Proxy Service Categories

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROXY SERVICE TYPES                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  DATACENTER PROXIES                                            │
│  ├── Cheap, fast, easily detected                               │
│  └── Good for: Low-security sites, high volume                 │
│                                                                 │
│  RESIDENTIAL PROXIES                                           │
│  ├── Real home IPs, expensive, hard to detect                   │
│  └── Good for: Protected sites, appearing human                │
│                                                                 │
│  ISP PROXIES                                                   │
│  ├── Residential IPs in datacenters, fast + stealthy           │
│  └── Good for: Speed + stealth balance                         │
│                                                                 │
│  MOBILE PROXIES                                                │
│  ├── Cellular carrier IPs, most trusted, expensive             │
│  └── Good for: Most protected sites, social media              │
│                                                                 │
│  SCRAPING APIs                                                 │
│  ├── Handle proxies + browsers for you                         │
│  └── Good for: Ease of use, complex targets                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Major Providers

### Tier 1: Enterprise Providers

| Provider | Types | Starting Price | Best For |
|----------|-------|----------------|----------|
| **Bright Data** | All types | $500+/mo | Enterprise, largest pool |
| **Oxylabs** | All types | $300+/mo | Enterprise, good support |
| **Smartproxy** | Residential, DC | $75+/mo | Mid-market, good value |

### Tier 2: Mid-Market

| Provider | Types | Starting Price | Best For |
|----------|-------|----------------|----------|
| **IPRoyal** | Residential, DC | $50+/mo | Budget residential |
| **Proxy-Seller** | Datacenter | $20+/mo | Budget datacenter |
| **Webshare** | Datacenter | $30+/mo | Cheap datacenter |
| **NetNut** | ISP, Residential | $100+/mo | ISP proxies |

### Tier 3: Specialty/Budget

| Provider | Types | Starting Price | Best For |
|----------|-------|----------------|----------|
| **PacketStream** | Residential | Pay-per-GB | Small projects |
| **Soax** | Residential | $75+/mo | Geo-targeting |
| **GeoSurf** | Residential | $300+/mo | Specific geos |

### Scraping APIs (Proxies Included)

| Provider | Type | Starting Price | Best For |
|----------|------|----------------|----------|
| **ScraperAPI** | API | $49/mo | General scraping |
| **Zyte (Crawlera)** | API | $29/mo | Scrapy integration |
| **Apify** | Platform | Pay-per-use | Full scraping platform |
| **WebScrapingAPI** | API | $49/mo | Simple API |

---

## Bright Data (Luminati)

### Overview
- Largest proxy network (72M+ IPs)
- All proxy types available
- Advanced features (Web Unlocker, SERP API)
- Enterprise pricing

### Proxy Types & Pricing

| Type | Pool Size | Price |
|------|-----------|-------|
| Datacenter | 770K+ | $0.06/IP/day |
| ISP | 700K+ | $0.50/GB |
| Residential | 72M+ | $8.40/GB |
| Mobile | 7M+ | $24/GB |

### Usage Example

```python
import requests

# Residential proxy
proxy = "http://USER:PASS@brd.superproxy.io:22225"

response = requests.get(
    "https://example.com",
    proxies={"http": proxy, "https": proxy}
)

# With country targeting
proxy = "http://USER-country-us:PASS@brd.superproxy.io:22225"

# With session (sticky IP)
proxy = "http://USER-session-abc123:PASS@brd.superproxy.io:22225"
```

### Web Unlocker (Scraping API)

```python
# Handles proxies, browsers, CAPTCHAs automatically
response = requests.get(
    "https://protected-site.com",
    proxies={"http": "http://USER:PASS@brd.superproxy.io:22225"},
    headers={"User-Agent": "Mozilla/5.0..."}
)
```

---

## Smartproxy

### Overview
- Good balance of price/quality
- Easy to use
- Good documentation
- Responsive support

### Pricing

| Type | Pool Size | Price |
|------|-----------|-------|
| Datacenter | 400K+ | $2.50/GB |
| Residential | 55M+ | $7/GB |
| ISP | 400K+ | $4/GB |

### Usage Example

```python
# Rotating residential
proxy = "http://USER:PASS@gate.smartproxy.com:7777"

# Sticky session
proxy = "http://USER-session-abc:PASS@gate.smartproxy.com:7777"

# Country targeting
proxy = "http://USER-country-US:PASS@us.smartproxy.com:7777"
```

---

## Oxylabs

### Overview
- Enterprise focus
- Excellent support
- Strong compliance stance
- Good documentation

### Pricing

| Type | Pool Size | Price |
|------|-----------|-------|
| Datacenter | 2M+ | $1.20/GB |
| Residential | 100M+ | $8/GB |

### Scraper APIs

```python
# Web Scraper API
payload = {
    "source": "universal",
    "url": "https://example.com",
    "render": "html"
}

response = requests.post(
    "https://realtime.oxylabs.io/v1/queries",
    auth=("USER", "PASS"),
    json=payload
)
```

---

## ScraperAPI

### Overview
- Simple API approach
- Handles proxies internally
- JavaScript rendering available
- Pay per successful request

### Pricing
- 5,000 API credits free
- Starter: $49/mo (100,000 credits)
- Business: $149/mo (1,000,000 credits)

### Usage Example

```python
import requests

API_KEY = "your_api_key"

# Simple request
response = requests.get(
    f"http://api.scraperapi.com?api_key={API_KEY}&url=https://example.com"
)

# With JavaScript rendering
response = requests.get(
    f"http://api.scraperapi.com?api_key={API_KEY}&url=https://example.com&render=true"
)

# Country targeting
response = requests.get(
    f"http://api.scraperapi.com?api_key={API_KEY}&url=https://example.com&country_code=us"
)

# As proxy
proxy = f"http://scraperapi:{API_KEY}@proxy-server.scraperapi.com:8001"
response = requests.get(url, proxies={"http": proxy, "https": proxy})
```

---

## Zyte (Formerly Scrapinghub)

### Overview
- Created Scrapy
- Best Scrapy integration
- Smart proxy management
- Enterprise features

### Products
- **Zyte API**: Scraping API with extraction
- **Smart Proxy Manager**: Proxy rotation
- **Scrapy Cloud**: Hosted Scrapy

### Usage Example

```python
# Zyte API
response = requests.post(
    "https://api.zyte.com/v1/extract",
    auth=(API_KEY, ""),
    json={
        "url": "https://example.com",
        "httpResponseBody": True,
        "httpResponseHeaders": True
    }
)

# With Scrapy
# settings.py
DOWNLOADER_MIDDLEWARES = {
    'scrapy_zyte_smartproxy.ZyteSmartProxyMiddleware': 610
}
ZYTE_SMARTPROXY_APIKEY = 'your-api-key'
```

---

## Choosing a Provider

### Decision Matrix

| Priority | Recommended |
|----------|-------------|
| **Lowest cost** | Webshare, Proxy-Seller (DC) |
| **Best value residential** | Smartproxy, IPRoyal |
| **Enterprise scale** | Bright Data, Oxylabs |
| **Easiest setup** | ScraperAPI, Zyte |
| **Mobile proxies** | Bright Data |
| **Specific countries** | Bright Data, Soax |

### Questions to Ask

```
1. What sites am I scraping?
   └── Protected sites → Residential/Mobile
   └── Basic sites → Datacenter

2. What volume?
   └── < 100K requests → ScraperAPI/Zyte
   └── 100K - 10M → Smartproxy/IPRoyal
   └── > 10M → Bright Data/Oxylabs

3. What's my budget?
   └── < $50/mo → Webshare, PacketStream
   └── $50-200/mo → Smartproxy
   └── $200+/mo → Bright Data, Oxylabs

4. Do I need specific locations?
   └── Yes → Check provider coverage

5. Do I need sticky sessions?
   └── Yes → Most providers support this
```

---

## Integration Patterns

### Basic Rotation

```python
import requests
import itertools

proxies = [
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "http://proxy3.example.com:8080",
]

proxy_cycle = itertools.cycle(proxies)

def fetch(url):
    proxy = next(proxy_cycle)
    return requests.get(url, proxies={"http": proxy, "https": proxy})
```

### With Proxy Service

```python
# Most services rotate automatically
proxy = "http://user:pass@gate.provider.com:7777"

# Every request gets a new IP
for url in urls:
    response = requests.get(url, proxies={"http": proxy, "https": proxy})
```

### Session Stickiness

```python
import uuid

# Generate session ID
session_id = str(uuid.uuid4())

# All requests with same session use same IP
proxy = f"http://user-session-{session_id}:pass@gate.provider.com:7777"

# Use for multi-page flows
session = requests.Session()
session.proxies = {"http": proxy, "https": proxy}
session.get("https://example.com/login")
session.post("https://example.com/login", data=credentials)
session.get("https://example.com/dashboard")
```

---

## Cost Optimization

### Tips to Reduce Costs

```python
# 1. Cache responses
from functools import lru_cache

@lru_cache(maxsize=1000)
def fetch_cached(url):
    return fetch(url)

# 2. Use datacenter where possible
# Start with DC, upgrade to residential only if blocked

# 3. Minimize bandwidth
headers = {"Accept-Encoding": "gzip, deflate, br"}

# 4. Block unnecessary resources
# In browser automation, block images/CSS

# 5. Batch requests
# Many providers charge per request, batch when possible

# 6. Monitor usage
# Set up alerts before hitting limits
```

### Estimated Costs

| Use Case | Monthly Volume | Estimated Cost |
|----------|----------------|----------------|
| Small project | 10K requests | $20-50 |
| Medium project | 100K requests | $75-200 |
| Large project | 1M requests | $300-1000 |
| Enterprise | 10M+ requests | $2000+ |

---

## Summary

| Provider | Best For | Starting Price |
|----------|----------|----------------|
| **Bright Data** | Enterprise, all types | $500/mo |
| **Smartproxy** | Mid-market value | $75/mo |
| **Oxylabs** | Enterprise, support | $300/mo |
| **ScraperAPI** | Simplicity | $49/mo |
| **Zyte** | Scrapy users | $29/mo |
| **Webshare** | Budget DC | $30/mo |
| **PacketStream** | Pay-per-use | $1/GB |

---

*Next: [05_data_storage_options.md](05_data_storage_options.md) - Where to store your scraped data*
