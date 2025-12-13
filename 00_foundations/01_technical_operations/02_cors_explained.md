# CORS Explained

> **Why Browsers Block Requests and Why Scrapers Don't Care**

CORS (Cross-Origin Resource Sharing) is one of the most misunderstood concepts in web development. Understanding it will help you realize why your browser can't do what your Python scraper does easily.

---

## The Short Answer

**CORS is a browser security feature. Scrapers aren't browsers, so CORS doesn't affect them.**

If you're writing a Python/Node.js scraper, you can skip this document—CORS won't stop you. But understanding it helps you:
- Debug browser-based tools
- Understand why some approaches fail in browsers
- Find hidden APIs that browsers can't access directly

---

## What is CORS?

### The Same-Origin Policy

Browsers implement the **Same-Origin Policy**: scripts from one origin cannot access resources from a different origin.

**Origin** = Scheme + Host + Port

```
https://www.example.com:443/page
│       │               │
Scheme  Host            Port
```

### Same Origin Examples

| URL A | URL B | Same Origin? |
|-------|-------|--------------|
| `https://example.com/a` | `https://example.com/b` | ✅ Yes |
| `https://example.com` | `https://www.example.com` | ❌ No (different host) |
| `https://example.com` | `http://example.com` | ❌ No (different scheme) |
| `https://example.com:443` | `https://example.com:8080` | ❌ No (different port) |
| `https://example.com` | `https://api.example.com` | ❌ No (different subdomain) |

### What Same-Origin Policy Blocks

In a browser, JavaScript on `https://mysite.com` CANNOT:
- Fetch data from `https://api.othersite.com`
- Read cookies from `https://othersite.com`
- Access iframe content from different origin

```javascript
// This fails in browser due to Same-Origin Policy
fetch('https://api.othersite.com/data')
  .then(r => r.json())  // CORS error!
```

---

## CORS: The Exception System

CORS allows servers to specify which origins CAN access their resources.

### How CORS Works

```
Browser                                  Server
   │                                        │
   │  1. Preflight Request (OPTIONS)        │
   │  Origin: https://mysite.com            │
   │  ──────────────────────────────────▶   │
   │                                        │
   │  2. Preflight Response                 │
   │  Access-Control-Allow-Origin: *        │
   │  ◀──────────────────────────────────   │
   │                                        │
   │  3. Actual Request (GET/POST)          │
   │  Origin: https://mysite.com            │
   │  ──────────────────────────────────▶   │
   │                                        │
   │  4. Response with CORS headers         │
   │  Access-Control-Allow-Origin: *        │
   │  ◀──────────────────────────────────   │
   │                                        │
   ▼  Browser allows JavaScript to read     ▼
```

### CORS Headers

#### Response Headers (Server → Browser)

| Header | Purpose | Example |
|--------|---------|---------|
| `Access-Control-Allow-Origin` | Allowed origins | `*` or `https://mysite.com` |
| `Access-Control-Allow-Methods` | Allowed HTTP methods | `GET, POST, PUT` |
| `Access-Control-Allow-Headers` | Allowed request headers | `Content-Type, Authorization` |
| `Access-Control-Allow-Credentials` | Allow cookies | `true` |
| `Access-Control-Max-Age` | Cache preflight (seconds) | `86400` |
| `Access-Control-Expose-Headers` | Headers JS can read | `X-Custom-Header` |

#### Request Headers (Browser → Server)

| Header | Purpose | Example |
|--------|---------|---------|
| `Origin` | Requesting origin | `https://mysite.com` |
| `Access-Control-Request-Method` | Method for actual request | `POST` |
| `Access-Control-Request-Headers` | Headers for actual request | `Content-Type` |

### Simple Requests vs Preflight

#### Simple Requests (No Preflight)

Requests that don't trigger preflight:
- Methods: GET, HEAD, POST
- Headers: Only Accept, Accept-Language, Content-Language, Content-Type
- Content-Type: Only `application/x-www-form-urlencoded`, `multipart/form-data`, `text/plain`

#### Preflight Required

Any request with:
- Methods: PUT, DELETE, PATCH
- Custom headers: `Authorization`, `X-Custom-Header`
- Content-Type: `application/json`

```
Preflight: OPTIONS /api/data
├── Access-Control-Request-Method: POST
├── Access-Control-Request-Headers: Content-Type, Authorization
└── Origin: https://mysite.com

Response:
├── Access-Control-Allow-Origin: https://mysite.com
├── Access-Control-Allow-Methods: POST, GET, OPTIONS
├── Access-Control-Allow-Headers: Content-Type, Authorization
└── Access-Control-Max-Age: 86400
```

---

## Why Scrapers Don't Care About CORS

### CORS is Browser-Only

```
┌─────────────────────────────────────────────────────────────┐
│                        BROWSER                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │ JavaScript  │───▶│ CORS Check  │───▶│   Server    │    │
│  │   Code      │    │  (Browser)  │    │             │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│                            │                               │
│                     BLOCKED IF NO                          │
│                     CORS HEADERS                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        SCRAPER                              │
│  ┌─────────────┐                       ┌─────────────┐    │
│  │   Python    │──────────────────────▶│   Server    │    │
│  │  requests   │                       │             │    │
│  └─────────────┘                       └─────────────┘    │
│                                                            │
│                    NO CORS CHECK!                          │
│                    DIRECT ACCESS                           │
└─────────────────────────────────────────────────────────────┘
```

### Python Doesn't Implement CORS

```python
import requests

# This works perfectly - no CORS in Python
response = requests.get("https://api.anysite.com/data")
print(response.json())  # Success!

# The server may still require authentication,
# but CORS headers are completely ignored
```

### curl Doesn't Implement CORS

```bash
# Works fine - curl ignores CORS
curl https://api.anysite.com/data

# CORS is purely a browser security feature
```

---

## When CORS Matters for Scrapers

### 1. Browser-Based Scraping Tools

If using browser automation in a way that relies on JavaScript:

```javascript
// Puppeteer/Playwright page.evaluate() runs in browser context
await page.evaluate(async () => {
    // This IS subject to CORS!
    const response = await fetch('https://other-api.com/data');
    return response.json();  // May fail due to CORS
});
```

**Solution**: Make requests from Node.js/Python, not from page context.

### 2. Understanding Hidden APIs

Sites often have internal APIs that browsers can access due to same-origin:

```
Website: https://example.com
│
├── Page: https://example.com/products
│   └── JavaScript fetches: https://example.com/api/products
│       └── Same origin, no CORS needed!
│
└── Your scraper can call: https://example.com/api/products
    └── Directly, ignoring that it was "meant" for same-origin only
```

**This is a goldmine for scrapers**: Find the JSON API the site uses internally.

### 3. CORS Headers Reveal API Usage

When inspecting network requests:

```
Response Headers:
Access-Control-Allow-Origin: https://example.com
```

This tells you:
- The API exists and is used by the frontend
- It's restricted to their domain (in browser)
- Your scraper can access it anyway!

---

## Finding Hidden APIs

### Using Browser DevTools

1. Open DevTools → Network tab
2. Filter by XHR/Fetch
3. Browse the site normally
4. Watch for JSON responses
5. Copy the API URL

```
Name                    Method    Status    Type
/api/products           GET       200       json
/api/products/123       GET       200       json
/api/search?q=test      GET       200       json
```

### Example: E-commerce Site

```
# What you see in browser
https://store.com/products

# What the browser fetches (found via DevTools)
https://store.com/api/v2/products?category=shoes&page=1

# Your scraper can call directly
response = requests.get(
    "https://store.com/api/v2/products",
    params={"category": "shoes", "page": 1},
    headers={"Accept": "application/json"}
)
products = response.json()  # Clean JSON data!
```

---

## CORS-Like Restrictions That DO Affect Scrapers

While CORS itself doesn't affect scrapers, servers can implement similar restrictions:

### 1. Origin Header Checking

```python
# Server may check Origin header
response = requests.get(url, headers={
    "Origin": "https://legitimate-site.com"
})
```

### 2. Referer Checking

```python
# Server may require specific Referer
response = requests.get(url, headers={
    "Referer": "https://example.com/products"
})
```

### 3. Host Header Checking

```python
# Server may check Host header
response = requests.get(url, headers={
    "Host": "api.example.com"
})
```

### 4. Custom Header Requirements

```python
# Some APIs require specific headers (not CORS, just API design)
response = requests.get(url, headers={
    "X-Requested-With": "XMLHttpRequest",
    "X-API-Version": "2.0"
})
```

---

## Practical Example: Bypassing "CORS"

### Scenario

You find an API via DevTools:
```
https://api.store.com/products
```

Browser shows: `Access-Control-Allow-Origin: https://store.com`

### What This Means

- Browser JavaScript on other sites can't access it
- YOUR SCRAPER CAN ACCESS IT FINE

### Code

```python
import requests

# Direct access - CORS doesn't apply
response = requests.get(
    "https://api.store.com/products",
    headers={
        "User-Agent": "Mozilla/5.0...",
        "Accept": "application/json",
        # Optionally add these if server checks:
        "Origin": "https://store.com",
        "Referer": "https://store.com/",
    }
)

data = response.json()
print(f"Found {len(data['products'])} products")
```

---

## Summary

| Aspect | Browser | Scraper |
|--------|---------|---------|
| Same-Origin Policy | ✅ Enforced | ❌ Not applicable |
| CORS headers | ✅ Required for cross-origin | ❌ Ignored |
| Preflight requests | ✅ Automatic | ❌ Not sent |
| Access to any URL | ❌ Restricted | ✅ Full access |

### Key Takeaways

1. **CORS is browser-only** - Python/Node scrapers ignore it completely
2. **CORS-blocked APIs are accessible** - If you find a JSON API via DevTools, your scraper can call it
3. **CORS reveals useful APIs** - Use it as a discovery tool
4. **Server-side checks still apply** - Auth, rate limits, IP blocks still work

---

*Next: [03_cookies_sessions_state.md](03_cookies_sessions_state.md) - Managing state across requests*
