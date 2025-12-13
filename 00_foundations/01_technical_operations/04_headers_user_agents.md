# Headers & User Agents

> **The Art of Looking Like a Real Browser**

Headers are the first thing anti-bot systems check. A request without proper headers screams "I'm a bot!" This document covers how to craft headers that blend in.

---

## Why Headers Matter

```
Default Python Request:
User-Agent: python-requests/2.28.0
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive

Real Browser Request:
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8
Accept-Language: en-US,en;q=0.9
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Sec-Ch-Ua: "Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1
Upgrade-Insecure-Requests: 1
```

**Which one looks like a bot?**

---

## 1. The User-Agent Header

### What It Is

The `User-Agent` header identifies the client making the request. It's the **#1 most checked header** by anti-bot systems.

### Anatomy of a User-Agent

```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
│           │                              │                                      │
│           │                              │                                      └─ Browser version
│           │                              └─ Rendering engine
│           └─ Operating system
└─ Mozilla compatibility token (historical)
```

### Common User-Agent Patterns

#### Chrome on Windows

```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

#### Chrome on Mac

```
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

#### Firefox on Windows

```
Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0
```

#### Safari on Mac

```
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15
```

#### Mobile Chrome (Android)

```
Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36
```

#### Mobile Safari (iPhone)

```
Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1
```

### User-Agent Rotation

```python
import random

USER_AGENTS = [
    # Chrome Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Chrome Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

# Use in requests
headers = {"User-Agent": get_random_user_agent()}
response = requests.get(url, headers=headers)
```

### Using fake-useragent Library

```python
from fake_useragent import UserAgent

ua = UserAgent()

# Random user agent
headers = {"User-Agent": ua.random}

# Specific browser
headers = {"User-Agent": ua.chrome}
headers = {"User-Agent": ua.firefox}
```

---

## 2. Essential Request Headers

### Complete Header Set

```python
def get_browser_headers(referer=None):
    """Generate realistic browser headers."""
    headers = {
        # Identity
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        
        # Content negotiation
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        
        # Connection
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        
        # Security headers (Chrome-specific)
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }
    
    if referer:
        headers["Referer"] = referer
    
    return headers

response = requests.get(url, headers=get_browser_headers())
```

### Header-by-Header Breakdown

| Header | Purpose | What to Set |
|--------|---------|-------------|
| `User-Agent` | Client identity | Real browser string |
| `Accept` | Acceptable content types | Match browser's value |
| `Accept-Language` | Preferred languages | `en-US,en;q=0.9` |
| `Accept-Encoding` | Compression support | `gzip, deflate, br` |
| `Referer` | Previous page | Logical referring page |
| `Connection` | Connection persistence | `keep-alive` |
| `Sec-Ch-Ua` | Client hints (Chrome) | Match Chrome version |
| `Sec-Fetch-*` | Fetch metadata | Indicates navigation type |

---

## 3. The Referer Header

### Why It Matters

Many sites check if the Referer makes sense:

```
❌ Suspicious:
Referer: (none) → Directly accessing deep page

✅ Normal:
Referer: https://example.com/category → Then accessing product page
```

### Setting Referer Correctly

```python
# Simulate natural navigation
session = requests.Session()

# Step 1: Visit homepage
homepage = session.get("https://example.com")

# Step 2: Visit category (referer = homepage)
category = session.get(
    "https://example.com/products",
    headers={"Referer": "https://example.com"}
)

# Step 3: Visit product (referer = category)
product = session.get(
    "https://example.com/products/123",
    headers={"Referer": "https://example.com/products"}
)
```

### Referer Policy Considerations

Some sites strip or validate Referer:

```python
# For cross-origin requests, Referer might be stripped
# For same-origin, it's usually sent in full

# You can set Referrer-Policy to control behavior:
headers = {
    "Referer": "https://example.com/page",
    # Some sites check this header too
}
```

---

## 4. Client Hints Headers

Modern Chrome sends additional "Client Hints" headers:

```python
CHROME_CLIENT_HINTS = {
    # User-Agent Client Hints
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",  # ?1 for mobile
    "Sec-Ch-Ua-Platform": '"Windows"',  # or "macOS", "Linux", "Android"
    
    # Fetch Metadata
    "Sec-Fetch-Dest": "document",  # or "image", "script", "style"
    "Sec-Fetch-Mode": "navigate",  # or "cors", "no-cors", "same-origin"
    "Sec-Fetch-Site": "none",  # "same-origin", "same-site", "cross-site"
    "Sec-Fetch-User": "?1",  # Present for user-initiated navigation
}
```

### Sec-Fetch-* Values

| Header | Value | Meaning |
|--------|-------|---------|
| `Sec-Fetch-Dest` | `document` | Main page navigation |
| | `image` | Image request |
| | `script` | JavaScript file |
| | `style` | CSS file |
| | `empty` | fetch() or XHR |
| `Sec-Fetch-Mode` | `navigate` | Page navigation |
| | `cors` | Cross-origin request |
| | `no-cors` | Simple request |
| | `same-origin` | Same-origin request |
| `Sec-Fetch-Site` | `none` | Direct URL entry/bookmark |
| | `same-origin` | Same origin |
| | `same-site` | Same site, different origin |
| | `cross-site` | Different site |

---

## 5. Headers for Different Request Types

### Page Navigation (GET)

```python
def get_navigation_headers(referer=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin" if referer else "none",
        "Sec-Fetch-User": "?1",
    }
    if referer:
        headers["Referer"] = referer
    return headers
```

### AJAX/API Request (GET JSON)

```python
def get_ajax_headers(referer):
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": referer,
        "X-Requested-With": "XMLHttpRequest",  # Indicates AJAX
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
```

### Form Submission (POST)

```python
def get_form_headers(referer):
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://example.com",
        "Referer": referer,
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
    }
```

### JSON API Request (POST)

```python
def get_api_headers(referer):
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Origin": "https://example.com",
        "Referer": referer,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
```

---

## 6. Header Consistency

### The Problem

Inconsistent headers can trigger detection:

```python
# ❌ Inconsistent - Chrome UA but Firefox Accept header
headers = {
    "User-Agent": "Mozilla/5.0 ... Chrome/120.0.0.0 ...",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",  # Firefox pattern
}

# ❌ Inconsistent - Desktop UA with mobile viewport
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ... Chrome/120.0.0.0",
    "Sec-Ch-Ua-Mobile": "?1",  # Claims mobile!
}
```

### Browser Profiles

Create consistent browser profiles:

```python
BROWSER_PROFILES = {
    "chrome_windows": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    },
    "chrome_mac": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"',
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    },
    "firefox_windows": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        # Firefox doesn't send Sec-Ch-Ua headers
    },
}

def get_profile_headers(profile="chrome_windows"):
    return BROWSER_PROFILES.get(profile, BROWSER_PROFILES["chrome_windows"]).copy()
```

---

## 7. Header Order

Some sophisticated detection looks at header order:

```python
# Real Chrome sends headers in this order:
CHROME_HEADER_ORDER = [
    "Host",
    "Connection",
    "sec-ch-ua",
    "sec-ch-ua-mobile",
    "sec-ch-ua-platform",
    "Upgrade-Insecure-Requests",
    "User-Agent",
    "Accept",
    "Sec-Fetch-Site",
    "Sec-Fetch-Mode",
    "Sec-Fetch-User",
    "Sec-Fetch-Dest",
    "Referer",
    "Accept-Encoding",
    "Accept-Language",
    "Cookie",
]

# Use OrderedDict or httpx for header order control
from collections import OrderedDict
import httpx

headers = OrderedDict([
    ("sec-ch-ua", '"Not_A Brand";v="8"...'),
    ("sec-ch-ua-mobile", "?0"),
    ("User-Agent", "Mozilla/5.0..."),
    # ... in correct order
])

# httpx preserves header order
response = httpx.get(url, headers=headers)
```

---

## 8. Common Mistakes

### ❌ Using Default User-Agent

```python
# Default reveals you're using requests
requests.get(url)  # User-Agent: python-requests/2.28.0
```

### ❌ Outdated User-Agent

```python
# Browser versions from years ago look suspicious
"Mozilla/5.0 (Windows NT 6.1; WOW64) Chrome/50.0.2661.102"
# Windows 7 + Chrome 50 from 2016? Suspicious.
```

### ❌ Bot-Like User-Agent Patterns

```python
# Obviously custom
"MyScraperBot/1.0"
"Mozilla/5.0 (compatible; MyCrawler/1.0)"
"python-urllib/3.8"
```

### ❌ Missing Standard Headers

```python
# Only User-Agent, nothing else
headers = {"User-Agent": "Mozilla/5.0..."}
# Real browsers send many more headers
```

### ❌ Wrong Headers for Request Type

```python
# JSON Content-Type for HTML page request
headers = {"Content-Type": "application/json"}
response = requests.get(html_page, headers=headers)
```

---

## 9. Keeping User-Agents Current

Browser versions update frequently. Keep your User-Agents fresh:

```python
# Check current browser versions at:
# https://www.whatismybrowser.com/guides/the-latest-user-agent/
# https://developers.whatismybrowser.com/useragents/explore/

# Or extract from your own browser:
# 1. Open DevTools (F12)
# 2. Go to Network tab
# 3. Load any page
# 4. Click request, find User-Agent in headers
```

### Auto-Update Script

```python
import requests
from bs4 import BeautifulSoup

def get_latest_chrome_ua():
    """Fetch latest Chrome user agent from whatismybrowser.com"""
    url = "https://www.whatismybrowser.com/guides/the-latest-user-agent/chrome"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    ua_span = soup.select_one(".code")
    return ua_span.text if ua_span else None
```

---

## Summary

### Minimum Headers for Scraping

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}
```

### Full Stealth Headers

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}
```

### Key Principles

1. **Always set a current User-Agent**
2. **Keep headers consistent with claimed browser**
3. **Set appropriate Referer for navigation flows**
4. **Include Sec-Fetch-* headers for Chrome impersonation**
5. **Rotate User-Agents if scraping at scale**

---

*Next: [05_javascript_rendering_spa.md](05_javascript_rendering_spa.md) - Handling JavaScript-heavy websites*
