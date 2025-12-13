# Headers & User-Agents

> **Looking Like a Real Browser**

Request headers are your scraper's identity card. The wrong headers scream "I'm a bot!" while the right ones help you blend in with legitimate traffic.

---

## Why Headers Matter

```python
# This gets blocked
requests.get("https://protected-site.com")
# User-Agent: python-requests/2.28.0  ← OBVIOUS BOT

# This works
requests.get("https://protected-site.com", headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
})
```

Sites check headers to:
- Block known bot signatures
- Detect automation tools
- Enforce access policies
- Track and fingerprint visitors

---

## 1. Essential Headers

### The Minimum Viable Header Set

```python
headers = {
    # CRITICAL - Most checked header
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    
    # IMPORTANT - What content you accept
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    
    # RECOMMENDED - Looks more like a browser
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
```

### Full Browser-Like Headers

```python
headers = {
    # Identity
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    
    # Content negotiation
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    
    # Connection
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    
    # Cache
    "Cache-Control": "max-age=0",
    
    # Security hints
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    
    # Privacy
    "DNT": "1",  # Do Not Track
    
    # Chrome-specific
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}
```

---

## 2. User-Agent Deep Dive

### Anatomy of a User-Agent

```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
│          │                              │                                      │                  │
│          │                              │                                      │                  └── Safari compatibility
│          │                              │                                      └── Chrome version
│          │                              └── Rendering engine (WebKit)
│          └── Operating system and architecture
└── Mozilla compatibility token (historical)
```

### Current User-Agents (2024)

#### Chrome (Windows)
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

#### Chrome (Mac)
```
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

#### Chrome (Linux)
```
Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

#### Firefox (Windows)
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0
```

#### Firefox (Mac)
```
Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0
```

#### Safari (Mac)
```
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15
```

#### Edge (Windows)
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0
```

#### Mobile Chrome (Android)
```
Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36
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
    # Firefox Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Firefox Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Safari Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

# Usage
headers = {"User-Agent": get_random_user_agent()}
```

### Keeping User-Agents Current

User-Agents become stale as browsers update. Options:

```python
# 1. Use a library
from fake_useragent import UserAgent
ua = UserAgent()
headers = {"User-Agent": ua.random}

# 2. Fetch from online list
def fetch_latest_user_agents():
    # https://www.whatismybrowser.com/guides/the-latest-user-agent/
    pass

# 3. Extract from your own browser
# DevTools → Network → Any request → User-Agent header
```

---

## 3. Header Categories

### Content Negotiation Headers

Tell server what formats you accept:

```python
# For HTML pages
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
}

# For JSON APIs
headers = {
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
}

# For images
headers = {
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
}
```

### Navigation Headers

Indicate how you arrived at the page:

```python
# First visit to site
headers = {
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",        # Not from another site
    "Sec-Fetch-User": "?1",          # User-initiated
}

# Clicking a link within site
headers = {
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin", # From same site
    "Sec-Fetch-User": "?1",
    "Referer": "https://example.com/page1",
}

# Coming from Google
headers = {
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",  # From different site
    "Sec-Fetch-User": "?1",
    "Referer": "https://www.google.com/",
}
```

### AJAX Request Headers

For XHR/Fetch requests:

```python
headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",  # Classic AJAX marker
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}
```

### POST Request Headers

```python
# Form submission
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://example.com",
    "Referer": "https://example.com/form",
}

# JSON API
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Origin": "https://example.com",
}
```

---

## 4. The Referer Header

### Why It Matters

Sites check Referer to:
- Prevent hotlinking
- Verify navigation flow
- Detect direct access to "internal" pages
- Track traffic sources

### Referer Patterns

```python
# Direct visit (no referer)
headers = {}
# Looks like: User typed URL or used bookmark

# From search engine
headers = {"Referer": "https://www.google.com/"}
# Looks like: User found page via Google

# From within site
headers = {"Referer": "https://example.com/products"}
# Looks like: User clicked from products page

# From external link
headers = {"Referer": "https://blog.example.com/article"}
# Looks like: User clicked from a blog post
```

### Building Realistic Referer Chains

```python
class ReferrerChain:
    def __init__(self, start_url):
        self.current_referer = None
        self.visit(start_url)
    
    def visit(self, url):
        """Return headers for visiting URL, update referer."""
        headers = {}
        if self.current_referer:
            headers["Referer"] = self.current_referer
        self.current_referer = url
        return headers

# Usage - realistic navigation
chain = ReferrerChain("https://example.com/")
session.get("https://example.com/", headers=chain.visit("https://example.com/"))
session.get("https://example.com/products", headers=chain.visit("https://example.com/products"))
session.get("https://example.com/products/123", headers=chain.visit("https://example.com/products/123"))
```

---

## 5. Client Hints (Modern Chrome)

Chrome sends additional headers called Client Hints:

```python
# sec-ch-* headers
headers = {
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    
    # Extended hints (if requested by server)
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version-list": '"Not_A Brand";v="8.0.0.0", "Chromium";v="120.0.6099.130", "Google Chrome";v="120.0.6099.130"',
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform-version": '"15.0.0"',
}
```

### Matching User-Agent and Client Hints

```python
# WRONG - Mismatched
headers = {
    "User-Agent": "...Chrome/120...",
    "sec-ch-ua": '"Chrome";v="119"',  # Version mismatch!
}

# RIGHT - Consistent
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}
```

---

## 6. Header Consistency

### The Consistency Principle

Your headers should tell a consistent story. Mismatches trigger detection.

```python
# BAD - Inconsistent
headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; ...",  # Mobile
    "sec-ch-ua-platform": '"Windows"',          # Desktop!
    "Accept-Language": "zh-CN",                 # Chinese
}

# GOOD - Consistent desktop profile
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Accept-Language": "en-US,en;q=0.9",
}
```

### Browser Profiles

```python
BROWSER_PROFILES = {
    "chrome_windows": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    },
    "chrome_mac": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
    },
    "firefox_windows": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        # Firefox doesn't send sec-ch-ua headers
    },
}

def get_headers(profile="chrome_windows"):
    return BROWSER_PROFILES[profile].copy()
```

---

## 7. Headers to Avoid

### Headers That Expose Bots

```python
# DON'T include these (or use carefully)
bad_headers = {
    # Automation frameworks
    "User-Agent": "Scrapy/2.8.0",
    "User-Agent": "python-requests/2.28.0",
    "User-Agent": "curl/7.68.0",
    "User-Agent": "Java/1.8.0_201",
    
    # Outdated browsers
    "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0)",
    
    # Proxy indicators
    "X-Forwarded-For": "...",
    "Via": "...",
    
    # Too honest
    "X-Scraper": "my-scraper",
}
```

### Headers Some Sites Check

```python
# These might be checked for presence/absence
conditional_headers = {
    "Connection": "keep-alive",      # Browsers always send this
    "Upgrade-Insecure-Requests": "1", # Modern browsers send this
    "DNT": "1",                       # Do Not Track
    "Cache-Control": "max-age=0",    # Often present on refresh
}
```

---

## 8. Complete Examples

### Standard Page Request

```python
def get_page(session, url, referer=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin" if referer else "none",
        "Sec-Fetch-User": "?1",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }
    
    if referer:
        headers["Referer"] = referer
    
    return session.get(url, headers=headers)
```

### API Request

```python
def api_request(session, url, referer):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Referer": referer,
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }
    
    return session.get(url, headers=headers)
```

---

## Summary

| Header | Purpose | Priority |
|--------|---------|----------|
| **User-Agent** | Identify browser | Critical |
| **Accept** | Content types | High |
| **Accept-Language** | Language preference | Medium |
| **Accept-Encoding** | Compression | Medium |
| **Referer** | Navigation source | Situational |
| **sec-ch-ua*** | Client hints | High (Chrome) |
| **Sec-Fetch-*** | Request context | Medium |

### Key Takeaways

1. **User-Agent is most important** - Always use a current browser UA
2. **Stay consistent** - All headers should match the same browser profile
3. **Rotate when needed** - Different UAs for different sessions
4. **Update regularly** - Browser versions change every few weeks
5. **Match the context** - Different headers for pages vs APIs

---

*Next: [05_javascript_rendering_spa.md](05_javascript_rendering_spa.md) - Handling JavaScript-dependent content*
