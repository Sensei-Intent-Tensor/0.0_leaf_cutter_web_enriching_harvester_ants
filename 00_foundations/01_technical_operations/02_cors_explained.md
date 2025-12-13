# CORS Explained

> **Why Browsers Block Requests (And Why Scrapers Don't Care)**

Cross-Origin Resource Sharing (CORS) is one of the most confusing web concepts. The good news for scrapers: it mostly doesn't apply to you. But understanding it helps you know what's browser-only vs. server-enforced.

---

## The Short Version

| Context | CORS Applies? | Why |
|---------|---------------|-----|
| **Browser JavaScript** | ✅ Yes | Browser enforces it |
| **Python/Node Scripts** | ❌ No | No browser = no CORS |
| **curl/wget** | ❌ No | Command line ignores CORS |
| **Headless Browser** | ✅ Yes | Still a browser |

**If you're using `requests`, `httpx`, or `scrapy`, CORS doesn't block you.**

---

## What Is CORS?

CORS is a **browser security mechanism** that restricts web pages from making requests to different domains than the one serving the page.

### The Same-Origin Policy

Browsers enforce the "Same-Origin Policy":

```
Origin = Protocol + Host + Port

https://example.com:443/page
  │         │         │
  └─────────┴─────────┴── Must all match for "same origin"
```

#### Same Origin Examples

| Page | Request To | Same Origin? |
|------|------------|--------------|
| `https://example.com/a` | `https://example.com/b` | ✅ Yes |
| `https://example.com` | `https://api.example.com` | ❌ No (different host) |
| `https://example.com` | `http://example.com` | ❌ No (different protocol) |
| `https://example.com:443` | `https://example.com:8080` | ❌ No (different port) |

---

## How CORS Works

### Without CORS (Blocked)

```
┌─────────────────┐         ┌─────────────────┐
│  Browser on     │         │  api.other.com  │
│  example.com    │────────▶│                 │
│                 │         │  "Who are you?  │
│  JavaScript:    │◀────────│   Not allowed!" │
│  fetch(other)   │         │                 │
└─────────────────┘         └─────────────────┘
        │
        ▼
   ❌ BLOCKED BY BROWSER
```

### With CORS Headers (Allowed)

```
┌─────────────────┐         ┌─────────────────┐
│  Browser on     │         │  api.other.com  │
│  example.com    │────────▶│                 │
│                 │         │  Response +     │
│  JavaScript:    │◀────────│  CORS Headers   │
│  fetch(other)   │         │                 │
└─────────────────┘         └─────────────────┘
        │
        ▼
   ✅ ALLOWED (headers permit it)
```

### The CORS Headers

Server responses include headers that tell the browser what's allowed:

```http
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 86400
```

| Header | Meaning |
|--------|---------|
| `Access-Control-Allow-Origin` | Which origins can access (or `*` for any) |
| `Access-Control-Allow-Methods` | Which HTTP methods are allowed |
| `Access-Control-Allow-Headers` | Which request headers are allowed |
| `Access-Control-Allow-Credentials` | Whether cookies/auth can be sent |
| `Access-Control-Max-Age` | How long to cache preflight response |

---

## Preflight Requests

For "complex" requests, browsers send a preflight OPTIONS request first:

```
Step 1: Browser sends OPTIONS (preflight)
────────────────────────────────────────▶
OPTIONS /api/data HTTP/1.1
Origin: https://example.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Content-Type

Step 2: Server responds with permissions
◀────────────────────────────────────────
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Methods: POST
Access-Control-Allow-Headers: Content-Type

Step 3: Browser sends actual request
────────────────────────────────────────▶
POST /api/data HTTP/1.1
Origin: https://example.com
Content-Type: application/json
```

### When Preflight Occurs

"Simple" requests (no preflight):
- Methods: GET, HEAD, POST
- Headers: Only Accept, Accept-Language, Content-Language, Content-Type
- Content-Type: Only `application/x-www-form-urlencoded`, `multipart/form-data`, `text/plain`

"Complex" requests (preflight required):
- Methods: PUT, DELETE, PATCH
- Custom headers: Authorization, X-Custom-Header
- Content-Type: `application/json`

---

## Why Scrapers Bypass CORS

CORS is enforced by **browsers**, not servers. When you use Python:

```python
import requests

# This works fine - no browser, no CORS
response = requests.get("https://api.other.com/data")
print(response.json())  # ✅ Success
```

The server sends the same response regardless of CORS headers. The browser just refuses to show it to JavaScript if headers are missing.

```
Browser:
┌────────────────────────────────────────────────────────┐
│  JavaScript                                            │
│       │                                                │
│       ▼                                                │
│  fetch("https://api.other.com")                        │
│       │                                                │
│       ▼                                                │
│  ┌─────────────────────────────────────┐               │
│  │  CORS Check (Browser Security)      │               │
│  │  "Does response allow this origin?" │               │
│  │  No? → Block JavaScript access      │               │
│  └─────────────────────────────────────┘               │
└────────────────────────────────────────────────────────┘

Python Script:
┌────────────────────────────────────────────────────────┐
│  requests.get("https://api.other.com")                 │
│       │                                                │
│       ▼                                                │
│  Direct HTTP Request (No CORS Check)                   │
│       │                                                │
│       ▼                                                │
│  ✅ Response received and accessible                   │
└────────────────────────────────────────────────────────┘
```

---

## When CORS Does Affect Scraping

### Headless Browsers

If you're using Playwright/Puppeteer to execute JavaScript:

```javascript
// This runs in a real browser - CORS applies!
const response = await page.evaluate(async () => {
    const res = await fetch("https://api.other.com/data");
    return await res.json();  // May be blocked by CORS
});
```

**Solution**: Intercept requests and make them from Python instead:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    
    # Intercept the API call and handle it outside the browser
    def handle_route(route):
        if "api.other.com" in route.request.url:
            # Make request from Python (no CORS)
            import requests
            response = requests.get(route.request.url)
            route.fulfill(body=response.text)
        else:
            route.continue_()
    
    page.route("**/*", handle_route)
    page.goto("https://example.com")
```

### Building Browser Extensions

Browser extensions have different CORS rules, but this is outside typical scraping scope.

---

## CORS vs. Other Protections

Don't confuse CORS with server-side protections:

| Protection | Where Enforced | Affects Scrapers? |
|------------|----------------|-------------------|
| **CORS** | Browser | ❌ No (unless using browser) |
| **Rate Limiting** | Server | ✅ Yes |
| **IP Blocking** | Server | ✅ Yes |
| **Authentication** | Server | ✅ Yes |
| **Bot Detection** | Server | ✅ Yes |
| **robots.txt** | Honor system | Depends on you |

---

## Practical Scenarios

### Scenario 1: API Endpoint Returns Data

```python
# Browser JavaScript would be blocked by CORS
# Python works fine
response = requests.get("https://api.site.com/products")
products = response.json()  # ✅ Works
```

### Scenario 2: Hidden API Discovery

You find a website's JavaScript making API calls:

```javascript
// In browser console, you see:
// GET https://api.site.com/internal/data
// But your browser extension can't access it due to CORS
```

```python
# Your scraper can access it directly:
response = requests.get(
    "https://api.site.com/internal/data",
    headers={"Authorization": "Bearer TOKEN"}
)
# ✅ No CORS blocking
```

### Scenario 3: Headless Browser Needs Data

```python
from playwright.sync_api import sync_playwright
import requests

# Get data from API directly (bypass CORS)
api_data = requests.get("https://api.site.com/data").json()

# Use headless browser only for rendering
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://site.com")
    
    # Inject the data we already have
    page.evaluate(f"window.apiData = {json.dumps(api_data)}")
```

---

## Common Misconceptions

### ❌ "CORS blocks my scraper"

No, CORS only blocks **browser JavaScript**. If you're using Python, Node.js scripts, curl, etc., CORS doesn't apply.

### ❌ "I need to add CORS headers to my requests"

CORS headers are **response** headers from the **server**. You can't add them to your requests to bypass anything.

### ❌ "Setting `Access-Control-Allow-Origin: *` is dangerous"

Only dangerous for the **server** allowing it, not for you. It means any website's JavaScript can access that API.

### ❌ "CORS is a security feature that protects data"

CORS protects **users** from malicious websites accessing APIs on their behalf. It doesn't protect the data itself from determined scrapers.

---

## Summary

| Key Point | Details |
|-----------|---------|
| **What CORS is** | Browser security policy restricting cross-origin requests |
| **Who enforces it** | Browsers only |
| **Effect on scrapers** | None (unless using browser automation) |
| **Workaround** | Use non-browser HTTP clients (requests, httpx) |

### Decision Tree

```
Are you using a browser (Puppeteer/Playwright)?
├── No → CORS doesn't apply, proceed normally
└── Yes → Making cross-origin fetch in page?
    ├── No → CORS doesn't apply
    └── Yes → Options:
        ├── Make request from Python instead
        ├── Use request interception
        └── Find the data another way
```

---

*Next: [03_cookies_sessions_state.md](03_cookies_sessions_state.md) - Managing state across requests*
