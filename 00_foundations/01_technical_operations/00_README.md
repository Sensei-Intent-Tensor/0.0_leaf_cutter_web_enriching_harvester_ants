# 01_technical_operations

> **How the Web Works for Scrapers**

This section covers the technical fundamentals you need to understand before building robust scrapers. From HTTP basics to proxy management, this is the engineering knowledge that separates working scrapers from blocked ones.

---

## 📚 Documents in This Section

| # | Document | Lines | Description |
|---|----------|-------|-------------|
| 01 | [HTTP Requests Anatomy](01_http_requests_anatomy.md) | 636 | Request/response structure, methods, headers, status codes |
| 02 | [CORS Explained](02_cors_explained.md) | 378 | Cross-origin restrictions and why scrapers ignore them |
| 03 | [Cookies, Sessions & State](03_cookies_sessions_state.md) | 612 | Maintaining identity across requests, login flows |
| 04 | [Headers & User-Agents](04_headers_user_agents.md) | 555 | Crafting convincing request headers |
| 05 | [JavaScript Rendering & SPAs](05_javascript_rendering_spa.md) | 631 | Handling JavaScript-dependent content |
| 06 | [Rate Limiting & Throttling](06_rate_limiting_throttling.md) | 618 | Controlling request speed |
| 07 | [Proxies & IP Rotation](07_proxies_rotation_ips.md) | 632 | Managing IP addresses and proxies |

**Total: 4,062 lines of technical knowledge**

---

## 🎯 Reading Order

### For Beginners

Read in order:
1. **HTTP Requests Anatomy** - Understand what a request actually is
2. **Headers & User-Agents** - Learn to look like a browser
3. **Cookies & Sessions** - Understand state and auth
4. **Rate Limiting** - Don't get blocked immediately
5. **JavaScript Rendering** - When static scraping fails
6. **Proxies** - Scale up without getting banned

### Quick Reference

Already know the basics? Jump to what you need:
- Getting blocked? → Rate Limiting, Proxies
- Login issues? → Cookies & Sessions
- Empty pages? → JavaScript Rendering
- 403 errors? → Headers & User-Agents

---

## 🔑 Key Takeaways by Document

### HTTP Requests Anatomy
- Every scraper is an HTTP client
- Status codes tell you what happened (200=good, 429=slow down, 403=blocked)
- Headers carry metadata about your request

### CORS Explained
- CORS is browser-only security
- Python/Node scrapers ignore CORS completely
- Use CORS restrictions to find hidden APIs

### Cookies & Sessions
- Use `requests.Session()` for multi-request scraping
- Extract CSRF tokens before form submissions
- Handle session expiration gracefully

### Headers & User-Agents
- User-Agent is the most important header
- Keep headers consistent (don't mix Chrome UA with Firefox hints)
- Update User-Agents regularly (browsers update monthly)

### JavaScript Rendering
- Check if content is in View Source vs. Inspect Element
- Find hidden APIs before using browser automation
- Playwright > Selenium for new projects

### Rate Limiting
- Random delays look more human than fixed delays
- Start slow, speed up until you see 429s
- Implement exponential backoff on failures

### Proxies & IP Rotation
- Datacenter proxies are cheap but detectable
- Residential proxies are expensive but stealthy
- Match proxy location to your headers

---

## 🛠️ Common Patterns

### Basic Request with Proper Headers

```python
import requests

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
})

response = session.get("https://example.com")
```

### Handling JavaScript Sites

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://spa-site.com")
    page.wait_for_selector("div.content")
    html = page.content()
    browser.close()
```

### Rate-Limited Scraping

```python
import time
import random

for url in urls:
    response = session.get(url)
    time.sleep(random.uniform(1, 3))  # Random delay
```

### Proxy Rotation

```python
import itertools

proxies = itertools.cycle(proxy_list)
for url in urls:
    proxy = next(proxies)
    response = session.get(url, proxies={"http": proxy, "https": proxy})
```

---

## 🔗 Related Sections

- **[00_terminology/](../00_terminology/)** - Definitions of terms used here
- **[02_anti_scraping_tech/](../02_anti_scraping_tech/)** - What you're up against
- **[04_tools_ecosystem/](../04_tools_ecosystem/)** - Libraries and tools

---

## 📊 Quick Reference Tables

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Parse response |
| 301/302 | Redirect | Follow (automatic) |
| 403 | Forbidden | Fix headers/proxy |
| 404 | Not Found | Skip URL |
| 429 | Rate Limited | Wait and retry |
| 5xx | Server Error | Retry later |

### When to Use Each Approach

| Situation | Solution |
|-----------|----------|
| Simple HTML pages | requests + BeautifulSoup |
| Login required | requests.Session with cookies |
| JavaScript content | Playwright |
| High volume | Proxies + rate limiting |
| Getting blocked | Better headers, proxies |

---

*Part of [00_foundations](../) - The complete web scraping knowledge base*
