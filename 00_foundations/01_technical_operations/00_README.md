# 01_technical_operations

> **How the Web Works for Scrapers**

Before scraping any website, you need to understand the technical infrastructure that powers the web. This section covers everything from HTTP fundamentals to advanced proxy management.

---

## 📚 Documents in This Section

| # | Document | Lines | Description |
|---|----------|-------|-------------|
| 01 | [HTTP Requests Anatomy](01_http_requests_anatomy.md) | 594 | Request/response structure, methods, headers, status codes |
| 02 | [CORS Explained](02_cors_explained.md) | 340 | Why browsers block requests (and why scrapers don't care) |
| 03 | [Cookies, Sessions & State](03_cookies_sessions_state.md) | 511 | Managing authentication and state across requests |
| 04 | [Headers & User Agents](04_headers_user_agents.md) | 573 | Crafting headers that don't get you blocked |
| 05 | [JavaScript Rendering & SPAs](05_javascript_rendering_spa.md) | 593 | Handling JavaScript-heavy websites |
| 06 | [Rate Limiting & Throttling](06_rate_limiting_throttling.md) | 594 | Controlling request speed respectfully |
| 07 | [Proxies & IP Rotation](07_proxies_rotation_ips.md) | 643 | Managing IP addresses at scale |

**Total: 3,848 lines of technical knowledge**

---

## 🎯 Reading Order

**For beginners**, read in order:
1. **HTTP Requests** - Foundation of all web communication
2. **CORS** - Know what's browser-only vs. server-enforced
3. **Cookies & Sessions** - Essential for authenticated scraping
4. **Headers & User Agents** - The #1 factor in avoiding detection
5. **JavaScript Rendering** - When static scraping isn't enough
6. **Rate Limiting** - How to be a polite scraper
7. **Proxies** - Scaling to thousands of requests

**Reference use**: Jump directly to what you need.

---

## 🔑 Key Takeaways

### From HTTP Requests Anatomy
- Every scrape is a request-response cycle
- Status codes tell you what happened
- Headers carry critical metadata
- POST for forms, GET for pages

### From CORS Explained
- CORS is browser-only enforcement
- Python/Node scripts bypass CORS entirely
- Only matters when using browser automation

### From Cookies & Sessions
- Use `requests.Session()` for related requests
- Extract CSRF tokens fresh before form submissions
- Handle session expiration gracefully

### From Headers & User Agents
- Always set a realistic User-Agent
- Keep headers consistent with claimed browser
- Add Sec-Fetch-* headers for Chrome impersonation

### From JavaScript Rendering
- Try static extraction first (always faster)
- Look for embedded JSON (`__NEXT_DATA__`)
- Find hidden APIs via DevTools Network tab
- Use Playwright/Puppeteer only when necessary

### From Rate Limiting
- Start slow and adapt
- Respect `Retry-After` headers
- Add randomness to avoid detection
- Implement exponential backoff

### From Proxies
- Datacenter = cheap but detectable
- Residential = trusted but expensive
- Rotate intelligently based on failures
- Match proxy type to target protection level

---

## 🛠️ Quick Reference Code

### Minimal Scraping Setup

```python
import requests
from bs4 import BeautifulSoup
import time
import random

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
})

for url in urls:
    response = session.get(url)
    
    if response.status_code == 429:
        time.sleep(int(response.headers.get("Retry-After", 60)))
        response = session.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        # Extract data...
    
    time.sleep(random.uniform(1, 2))
```

### With Proxy Rotation

```python
import random

proxies = ["http://proxy1:8080", "http://proxy2:8080", "http://proxy3:8080"]

for url in urls:
    proxy = random.choice(proxies)
    response = session.get(url, proxies={"http": proxy, "https": proxy})
    # ...
```

### With JavaScript Rendering

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url)
    page.wait_for_selector("div.content")
    html = page.content()
    # Parse with BeautifulSoup...
    browser.close()
```

---

## ➡️ Next Section

Now that you understand how the web works technically, learn about:

**[02_anti_scraping_tech/](../02_anti_scraping_tech/)** - What websites deploy to stop you (CAPTCHAs, fingerprinting, bot detection, and how to work around them)

---

*Part of [00_foundations](../) - The complete web scraping knowledge base*
