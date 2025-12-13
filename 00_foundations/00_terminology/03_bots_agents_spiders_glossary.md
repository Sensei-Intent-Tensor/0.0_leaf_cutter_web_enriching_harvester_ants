# Bots, Agents, Spiders: Complete Glossary

> **The Definitive Dictionary of Web Data Extraction Terminology**

This glossary covers every term you'll encounter in the world of web scraping, crawling, and data extraction—from basic concepts to advanced techniques.

---

## How to Use This Glossary

- **Terms are alphabetized** within categories
- **Cross-references** link related terms with →
- **Code examples** show practical usage where relevant
- **See also** sections connect related concepts

---

## 📑 Table of Contents

1. [Core Concepts](#1-core-concepts)
2. [Bot & Agent Types](#2-bot--agent-types)
3. [HTTP & Networking](#3-http--networking)
4. [HTML & DOM](#4-html--dom)
5. [Selectors & Parsing](#5-selectors--parsing)
6. [Anti-Scraping & Detection](#6-anti-scraping--detection)
7. [Authentication & Sessions](#7-authentication--sessions)
8. [Data Processing](#8-data-processing)
9. [Infrastructure & Scaling](#9-infrastructure--scaling)
10. [Legal & Ethical](#10-legal--ethical)

---

## 1. Core Concepts

### Bot
An automated software program that performs tasks without human intervention. In web context, a bot makes HTTP requests to websites programmatically.

**Types**: Good bots (search engines, price monitors), Bad bots (spam, credential stuffing)

→ See: *Agent*, *Spider*, *Crawler*

---

### Crawler
A program that systematically browses the web by following links from page to page. Primary purpose is discovery and indexing.

**Example**: Googlebot crawls billions of pages to build Google's search index.

→ See: *Spider*, *Scraper*

---

### Scraper
A program that extracts specific structured data from web pages. Focuses on data extraction rather than page discovery.

```python
# Scraper extracts specific data
data = {
    "title": page.select_one("h1").text,
    "price": page.select_one(".price").text
}
```

→ See: *Crawler*, *Parser*

---

### Spider
A bot that maps the complete structure of a website by traversing all internal links. Named for how a spider traverses its web.

**Distinction**: Spiders typically stay within one domain; crawlers cross domains.

→ See: *Crawler*, *Site Map*

---

### Agent
Generic term for any automated program acting on behalf of a user or system. Broader than "bot"—includes scrapers, crawlers, and automation scripts.

**User-Agent**: The HTTP header identifying the agent making a request.

→ See: *Bot*, *User-Agent*

---

### Harvesting
The process of collecting raw data from web sources. First stage of the data pipeline before cleaning and enrichment.

→ See: *Scraping*, *Pipeline*

---

### Enrichment
Adding value to harvested data through additional lookups, computations, or cross-referencing with other data sources.

**Examples**: Geocoding addresses, adding social profiles, computing derived fields.

→ See: *Pipeline*, *Data Augmentation*

---

### Pipeline
A sequence of data processing stages where output of each stage becomes input to the next.

```
Source → Harvest → Clean → Enrich → Output
```

→ See: *ETL*, *Workflow*

---

### ETL (Extract, Transform, Load)
Traditional data pipeline pattern. In scraping context:
- **Extract**: Harvest data from web
- **Transform**: Clean and enrich
- **Load**: Store in database/file

→ See: *Pipeline*

---

## 2. Bot & Agent Types

### Googlebot
Google's web crawler. Respects robots.txt, identifies as "Googlebot" in User-Agent.

```
User-Agent: Googlebot/2.1 (+http://www.google.com/bot.html)
```

---

### Bingbot
Microsoft's crawler for Bing search engine.

```
User-Agent: Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)
```

---

### Search Engine Bot
Any crawler operated by a search engine to index web content. Generally considered "good bots" and given preferential treatment.

**Major bots**: Googlebot, Bingbot, DuckDuckBot, Yandex, Baidu Spider

---

### Price Monitoring Bot
Automated system that tracks prices across e-commerce sites. Used for competitive intelligence and dynamic pricing.

→ See: *Competitive Intelligence*

---

### Content Aggregator
Bot that collects content from multiple sources to present in one place. Examples: news aggregators, job boards, real estate listings.

---

### Headless Browser
A web browser without a graphical interface, controlled programmatically. Used when JavaScript rendering is required.

**Tools**: Puppeteer, Playwright, Selenium (headless mode)

```python
# Playwright headless browser
browser = playwright.chromium.launch(headless=True)
page = browser.new_page()
page.goto("https://example.com")
```

→ See: *Browser Automation*, *JavaScript Rendering*

---

### Zombie Bot
A compromised computer running bot software without owner's knowledge. Part of botnets used for malicious purposes.

**Not related to legitimate scraping.**

---

## 3. HTTP & Networking

### HTTP Request
A message sent from client to server requesting a resource.

**Components**:
- Method (GET, POST, PUT, DELETE)
- URL
- Headers
- Body (for POST/PUT)

```python
import requests
response = requests.get(
    "https://example.com/api/data",
    headers={"User-Agent": "MyBot/1.0"}
)
```

---

### HTTP Response
Server's reply to an HTTP request.

**Components**:
- Status code (200, 404, 403, etc.)
- Headers
- Body (HTML, JSON, etc.)

---

### Status Codes

| Code | Meaning | Scraping Implication |
|------|---------|---------------------|
| **200** | OK | Success, parse the content |
| **301/302** | Redirect | Follow to new URL |
| **400** | Bad Request | Fix your request |
| **401** | Unauthorized | Need authentication |
| **403** | Forbidden | Blocked or need auth |
| **404** | Not Found | URL doesn't exist |
| **429** | Too Many Requests | Rate limited, slow down |
| **500** | Server Error | Retry later |
| **503** | Service Unavailable | Site down or blocking |

---

### Headers
Metadata sent with HTTP requests and responses.

**Important Request Headers**:
```
User-Agent: Mozilla/5.0...
Accept: text/html
Accept-Language: en-US
Referer: https://example.com/previous-page
Cookie: session=abc123
```

**Important Response Headers**:
```
Content-Type: text/html
Set-Cookie: session=xyz789
X-RateLimit-Remaining: 95
Retry-After: 60
```

→ See: *User-Agent*, *Cookies*

---

### User-Agent
HTTP header identifying the client making the request.

**Real browser**:
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

**Bot identifier**:
```
MyScraperBot/1.0 (+https://mysite.com/bot-info)
```

→ See: *Headers*, *Bot Detection*

---

### Referer (Referrer)
Header indicating the previous page that linked to current request. Often checked by anti-scraping systems.

**Note**: Spelled "Referer" (historical typo in HTTP spec).

---

### Request Method

| Method | Purpose | Scraping Use |
|--------|---------|--------------|
| **GET** | Retrieve data | Most scraping requests |
| **POST** | Submit data | Form submission, API calls |
| **PUT** | Update data | Rare in scraping |
| **DELETE** | Remove data | Rare in scraping |
| **HEAD** | Get headers only | Check if page exists |

---

### Session
A persistent connection state between client and server, typically maintained via cookies.

```python
# Requests session maintains cookies
session = requests.Session()
session.get("https://example.com/login")  # Sets cookies
session.get("https://example.com/protected")  # Uses cookies
```

→ See: *Cookies*, *Authentication*

---

### Proxy
An intermediary server that forwards requests on behalf of the client.

**Types**:
- **HTTP Proxy**: Basic forwarding
- **SOCKS Proxy**: Lower level, more versatile
- **Residential Proxy**: Uses real home IP addresses
- **Datacenter Proxy**: Uses server IP addresses

```python
proxies = {
    "http": "http://proxy.example.com:8080",
    "https": "http://proxy.example.com:8080"
}
requests.get("https://target.com", proxies=proxies)
```

→ See: *IP Rotation*, *Residential Proxy*

---

### IP Rotation
Cycling through multiple IP addresses to avoid rate limits and blocks.

```python
proxy_pool = ["ip1:port", "ip2:port", "ip3:port"]
proxy = random.choice(proxy_pool)
```

→ See: *Proxy*, *Rate Limiting*

---

### Residential Proxy
Proxy using IP addresses assigned to real residential internet connections. Harder to detect than datacenter IPs.

**Cost**: More expensive than datacenter proxies

→ See: *Proxy*, *Datacenter Proxy*

---

### SSL/TLS
Encryption protocols for secure HTTP (HTTPS). Most modern websites require HTTPS.

**Certificate Verification**: Should generally be kept enabled to avoid security issues.

---

### Timeout
Maximum time to wait for a response before giving up.

```python
# Set connection and read timeouts
requests.get(url, timeout=(5, 30))  # 5s connect, 30s read
```

---

### Retry
Attempting a failed request again, often with exponential backoff.

```python
from tenacity import retry, wait_exponential

@retry(wait=wait_exponential(multiplier=1, max=60))
def fetch_with_retry(url):
    return requests.get(url)
```

---

## 4. HTML & DOM

### HTML (HyperText Markup Language)
The standard markup language for web pages. What scrapers parse to extract data.

```html
<html>
  <body>
    <h1 class="title">Product Name</h1>
    <span id="price">$99.99</span>
  </body>
</html>
```

---

### DOM (Document Object Model)
A programming interface representing HTML as a tree structure that can be traversed and manipulated.

```
document
└── html
    └── body
        ├── h1.title
        └── span#price
```

---

### Element
A single node in the HTML DOM tree, defined by tags.

```html
<div class="product">  <!-- Opening tag -->
  Content here
</div>                 <!-- Closing tag -->
```

---

### Attribute
Properties of HTML elements.

```html
<a href="https://example.com" class="link" id="main-link">
   ↑ href attribute      ↑ class attribute  ↑ id attribute
```

---

### Tag
HTML markers that define elements.

**Common tags**:
- `<div>`, `<span>` - Generic containers
- `<a>` - Links
- `<p>` - Paragraphs
- `<table>`, `<tr>`, `<td>` - Tables
- `<ul>`, `<li>` - Lists
- `<form>`, `<input>` - Forms

---

### Class
HTML attribute for grouping elements. Multiple elements can share the same class.

```html
<div class="product featured">...</div>
<div class="product">...</div>
```

**CSS Selector**: `.product`, `.featured`

---

### ID
HTML attribute for uniquely identifying an element. Should be unique per page.

```html
<div id="main-content">...</div>
```

**CSS Selector**: `#main-content`

---

### Nested Elements
Elements contained within other elements, forming the DOM tree.

```html
<div class="card">           <!-- Parent -->
  <h2>Title</h2>             <!-- Child -->
  <div class="body">         <!-- Child -->
    <p>Content</p>           <!-- Grandchild -->
  </div>
</div>
```

---

## 5. Selectors & Parsing

### Selector
A pattern used to identify and select HTML elements for extraction.

**Types**: CSS Selectors, XPath

→ See: *CSS Selector*, *XPath*

---

### CSS Selector
Pattern syntax for selecting HTML elements, borrowed from CSS styling.

| Selector | Meaning | Example |
|----------|---------|---------|
| `tag` | Element type | `div`, `p`, `a` |
| `.class` | Class name | `.product`, `.price` |
| `#id` | ID | `#main`, `#header` |
| `tag.class` | Tag with class | `div.product` |
| `parent child` | Descendant | `div.product span.price` |
| `parent > child` | Direct child | `ul > li` |
| `[attr]` | Has attribute | `[href]` |
| `[attr=value]` | Attribute equals | `[type="submit"]` |
| `:first-child` | First child | `li:first-child` |
| `:nth-child(n)` | Nth child | `tr:nth-child(2)` |

```python
# BeautifulSoup CSS selection
soup.select("div.product span.price")
soup.select_one("#main-title")
```

---

### XPath
XML Path Language—powerful syntax for navigating XML/HTML documents.

| XPath | Meaning |
|-------|---------|
| `//div` | All div elements |
| `//div[@class='product']` | Div with class |
| `//div[@id='main']` | Div with ID |
| `//div/span` | Span children of div |
| `//div//span` | Span descendants of div |
| `//a/@href` | href attribute of links |
| `//text()` | Text content |
| `//div[1]` | First div |
| `//div[last()]` | Last div |
| `//div[contains(@class, 'prod')]` | Class contains |
| `//div[starts-with(@id, 'item')]` | ID starts with |

```python
# lxml XPath
tree.xpath("//div[@class='product']//span[@class='price']/text()")
```

---

### Parser
Software that reads HTML and creates a navigable structure.

**Popular parsers**:
- **BeautifulSoup** (Python) - Easy, forgiving
- **lxml** (Python) - Fast, strict
- **Parsel** (Python) - Scrapy's parser
- **Cheerio** (Node.js) - jQuery-like
- **Nokogiri** (Ruby) - Full-featured

---

### BeautifulSoup
Popular Python library for parsing HTML. Forgiving of malformed HTML.

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "html.parser")
title = soup.select_one("h1.title").text
links = [a["href"] for a in soup.select("a")]
```

---

### lxml
Fast XML/HTML parser for Python. Stricter than BeautifulSoup.

```python
from lxml import html

tree = html.fromstring(html_content)
prices = tree.xpath("//span[@class='price']/text()")
```

---

### Regular Expression (Regex)
Pattern matching for text. Use sparingly for HTML—prefer proper parsers.

```python
import re

# Extract prices like $99.99
prices = re.findall(r'\$[\d,]+\.?\d*', text)

# Extract emails
emails = re.findall(r'[\w.-]+@[\w.-]+\.\w+', text)
```

**Warning**: "Don't parse HTML with regex" is good advice. Use for post-extraction text processing.

---

### Text Extraction
Getting visible text content from HTML elements.

```python
# Get text, strip whitespace
element.text.strip()

# Get all text including children
element.get_text(separator=" ", strip=True)
```

---

## 6. Anti-Scraping & Detection

### Anti-Scraping
Technologies and techniques used to prevent or hinder automated data extraction.

→ See: *Bot Detection*, *CAPTCHA*, *Rate Limiting*

---

### Bot Detection
Systems that identify and block automated requests.

**Detection signals**:
- Request patterns (speed, regularity)
- Browser fingerprint anomalies
- Missing JavaScript execution
- Known bot IP addresses
- Behavioral analysis

→ See: *Fingerprinting*, *Honeypot*

---

### CAPTCHA
"Completely Automated Public Turing test to tell Computers and Humans Apart"

**Types**:
- **reCAPTCHA**: Google's system (checkbox, image selection)
- **hCaptcha**: Privacy-focused alternative
- **Text CAPTCHA**: Distorted text to type
- **Math CAPTCHA**: Simple arithmetic

→ See: *CAPTCHA Solving Services*

---

### reCAPTCHA
Google's CAPTCHA system. Multiple versions:

- **v2 Checkbox**: "I'm not a robot" checkbox
- **v2 Invisible**: Triggered automatically
- **v3**: Scoring system, no user interaction

---

### Fingerprinting
Creating a unique identifier from browser/system characteristics.

**Fingerprint data points**:
- Screen resolution
- Installed fonts
- Browser plugins
- Canvas rendering
- WebGL renderer
- Timezone
- Language settings

→ See: *Bot Detection*, *Browser Fingerprint*

---

### Honeypot
Hidden trap elements invisible to humans but followed by bots.

```html
<!-- Honeypot link - hidden via CSS -->
<a href="/trap" style="display:none">Click here</a>
```

**If a bot follows this link, it reveals itself as automated.**

→ See: *Bot Detection*

---

### Rate Limiting
Restricting the number of requests from a client within a time period.

**Response**: HTTP 429 Too Many Requests

**Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
Retry-After: 60
```

→ See: *Throttling*, *Backoff*

---

### Throttling
Intentionally slowing down requests to avoid detection or respect limits.

```python
import time

for url in urls:
    response = fetch(url)
    time.sleep(2)  # Wait 2 seconds between requests
```

→ See: *Rate Limiting*, *Backoff*

---

### Backoff
Increasing wait time after failures or rate limits.

**Exponential backoff**: 1s → 2s → 4s → 8s → 16s...

```python
wait_time = min(2 ** attempt, max_wait)
```

---

### Cloudflare
Major CDN and security provider. Implements various anti-bot measures.

**Challenges**:
- JavaScript challenges
- CAPTCHA challenges
- Browser integrity checks

→ See: *WAF*, *CDN*

---

### WAF (Web Application Firewall)
Security system that filters HTTP traffic. Can block scrapers.

**Major WAFs**: Cloudflare, Akamai, AWS WAF, Imperva

---

### JavaScript Challenge
Requiring JavaScript execution to access content. Blocks simple HTTP scrapers.

**Solution**: Use headless browsers (Puppeteer, Playwright)

---

### IP Ban
Blocking requests from specific IP addresses.

**Types**:
- Temporary (minutes to hours)
- Permanent
- Range ban (entire subnet)

→ See: *Proxy*, *IP Rotation*

---

## 7. Authentication & Sessions

### Authentication
Proving identity to access protected resources.

**Types**:
- Username/password login
- API keys
- OAuth tokens
- Session cookies

---

### Cookie
Small data stored by browser, sent with subsequent requests. Used for session management.

```python
# Access cookies
response.cookies["session_id"]

# Send cookies
requests.get(url, cookies={"session": "abc123"})
```

→ See: *Session*, *Headers*

---

### Session Cookie
Cookie that expires when browser closes. Common for login sessions.

---

### Persistent Cookie
Cookie with explicit expiration date. Survives browser restarts.

---

### Login Flow
Sequence of requests to authenticate with a website.

```python
session = requests.Session()

# 1. Get login page (may set initial cookies)
session.get("https://example.com/login")

# 2. Submit credentials
session.post("https://example.com/login", data={
    "username": "user",
    "password": "pass"
})

# 3. Access protected content
response = session.get("https://example.com/dashboard")
```

---

### CSRF Token
Cross-Site Request Forgery token. Hidden form field required for POST requests.

```python
# Extract CSRF token from page
csrf = soup.select_one("input[name='csrf_token']")["value"]

# Include in POST request
session.post(url, data={"csrf_token": csrf, ...})
```

---

### OAuth
Authorization framework for API access. Used by Google, Facebook, Twitter APIs.

**Flow**: Redirect to provider → User authorizes → Receive token → Use token

---

### API Key
Secret string for authenticating API requests.

```python
headers = {"Authorization": "Bearer YOUR_API_KEY"}
requests.get("https://api.example.com/data", headers=headers)
```

---

### Bearer Token
Authentication token sent in Authorization header.

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

---

## 8. Data Processing

### Data Cleaning
Transforming raw data into consistent, valid format.

**Operations**:
- Trim whitespace
- Standardize formats
- Handle nulls
- Fix encoding
- Remove duplicates

→ See: *Pipeline*, *Validation*

---

### Normalization
Converting data to standard format.

```python
# Phone normalization
"(212) 555-1234" → "+12125551234"

# Date normalization  
"Jan 15, 2024" → "2024-01-15"
```

---

### Deduplication
Removing duplicate records.

**Methods**:
- Exact match (hash comparison)
- Fuzzy match (similarity threshold)
- Key-based (same ID = duplicate)

---

### Entity Resolution
Determining when different records refer to the same real-world entity.

```
"Joe's Pizza" (Yelp)     ─┐
"Joe's Pizza NYC" (Google) ├── Same business
"Joes Pizza" (TripAdvisor) ─┘
```

→ See: *Deduplication*, *Record Matching*

---

### Schema
Structure definition for data records.

```python
BUSINESS_SCHEMA = {
    "name": str,
    "address": str,
    "phone": str,
    "rating": float,
    "categories": list
}
```

---

### JSON (JavaScript Object Notation)
Lightweight data format. Standard for API responses and data storage.

```json
{
  "name": "Joe's Pizza",
  "rating": 4.5,
  "categories": ["pizza", "italian"]
}
```

---

### JSONL (JSON Lines)
One JSON object per line. Good for large datasets and streaming.

```
{"id": 1, "name": "Item 1"}
{"id": 2, "name": "Item 2"}
{"id": 3, "name": "Item 3"}
```

---

### CSV (Comma-Separated Values)
Simple tabular format. Good for spreadsheets.

```csv
name,rating,phone
"Joe's Pizza",4.5,"212-555-1234"
"Bob's Burgers",4.2,"212-555-5678"
```

---

## 9. Infrastructure & Scaling

### Concurrency
Running multiple operations simultaneously.

```python
import asyncio

async def fetch_all(urls):
    tasks = [fetch(url) for url in urls]
    return await asyncio.gather(*tasks)
```

---

### Parallelism
True simultaneous execution across multiple CPU cores.

```python
from multiprocessing import Pool

with Pool(4) as p:
    results = p.map(scrape_page, urls)
```

---

### Queue
Data structure for managing work items. First-in, first-out (FIFO).

```python
from queue import Queue

work_queue = Queue()
work_queue.put(url)
url = work_queue.get()
```

---

### Distributed Crawling
Spreading crawling across multiple machines.

**Tools**: Scrapy-Redis, Celery, custom solutions

---

### Job Scheduler
System for running tasks at specified times.

**Tools**: cron, Airflow, Celery Beat

---

### Checkpoint
Saved state allowing resume after interruption.

```python
# Save progress
with open("checkpoint.json", "w") as f:
    json.dump({"processed": processed_urls}, f)

# Resume from checkpoint
checkpoint = json.load(open("checkpoint.json"))
```

---

### Dead Letter Queue
Storage for failed items that couldn't be processed.

```python
if not process(item):
    dead_letter_queue.put(item)
```

---

## 10. Legal & Ethical

### robots.txt
File specifying crawler access rules.

```
User-agent: *
Disallow: /private/
Disallow: /api/
Crawl-delay: 10

User-agent: Googlebot
Allow: /
```

→ See: *Crawl-delay*, *User-agent*

---

### Crawl-delay
robots.txt directive specifying seconds between requests.

```
Crawl-delay: 10  # Wait 10 seconds between requests
```

---

### Terms of Service (ToS)
Legal agreement governing website use. May prohibit scraping.

**Note**: ToS enforceability varies by jurisdiction.

→ See: *Legal Considerations*

---

### Rate Respect
Ethical principle of not overwhelming target servers.

**Guidelines**:
- Respect robots.txt
- Honor rate limits
- Add delays between requests
- Identify your bot
- Scrape during off-peak hours

---

### Public Data
Information freely accessible without authentication.

**Generally safer to scrape than private/gated data.**

---

### PII (Personally Identifiable Information)
Data that can identify individuals. Handle with care.

**Examples**: Names, emails, phone numbers, addresses

---

### GDPR
EU regulation on data protection. Affects how personal data can be collected and stored.

---

### CCPA
California Consumer Privacy Act. Similar to GDPR for California residents.

---

## Quick Reference: Common Acronyms

| Acronym | Full Form |
|---------|-----------|
| API | Application Programming Interface |
| CAPTCHA | Completely Automated Public Turing test... |
| CDN | Content Delivery Network |
| CORS | Cross-Origin Resource Sharing |
| CSRF | Cross-Site Request Forgery |
| CSS | Cascading Style Sheets |
| DOM | Document Object Model |
| ETL | Extract, Transform, Load |
| HTML | HyperText Markup Language |
| HTTP | HyperText Transfer Protocol |
| JSON | JavaScript Object Notation |
| PII | Personally Identifiable Information |
| SSL | Secure Sockets Layer |
| TLS | Transport Layer Security |
| ToS | Terms of Service |
| URL | Uniform Resource Locator |
| WAF | Web Application Firewall |
| XML | eXtensible Markup Language |

---

*Next: [04_data_extraction_taxonomy.md](04_data_extraction_taxonomy.md) - Classifying data extraction approaches*
