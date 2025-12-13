# HTTP Requests Anatomy

> **Understanding the Foundation of All Web Scraping**

Every web scraper is, at its core, an HTTP client. Understanding HTTP requests and responses is essential for debugging issues, bypassing blocks, and building robust scrapers.

---

## The HTTP Request-Response Cycle

```
┌──────────────┐                           ┌──────────────┐
│    CLIENT    │                           │    SERVER    │
│  (Scraper)   │                           │  (Website)   │
└──────┬───────┘                           └──────┬───────┘
       │                                          │
       │  1. HTTP REQUEST                         │
       │  ─────────────────────────────────────▶  │
       │  GET /products/123 HTTP/1.1              │
       │  Host: example.com                       │
       │  User-Agent: Mozilla/5.0...              │
       │                                          │
       │                                          │
       │  2. HTTP RESPONSE                        │
       │  ◀─────────────────────────────────────  │
       │  HTTP/1.1 200 OK                         │
       │  Content-Type: text/html                 │
       │  <html>...</html>                        │
       │                                          │
```

---

## 1. HTTP Request Structure

Every HTTP request has four components:

```
┌─────────────────────────────────────────────────────────────┐
│ REQUEST LINE                                                │
│ GET /products/123?color=blue HTTP/1.1                       │
├─────────────────────────────────────────────────────────────┤
│ HEADERS                                                     │
│ Host: www.example.com                                       │
│ User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)...   │
│ Accept: text/html,application/xhtml+xml                     │
│ Accept-Language: en-US,en;q=0.9                            │
│ Accept-Encoding: gzip, deflate, br                         │
│ Cookie: session=abc123; user_id=456                        │
│ Referer: https://www.example.com/products                  │
├─────────────────────────────────────────────────────────────┤
│ BLANK LINE (separates headers from body)                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ BODY (optional, used in POST/PUT)                          │
│ {"product_id": 123, "quantity": 2}                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Request Line

### Structure
```
METHOD SP REQUEST-URI SP HTTP-VERSION CRLF
```

### Example
```
GET /products/123?color=blue&size=large HTTP/1.1
│   │                                   │
│   │                                   └── Protocol version
│   └── Path + Query string
└── HTTP Method
```

### HTTP Methods

| Method | Purpose | Has Body | Idempotent | Scraping Use |
|--------|---------|----------|------------|--------------|
| **GET** | Retrieve data | No | Yes | 95% of scraping |
| **POST** | Submit data | Yes | No | Forms, search, login |
| **PUT** | Update/replace | Yes | Yes | Rare |
| **PATCH** | Partial update | Yes | No | Rare |
| **DELETE** | Remove | Optional | Yes | Rare |
| **HEAD** | Get headers only | No | Yes | Check if page exists |
| **OPTIONS** | Get allowed methods | No | Yes | CORS preflight |

### GET vs POST in Scraping

```python
# GET - Data in URL (query parameters)
requests.get("https://example.com/search", params={
    "q": "python",
    "page": 1
})
# Results in: https://example.com/search?q=python&page=1

# POST - Data in body
requests.post("https://example.com/search", data={
    "q": "python",
    "page": 1
})
# URL stays: https://example.com/search
# Data sent in request body
```

---

## 3. URL Structure

```
https://www.example.com:443/products/shoes?color=red&size=10#reviews
│       │               │   │              │                  │
│       │               │   │              │                  └── Fragment
│       │               │   │              └── Query string
│       │               │   └── Path
│       │               └── Port (optional, 443 is default for HTTPS)
│       └── Host (domain)
└── Scheme (protocol)
```

### Query String Parameters

```python
# Building URLs with parameters
from urllib.parse import urlencode, urljoin

base = "https://example.com/search"
params = {
    "q": "web scraping",
    "page": 1,
    "sort": "relevance",
    "filters[]": ["price", "rating"]  # Array parameter
}

# Method 1: requests handles it
response = requests.get(base, params=params)
print(response.url)
# https://example.com/search?q=web+scraping&page=1&sort=relevance&filters%5B%5D=price&filters%5B%5D=rating

# Method 2: Manual encoding
query = urlencode(params, doseq=True)
full_url = f"{base}?{query}"
```

### URL Encoding

Special characters must be encoded:

| Character | Encoded | Meaning |
|-----------|---------|---------|
| Space | `%20` or `+` | Space in query |
| `&` | `%26` | Parameter separator |
| `=` | `%3D` | Key-value separator |
| `?` | `%3F` | Query start |
| `/` | `%2F` | Path separator |
| `#` | `%23` | Fragment |

```python
from urllib.parse import quote, quote_plus

# Path encoding (keeps /)
quote("/path/to/page", safe="/")  # /path/to/page

# Query encoding (spaces as +)
quote_plus("hello world")  # hello+world

# Full encoding
quote("hello world")  # hello%20world
```

---

## 4. Request Headers

Headers provide metadata about the request. They're key-value pairs.

### Essential Headers for Scraping

```python
headers = {
    # REQUIRED - Server needs to know the target
    "Host": "www.example.com",
    
    # CRITICAL - Identifies your client
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    
    # IMPORTANT - What content you accept
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    
    # OFTEN CHECKED - Where you came from
    "Referer": "https://www.example.com/",
    
    # AUTHENTICATION - Session state
    "Cookie": "session_id=abc123; user_pref=dark_mode",
    
    # API REQUESTS - Content type
    "Content-Type": "application/json",
    
    # AJAX DETECTION
    "X-Requested-With": "XMLHttpRequest",
}
```

### Header Deep Dive

#### User-Agent

Identifies the client. Most important header for avoiding blocks.

```python
# BAD - Obvious bot
"User-Agent": "python-requests/2.28.0"

# BAD - Outdated
"User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0)"

# GOOD - Current Chrome on Windows
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# GOOD - Current Firefox on Mac
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0"
```

#### Accept Headers

Tell server what formats you can handle:

```python
# Web page request
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"

# JSON API request
"Accept": "application/json"

# Image request
"Accept": "image/webp,image/apng,image/*,*/*;q=0.8"
```

The `q=` parameter is quality/preference (0-1).

#### Referer

Where the request originated. Often checked for:
- Hot-linking prevention
- Navigation flow verification
- Analytics

```python
# Direct visit (no referer)
headers = {}

# From search results
headers = {"Referer": "https://www.google.com/"}

# From site navigation
headers = {"Referer": "https://example.com/products"}
```

#### Cookie

Session state as key-value pairs:

```python
# Single cookie
"Cookie": "session_id=abc123"

# Multiple cookies
"Cookie": "session_id=abc123; user_id=456; theme=dark"
```

---

## 5. HTTP Response Structure

```
┌─────────────────────────────────────────────────────────────┐
│ STATUS LINE                                                 │
│ HTTP/1.1 200 OK                                            │
├─────────────────────────────────────────────────────────────┤
│ HEADERS                                                     │
│ Content-Type: text/html; charset=utf-8                     │
│ Content-Length: 15234                                       │
│ Content-Encoding: gzip                                      │
│ Set-Cookie: session=xyz789; Path=/; HttpOnly               │
│ Cache-Control: max-age=3600                                │
│ X-RateLimit-Remaining: 95                                  │
├─────────────────────────────────────────────────────────────┤
│ BLANK LINE                                                  │
├─────────────────────────────────────────────────────────────┤
│ BODY                                                        │
│ <!DOCTYPE html>                                            │
│ <html>                                                     │
│ <head><title>Product Page</title></head>                   │
│ <body>...</body>                                           │
│ </html>                                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Status Codes

### Status Code Categories

| Range | Category | Meaning |
|-------|----------|---------|
| 1xx | Informational | Request received, continuing |
| 2xx | Success | Request successful |
| 3xx | Redirection | Further action needed |
| 4xx | Client Error | Problem with request |
| 5xx | Server Error | Server failed |

### Status Codes for Scrapers

#### Success Codes

| Code | Name | Action |
|------|------|--------|
| **200** | OK | Parse the response body |
| **201** | Created | Resource created (POST success) |
| **204** | No Content | Success but no body |

#### Redirect Codes

| Code | Name | Action |
|------|------|--------|
| **301** | Moved Permanently | Update URL, follow redirect |
| **302** | Found (Temporary) | Follow redirect |
| **303** | See Other | Follow with GET |
| **307** | Temporary Redirect | Follow, keep method |
| **308** | Permanent Redirect | Update URL, keep method |

```python
# Requests follows redirects by default
response = requests.get(url)  # Follows redirects
print(response.url)           # Final URL
print(response.history)       # List of redirects

# Disable redirect following
response = requests.get(url, allow_redirects=False)
if response.status_code in (301, 302):
    new_url = response.headers["Location"]
```

#### Client Error Codes

| Code | Name | Meaning | Action |
|------|------|---------|--------|
| **400** | Bad Request | Malformed request | Fix request |
| **401** | Unauthorized | Auth required | Add credentials |
| **403** | Forbidden | Access denied | Blocked or need auth |
| **404** | Not Found | Page doesn't exist | Skip URL |
| **405** | Method Not Allowed | Wrong HTTP method | Try different method |
| **429** | Too Many Requests | Rate limited | Wait and retry |

```python
# Handle 429 rate limiting
response = requests.get(url)
if response.status_code == 429:
    retry_after = int(response.headers.get("Retry-After", 60))
    time.sleep(retry_after)
    response = requests.get(url)  # Retry
```

#### Server Error Codes

| Code | Name | Meaning | Action |
|------|------|---------|--------|
| **500** | Internal Server Error | Server bug | Retry later |
| **502** | Bad Gateway | Upstream error | Retry |
| **503** | Service Unavailable | Overloaded/maintenance | Retry with backoff |
| **504** | Gateway Timeout | Upstream timeout | Retry |

---

## 7. Response Headers

### Important Response Headers

```python
response = requests.get(url)

# Content information
response.headers["Content-Type"]      # text/html; charset=utf-8
response.headers["Content-Length"]    # 15234
response.headers["Content-Encoding"]  # gzip

# Cookies to set
response.headers["Set-Cookie"]        # session=xyz; Path=/

# Caching
response.headers["Cache-Control"]     # max-age=3600
response.headers["ETag"]              # "abc123"
response.headers["Last-Modified"]     # Wed, 15 Jan 2024 10:00:00 GMT

# Rate limiting (custom headers)
response.headers["X-RateLimit-Limit"]      # 100
response.headers["X-RateLimit-Remaining"]  # 95
response.headers["X-RateLimit-Reset"]      # 1705312800

# Security
response.headers["X-Frame-Options"]   # DENY
response.headers["X-XSS-Protection"]  # 1; mode=block
```

### Set-Cookie Header

```
Set-Cookie: session_id=abc123; Path=/; Domain=.example.com; Secure; HttpOnly; SameSite=Lax; Expires=Thu, 01 Jan 2025 00:00:00 GMT
```

| Attribute | Meaning |
|-----------|---------|
| `Path=/` | Cookie valid for all paths |
| `Domain=.example.com` | Valid for subdomains too |
| `Secure` | HTTPS only |
| `HttpOnly` | Not accessible via JavaScript |
| `SameSite=Lax` | CSRF protection |
| `Expires=...` | When cookie expires |

---

## 8. Response Body

### Content Types

| Content-Type | Data Format | Parsing |
|--------------|-------------|---------|
| `text/html` | HTML page | BeautifulSoup, lxml |
| `application/json` | JSON data | `response.json()` |
| `application/xml` | XML data | lxml, ElementTree |
| `text/plain` | Plain text | `response.text` |
| `application/octet-stream` | Binary | `response.content` |
| `image/*` | Images | `response.content` |

### Accessing Response Body

```python
response = requests.get(url)

# Text content (decoded)
html = response.text

# Binary content (raw bytes)
image_data = response.content

# JSON (parsed)
data = response.json()

# Encoding
print(response.encoding)  # utf-8
response.encoding = "utf-8"  # Override if wrong
```

### Content Encoding (Compression)

```python
# Requests handles gzip/deflate automatically
response = requests.get(url)  # Sends Accept-Encoding: gzip, deflate
# response.text is already decompressed

# Raw compressed content
response = requests.get(url, headers={"Accept-Encoding": "identity"})
```

---

## 9. Practical Patterns

### Complete Request Example

```python
import requests

def fetch_page(url, session=None):
    """Fetch a page with proper headers."""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    client = session or requests
    
    response = client.get(
        url,
        headers=headers,
        timeout=(10, 30),  # Connect, read timeout
        allow_redirects=True
    )
    
    response.raise_for_status()  # Raise on 4xx/5xx
    
    return response
```

### POST Request with Form Data

```python
def submit_form(url, data, session=None):
    """Submit a form via POST."""
    
    headers = {
        "User-Agent": "Mozilla/5.0...",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://example.com",
        "Referer": "https://example.com/form",
    }
    
    client = session or requests
    
    response = client.post(
        url,
        data=data,  # Form data
        headers=headers
    )
    
    return response
```

### POST Request with JSON

```python
def api_request(url, payload, api_key):
    """Make a JSON API request."""
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    
    response = requests.post(
        url,
        json=payload,  # Automatically serialized
        headers=headers
    )
    
    return response.json()
```

### Robust Request with Retries

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session():
    """Create session with retry logic."""
    
    session = requests.Session()
    
    retries = Retry(
        total=3,
        backoff_factor=1,  # Wait 1, 2, 4 seconds
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

# Usage
session = create_session()
response = session.get(url)  # Automatically retries on failure
```

---

## 10. Debugging HTTP

### Inspect Full Request/Response

```python
import requests
from requests_toolbelt.utils import dump

response = requests.get(url)

# Print full HTTP exchange
data = dump.dump_all(response)
print(data.decode('utf-8'))
```

### Using a Proxy for Inspection

```python
# Route through debugging proxy (mitmproxy, Charles, Fiddler)
proxies = {
    "http": "http://localhost:8080",
    "https": "http://localhost:8080",
}
response = requests.get(url, proxies=proxies, verify=False)
```

### Logging All Requests

```python
import logging
import http.client

# Enable HTTP debug logging
http.client.HTTPConnection.debuglevel = 1
logging.basicConfig(level=logging.DEBUG)
```

---

## Summary

| Component | Purpose | Scraper Implication |
|-----------|---------|---------------------|
| **Method** | Action type | GET for reading, POST for forms |
| **URL** | Target resource | Build properly with encoding |
| **Headers** | Request metadata | Critical for avoiding blocks |
| **Body** | Payload data | For POST/PUT requests |
| **Status Code** | Result indicator | Handle all cases |
| **Response Headers** | Response metadata | Check for cookies, rate limits |
| **Response Body** | The data | Parse based on Content-Type |

---

*Next: [02_cors_explained.md](02_cors_explained.md) - Understanding cross-origin restrictions*
