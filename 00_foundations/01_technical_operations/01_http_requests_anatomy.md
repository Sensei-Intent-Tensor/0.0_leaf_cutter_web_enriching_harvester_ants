# HTTP Requests Anatomy

> **Understanding the Foundation of All Web Scraping**

Every web scraping operation is built on HTTP requests. Before you can extract data, you need to understand how browsers and servers communicate. This document dissects HTTP from a scraper's perspective.

---

## The Request-Response Cycle

```
┌─────────────┐                              ┌─────────────┐
│             │  ──── HTTP REQUEST ────▶     │             │
│   CLIENT    │                              │   SERVER    │
│  (Scraper)  │  ◀─── HTTP RESPONSE ────     │  (Website)  │
│             │                              │             │
└─────────────┘                              └─────────────┘
```

**Every scrape is this cycle repeated.**

---

## 1. HTTP Request Structure

An HTTP request has four components:

```
┌─────────────────────────────────────────────────────────┐
│ REQUEST LINE                                            │
│ GET /products/123 HTTP/1.1                              │
├─────────────────────────────────────────────────────────┤
│ HEADERS                                                 │
│ Host: www.example.com                                   │
│ User-Agent: Mozilla/5.0...                              │
│ Accept: text/html                                       │
│ Cookie: session=abc123                                  │
├─────────────────────────────────────────────────────────┤
│ BLANK LINE                                              │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ BODY (optional, for POST/PUT)                           │
│ {"query": "search term"}                                │
└─────────────────────────────────────────────────────────┘
```

---

### 1.1 Request Line

The first line specifies what you want:

```
METHOD  PATH        VERSION
GET     /products   HTTP/1.1
```

#### HTTP Methods for Scrapers

| Method | Purpose | When You'll Use It |
|--------|---------|-------------------|
| **GET** | Retrieve data | 95% of scraping - fetching pages |
| **POST** | Submit data | Form submissions, search queries, API calls |
| **HEAD** | Get headers only | Check if page exists, get content-type |
| **PUT** | Update resource | Rare in scraping |
| **DELETE** | Remove resource | Rare in scraping |
| **OPTIONS** | Check allowed methods | CORS preflight (browser only) |

```python
import requests

# GET - most common
response = requests.get("https://example.com/page")

# POST - for forms and APIs
response = requests.post("https://example.com/search", 
    data={"query": "python"})

# HEAD - check without downloading
response = requests.head("https://example.com/large-file.pdf")
print(response.headers["Content-Length"])  # Size without downloading
```

---

### 1.2 Request Headers

Headers provide metadata about the request. **These are critical for avoiding detection.**

#### Essential Headers for Scrapers

```python
headers = {
    # REQUIRED: Identifies the target server
    "Host": "www.example.com",
    
    # CRITICAL: Identifies your client (most checked by anti-bot)
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    
    # What content types you accept
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    
    # Encoding support
    "Accept-Encoding": "gzip, deflate, br",
    
    # Language preference
    "Accept-Language": "en-US,en;q=0.9",
    
    # Previous page (often checked)
    "Referer": "https://www.example.com/",
    
    # Connection handling
    "Connection": "keep-alive",
}

response = requests.get(url, headers=headers)
```

#### Header Deep Dive

| Header | Purpose | Scraping Importance |
|--------|---------|---------------------|
| `User-Agent` | Client identification | 🔴 **Critical** - Most checked |
| `Accept` | Content type preference | 🟡 Medium - Looks more real |
| `Accept-Language` | Language preference | 🟡 Medium - Geo consistency |
| `Accept-Encoding` | Compression support | 🟢 Low - Performance |
| `Referer` | Previous page | 🟡 Medium - Often validated |
| `Cookie` | Session data | 🔴 **Critical** - Auth required |
| `Authorization` | API credentials | 🔴 **Critical** - For APIs |
| `Content-Type` | Body format (POST) | 🔴 **Critical** - For POST |
| `X-Requested-With` | AJAX indicator | 🟡 Medium - For AJAX calls |
| `Origin` | Request origin | 🟡 Medium - CORS related |

---

### 1.3 Request Body

Only present for POST, PUT, PATCH requests.

#### Form Data (application/x-www-form-urlencoded)

```python
# Standard form submission
response = requests.post(url, data={
    "username": "user",
    "password": "pass",
    "remember": "true"
})
# Sent as: username=user&password=pass&remember=true
```

#### JSON Data (application/json)

```python
# API request
response = requests.post(url, json={
    "query": "search term",
    "filters": {"category": "electronics"}
})
# Sent as: {"query": "search term", "filters": {"category": "electronics"}}
```

#### Multipart Form Data (file uploads)

```python
# File upload
files = {"document": open("file.pdf", "rb")}
response = requests.post(url, files=files, data={"title": "My Doc"})
```

---

## 2. HTTP Response Structure

```
┌─────────────────────────────────────────────────────────┐
│ STATUS LINE                                             │
│ HTTP/1.1 200 OK                                         │
├─────────────────────────────────────────────────────────┤
│ HEADERS                                                 │
│ Content-Type: text/html; charset=utf-8                  │
│ Content-Length: 15234                                   │
│ Set-Cookie: session=xyz789                              │
├─────────────────────────────────────────────────────────┤
│ BLANK LINE                                              │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ BODY                                                    │
│ <!DOCTYPE html><html>...</html>                         │
└─────────────────────────────────────────────────────────┘
```

---

### 2.1 Status Codes

The three-digit code tells you what happened:

#### Success Codes (2xx)

| Code | Meaning | Scraper Action |
|------|---------|----------------|
| **200** | OK | ✅ Parse the response |
| **201** | Created | ✅ Resource created (POST success) |
| **204** | No Content | ✅ Success but empty body |

#### Redirect Codes (3xx)

| Code | Meaning | Scraper Action |
|------|---------|----------------|
| **301** | Moved Permanently | Follow new URL, update records |
| **302** | Found (Temporary) | Follow new URL |
| **303** | See Other | Follow with GET |
| **307** | Temporary Redirect | Follow, preserve method |
| **308** | Permanent Redirect | Follow, preserve method |

```python
# requests follows redirects by default
response = requests.get(url, allow_redirects=True)
print(response.url)  # Final URL after redirects
print(response.history)  # List of redirect responses
```

#### Client Error Codes (4xx)

| Code | Meaning | Scraper Action |
|------|---------|----------------|
| **400** | Bad Request | Fix request format |
| **401** | Unauthorized | Need authentication |
| **403** | Forbidden | Blocked or need different auth |
| **404** | Not Found | URL doesn't exist, skip |
| **405** | Method Not Allowed | Use different HTTP method |
| **429** | Too Many Requests | **Rate limited - slow down!** |
| **451** | Unavailable for Legal | Content blocked in region |

#### Server Error Codes (5xx)

| Code | Meaning | Scraper Action |
|------|---------|----------------|
| **500** | Internal Server Error | Retry later |
| **502** | Bad Gateway | Retry later |
| **503** | Service Unavailable | Retry later (or blocked) |
| **504** | Gateway Timeout | Retry later |

```python
def fetch_with_handling(url):
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.text
    elif response.status_code == 404:
        return None  # Page doesn't exist
    elif response.status_code == 429:
        time.sleep(60)  # Rate limited, wait
        return fetch_with_handling(url)  # Retry
    elif response.status_code == 403:
        raise BlockedError("Access denied")
    elif response.status_code >= 500:
        time.sleep(5)  # Server error, brief wait
        return fetch_with_handling(url)  # Retry
    else:
        raise UnexpectedError(f"Status {response.status_code}")
```

---

### 2.2 Response Headers

Headers contain valuable metadata:

```python
response = requests.get(url)

# Content information
response.headers["Content-Type"]      # text/html; charset=utf-8
response.headers["Content-Length"]    # 15234
response.headers["Content-Encoding"]  # gzip

# Caching
response.headers["Cache-Control"]     # max-age=3600
response.headers["ETag"]              # "abc123"
response.headers["Last-Modified"]     # Wed, 15 Jan 2024 12:00:00 GMT

# Rate limiting (if provided)
response.headers["X-RateLimit-Limit"]      # 100
response.headers["X-RateLimit-Remaining"]  # 95
response.headers["Retry-After"]            # 60

# Cookies
response.headers["Set-Cookie"]  # session=xyz789; Path=/; HttpOnly
```

#### Important Response Headers for Scrapers

| Header | What It Tells You |
|--------|------------------|
| `Content-Type` | How to parse the body (HTML, JSON, etc.) |
| `Content-Encoding` | If body is compressed |
| `Set-Cookie` | Cookies to store for future requests |
| `Location` | Redirect destination (3xx responses) |
| `Retry-After` | When to retry after 429/503 |
| `X-RateLimit-*` | Rate limit status |

---

### 2.3 Response Body

The actual content you're scraping:

```python
response = requests.get(url)

# For HTML pages
html = response.text  # Decoded string
# or
html = response.content.decode('utf-8')  # Manual decode

# For JSON APIs
data = response.json()  # Parsed dict/list

# For binary (images, PDFs)
binary_data = response.content  # Raw bytes

# Check content type before parsing
content_type = response.headers.get("Content-Type", "")
if "application/json" in content_type:
    data = response.json()
elif "text/html" in content_type:
    html = response.text
```

---

## 3. Practical Request Patterns

### 3.1 Basic GET Request

```python
import requests

# Simple
response = requests.get("https://example.com")

# With headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
}
response = requests.get("https://example.com", headers=headers)

# With query parameters
params = {"q": "search term", "page": 1}
response = requests.get("https://example.com/search", params=params)
# Becomes: https://example.com/search?q=search+term&page=1
```

### 3.2 POST Request with Form Data

```python
# Login form
login_data = {
    "username": "myuser",
    "password": "mypass",
    "csrf_token": "extracted_token"
}

response = requests.post(
    "https://example.com/login",
    data=login_data,
    headers={"Referer": "https://example.com/login"}
)
```

### 3.3 POST Request with JSON

```python
# API call
payload = {
    "query": "laptops",
    "filters": {
        "price_min": 500,
        "price_max": 1500
    },
    "page": 1
}

response = requests.post(
    "https://api.example.com/search",
    json=payload,
    headers={"Authorization": "Bearer API_KEY"}
)

results = response.json()
```

### 3.4 Session-Based Requests

```python
# Session maintains cookies across requests
session = requests.Session()

# Set default headers
session.headers.update({
    "User-Agent": "Mozilla/5.0...",
    "Accept-Language": "en-US,en;q=0.9"
})

# Login (cookies automatically stored)
session.post("https://example.com/login", data=credentials)

# Subsequent requests include session cookies
protected_page = session.get("https://example.com/dashboard")
```

### 3.5 Request with Timeout and Retries

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)

# Create session with retry
session = requests.Session()
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Request with timeout
response = session.get(
    "https://example.com",
    timeout=(5, 30)  # (connect timeout, read timeout)
)
```

---

## 4. Request/Response Inspection

### 4.1 Examining What Was Sent

```python
response = requests.get(url, headers=headers)

# What was actually sent
print(response.request.method)
print(response.request.url)
print(response.request.headers)
print(response.request.body)
```

### 4.2 Full Request/Response Debug

```python
import requests
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)

response = requests.get("https://example.com")
# Outputs full request/response details
```

### 4.3 Using Browser DevTools

1. **Open DevTools** (F12)
2. **Go to Network tab**
3. **Make the request in browser**
4. **Click on request** to see:
   - Headers (request & response)
   - Payload (POST body)
   - Response body
   - Timing

**Pro tip**: Right-click request → "Copy as cURL" → Convert to Python

---

## 5. Common Pitfalls

### 5.1 Missing Headers

```python
# ❌ Bare request - easily detected
response = requests.get(url)

# ✅ With realistic headers
response = requests.get(url, headers={
    "User-Agent": "Mozilla/5.0...",
    "Accept": "text/html...",
    "Accept-Language": "en-US,en;q=0.9"
})
```

### 5.2 Ignoring Redirects

```python
# ❌ May miss final destination
response = requests.get(url, allow_redirects=False)

# ✅ Follow redirects, check final URL
response = requests.get(url, allow_redirects=True)
actual_url = response.url
```

### 5.3 Not Handling Encoding

```python
# ❌ May get garbled text
text = response.content.decode()

# ✅ Use detected encoding
text = response.text  # requests detects encoding

# ✅ Or specify if known
text = response.content.decode('utf-8', errors='replace')
```

### 5.4 Ignoring Rate Limits

```python
# ❌ Hammer the server
for url in urls:
    requests.get(url)

# ✅ Respect rate limits
for url in urls:
    response = requests.get(url)
    if response.status_code == 429:
        wait = int(response.headers.get("Retry-After", 60))
        time.sleep(wait)
    time.sleep(1)  # Base delay
```

---

## 6. HTTP/2 and HTTP/3

Modern protocols with improved performance:

| Feature | HTTP/1.1 | HTTP/2 | HTTP/3 |
|---------|----------|--------|--------|
| Connections | Multiple | Single (multiplexed) | Single (QUIC) |
| Header Compression | No | Yes (HPACK) | Yes (QPACK) |
| Server Push | No | Yes | Yes |
| Transport | TCP | TCP | UDP (QUIC) |

```python
# For HTTP/2 support, use httpx
import httpx

# HTTP/2 client
with httpx.Client(http2=True) as client:
    response = client.get("https://example.com")
```

---

## Summary

### Request Essentials

| Component | What to Set |
|-----------|-------------|
| Method | GET for pages, POST for forms/APIs |
| Headers | User-Agent, Accept, Referer, Cookie |
| Body | Form data or JSON for POST |

### Response Essentials

| What to Check | Why |
|---------------|-----|
| Status Code | Know if request succeeded |
| Content-Type | Know how to parse |
| Set-Cookie | Maintain session |
| Rate Limit Headers | Avoid getting blocked |

### Key Principles

1. **Always set a realistic User-Agent**
2. **Use sessions for related requests**
3. **Handle all status codes appropriately**
4. **Respect rate limits and add delays**
5. **Inspect requests in browser first**

---

*Next: [02_cors_explained.md](02_cors_explained.md) - Understanding Cross-Origin Resource Sharing*
