# Data Extraction Taxonomy

> **A Complete Classification of Web Data Extraction Approaches**

This document provides a structured framework for understanding and categorizing the different methods, techniques, and strategies used in web data extraction. Use this taxonomy to choose the right approach for your specific use case.

---

## Taxonomy Overview

```
Data Extraction
├── By Source Type
│   ├── HTML Pages
│   ├── APIs
│   ├── Feeds
│   └── Files
├── By Technique
│   ├── Static Extraction
│   ├── Dynamic Extraction
│   └── Hybrid Extraction
├── By Scale
│   ├── Single Page
│   ├── Site-Wide
│   └── Web-Scale
├── By Authentication
│   ├── Public
│   ├── Authenticated
│   └── Privileged
└── By Data Structure
    ├── Structured
    ├── Semi-Structured
    └── Unstructured
```

---

## 1. Classification by Source Type

### 1.1 HTML Page Extraction

Extracting data from rendered web pages.

| Subtype | Description | Example |
|---------|-------------|---------|
| **Static HTML** | Server-rendered pages, no JS needed | Wikipedia articles |
| **Dynamic HTML** | JavaScript-rendered content | React/Vue SPAs |
| **Paginated** | Data spread across multiple pages | Search results |
| **Infinite Scroll** | Content loaded on scroll | Social media feeds |
| **Tabular** | Data in HTML tables | Financial reports |
| **Form-Based** | Data behind form submissions | Search interfaces |

**Tools**: BeautifulSoup, lxml, Scrapy (static); Playwright, Puppeteer (dynamic)

---

### 1.2 API Extraction

Extracting data from programmatic interfaces.

| Subtype | Description | Example |
|---------|-------------|---------|
| **REST API** | Standard HTTP endpoints | Twitter API |
| **GraphQL** | Query-based API | GitHub GraphQL |
| **JSON Endpoints** | Unofficial JSON responses | Hidden site APIs |
| **XML/SOAP** | Legacy enterprise APIs | Banking systems |
| **WebSocket** | Real-time data streams | Stock tickers |

**Characteristics**:
- Structured responses (JSON/XML)
- Often requires authentication
- Rate limits explicitly defined
- More stable than HTML scraping

```python
# REST API extraction
response = requests.get(
    "https://api.example.com/v1/products",
    headers={"Authorization": "Bearer TOKEN"}
)
data = response.json()
```

---

### 1.3 Feed Extraction

Extracting data from syndication formats.

| Subtype | Description | Example |
|---------|-------------|---------|
| **RSS** | Really Simple Syndication | Blog feeds |
| **Atom** | Alternative to RSS | News sites |
| **JSON Feed** | Modern JSON-based feed | Podcasts |
| **Sitemap XML** | Site structure listing | SEO sitemaps |

**Characteristics**:
- Designed for machine consumption
- Standardized formats
- Usually public
- Limited to what publisher chooses to share

```python
import feedparser
feed = feedparser.parse("https://example.com/rss")
for entry in feed.entries:
    print(entry.title, entry.link)
```

---

### 1.4 File Extraction

Extracting data from downloadable documents.

| Subtype | Description | Tools |
|---------|-------------|-------|
| **PDF** | Portable Document Format | pdfplumber, PyMuPDF |
| **Excel/CSV** | Spreadsheet data | pandas, openpyxl |
| **Word/Docs** | Document text | python-docx |
| **Images** | Text via OCR | Tesseract, Google Vision |
| **Archives** | ZIP, compressed data | zipfile, tarfile |

```python
# PDF extraction
import pdfplumber
with pdfplumber.open("document.pdf") as pdf:
    text = pdf.pages[0].extract_text()
    tables = pdf.pages[0].extract_tables()
```

---

## 2. Classification by Technique

### 2.1 Static Extraction

Parsing HTML/data as delivered by server, no JavaScript execution.

```
Request → Response (HTML) → Parse → Extract
```

**When to Use**:
- ✅ Content visible in "View Source"
- ✅ No JavaScript-dependent content
- ✅ Speed is priority
- ✅ High-volume extraction

**Tools**: requests + BeautifulSoup, Scrapy, httpx

**Advantages**:
- Fast (no browser overhead)
- Low resource usage
- Easy to scale
- Simple to implement

**Limitations**:
- Cannot handle JS-rendered content
- May miss dynamic elements
- AJAX data not accessible

```python
# Static extraction
import requests
from bs4 import BeautifulSoup

html = requests.get(url).text
soup = BeautifulSoup(html, "html.parser")
data = soup.select("div.product")
```

---

### 2.2 Dynamic Extraction

Using browser automation to render JavaScript before extraction.

```
Launch Browser → Navigate → Wait for JS → Render → Extract
```

**When to Use**:
- ✅ Content loaded via JavaScript
- ✅ Single Page Applications (React, Vue, Angular)
- ✅ Infinite scroll pages
- ✅ Content behind interactions (clicks, hovers)

**Tools**: Playwright, Puppeteer, Selenium

**Advantages**:
- Handles any JS framework
- Can interact with page (click, scroll, type)
- Renders exactly like real browser
- Can capture network requests

**Limitations**:
- Slow (browser overhead)
- High resource usage
- Complex to scale
- More detectable

```python
# Dynamic extraction with Playwright
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url)
    page.wait_for_selector("div.product")
    
    # Now extract from rendered content
    products = page.query_selector_all("div.product")
```

---

### 2.3 Hybrid Extraction

Combining static and dynamic techniques strategically.

```
Static Request → Check if JS needed → Dynamic if required → Extract
```

**Strategies**:

| Strategy | Description |
|----------|-------------|
| **API Discovery** | Use browser to find hidden JSON APIs, then call directly |
| **Selective Rendering** | Static for most pages, browser for JS-heavy pages |
| **Cookie Harvesting** | Browser for login, requests for data extraction |
| **Initial + Incremental** | Browser for first load, static for pagination |

```python
# Hybrid: Use browser to get cookies, then static requests
from playwright.sync_api import sync_playwright
import requests

# Get authenticated session via browser
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com/login")
    page.fill("#username", "user")
    page.fill("#password", "pass")
    page.click("#submit")
    
    # Extract cookies
    cookies = page.context.cookies()

# Use cookies with fast static requests
session = requests.Session()
for cookie in cookies:
    session.cookies.set(cookie["name"], cookie["value"])

# Now scrape efficiently
for page_num in range(1, 100):
    response = session.get(f"https://example.com/data?page={page_num}")
```

---

## 3. Classification by Scale

### 3.1 Single Page Extraction

Extracting data from one specific page or a small set of known URLs.

**Characteristics**:
- Known URLs
- One-time or infrequent runs
- Simple implementation
- Minimal infrastructure

**Use Cases**:
- Grabbing specific product details
- One-time data collection
- Testing extraction logic

```python
# Single page - simple and direct
def extract_product(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    return {
        "name": soup.select_one("h1").text,
        "price": soup.select_one(".price").text
    }

product = extract_product("https://store.com/product/123")
```

---

### 3.2 Site-Wide Extraction

Systematically extracting data from an entire website or large sections.

**Characteristics**:
- URL discovery required (spidering)
- Pagination handling
- Rate limiting essential
- Error recovery needed
- Incremental updates

**Use Cases**:
- Complete product catalog
- Full directory listing
- Site backup/archival
- Competitive monitoring

```python
# Site-wide extraction pattern
class SiteScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited = set()
        self.queue = [base_url]
        self.data = []
    
    def run(self):
        while self.queue:
            url = self.queue.pop(0)
            if url in self.visited:
                continue
            
            self.visited.add(url)
            page_data, new_urls = self.process_page(url)
            
            if page_data:
                self.data.append(page_data)
            
            for new_url in new_urls:
                if self.is_valid(new_url):
                    self.queue.append(new_url)
            
            time.sleep(1)  # Rate limiting
```

---

### 3.3 Web-Scale Extraction

Extracting data across multiple websites or the broader web.

**Characteristics**:
- Multiple domains
- Distributed architecture
- Massive storage requirements
- Complex deduplication
- Legal considerations per site

**Use Cases**:
- Search engine indexing
- Price comparison across retailers
- News aggregation
- Research datasets

**Architecture**:
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   URL       │────▶│   Worker    │────▶│   Storage   │
│   Frontier  │     │   Cluster   │     │   Cluster   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │
       │    ┌──────────────┘
       │    │
       ▼    ▼
┌─────────────────┐
│   Coordinator   │
│   (Scheduling,  │
│    Dedup, etc)  │
└─────────────────┘
```

**Tools**: Scrapy-Redis, Apache Nutch, custom distributed systems

---

## 4. Classification by Authentication

### 4.1 Public Extraction

Data accessible without any authentication.

**Characteristics**:
- No login required
- Visible to search engines
- Generally lower legal risk
- Often explicitly allowed

**Examples**:
- Wikipedia articles
- Public business listings
- News articles
- Government data portals

---

### 4.2 Authenticated Extraction

Data requiring user account login.

**Characteristics**:
- Session management required
- May require solving CAPTCHAs
- Cookie/token handling
- Account may be suspended
- ToS often prohibits scraping

**Challenges**:
- Maintaining login state
- Multi-factor authentication
- Session expiration
- Account limits

```python
# Authenticated extraction pattern
class AuthenticatedScraper:
    def __init__(self):
        self.session = requests.Session()
    
    def login(self, username, password):
        # Get login page (may set cookies, CSRF)
        login_page = self.session.get("https://example.com/login")
        csrf = extract_csrf(login_page.text)
        
        # Submit credentials
        response = self.session.post(
            "https://example.com/login",
            data={
                "username": username,
                "password": password,
                "csrf_token": csrf
            }
        )
        
        return "dashboard" in response.url
    
    def scrape(self, url):
        # Session maintains auth cookies
        return self.session.get(url)
```

---

### 4.3 Privileged Extraction

Data requiring special access levels (admin, paid subscription, internal).

**Characteristics**:
- Higher data quality/completeness
- API access may be available
- Explicit permission often required
- Legal agreements typical

**Examples**:
- Paid API subscriptions
- Partner data feeds
- Internal company data
- Licensed datasets

**Note**: This often moves from "scraping" to "integration" territory.

---

## 5. Classification by Data Structure

### 5.1 Structured Data Extraction

Data in well-defined, consistent formats.

**Sources**:
- API responses (JSON/XML)
- Database exports
- HTML tables
- CSV/Excel files

**Characteristics**:
- Predictable schema
- Easy to parse
- Minimal cleaning needed
- Direct to database

```python
# Structured: API JSON
response = requests.get("https://api.example.com/products")
products = response.json()["data"]  # Already structured
```

---

### 5.2 Semi-Structured Data Extraction

Data with some organization but inconsistent formatting.

**Sources**:
- HTML pages with consistent layout
- Varying API responses
- Documents with recognizable sections

**Characteristics**:
- Identifiable patterns
- Requires selectors/parsing
- Some cleaning needed
- Schema enforcement required

```python
# Semi-structured: HTML with patterns
soup = BeautifulSoup(html, "html.parser")
products = []
for card in soup.select("div.product-card"):
    products.append({
        "name": card.select_one("h2").text.strip(),
        "price": parse_price(card.select_one(".price").text),
        "rating": extract_rating(card)  # May not exist
    })
```

---

### 5.3 Unstructured Data Extraction

Data without predefined organization.

**Sources**:
- Free-form text (articles, reviews)
- Images
- PDFs without structure
- Social media posts

**Characteristics**:
- Requires NLP/ML techniques
- Heavy processing needed
- Ambiguous extraction
- Lower accuracy

**Techniques**:
- Named Entity Recognition (NER)
- Regular expressions
- OCR for images
- Text classification

```python
# Unstructured: Extract entities from text
import spacy
nlp = spacy.load("en_core_web_sm")

doc = nlp(article_text)
entities = {
    "people": [ent.text for ent in doc.ents if ent.label_ == "PERSON"],
    "orgs": [ent.text for ent in doc.ents if ent.label_ == "ORG"],
    "dates": [ent.text for ent in doc.ents if ent.label_ == "DATE"]
}
```

---

## 6. Classification by Update Pattern

### 6.1 One-Time Extraction

Single extraction run, no updates planned.

**Use Cases**:
- Historical data collection
- Research datasets
- Migration projects
- One-off analysis

---

### 6.2 Periodic Extraction

Scheduled re-extraction at fixed intervals.

| Frequency | Use Case |
|-----------|----------|
| **Real-time** | Stock prices, news |
| **Hourly** | Social media trends |
| **Daily** | Product prices, listings |
| **Weekly** | Directory updates |
| **Monthly** | Archive snapshots |

```python
# Periodic extraction with scheduling
from apscheduler.schedulers.blocking import BlockingScheduler

def daily_scrape():
    data = scrape_all_products()
    save_to_database(data)

scheduler = BlockingScheduler()
scheduler.add_job(daily_scrape, 'cron', hour=2)  # 2 AM daily
scheduler.start()
```

---

### 6.3 Incremental Extraction

Only extracting new or changed data.

**Strategies**:

| Strategy | How It Works |
|----------|--------------|
| **Timestamp-based** | Only items modified since last run |
| **ID-based** | Only items with ID > last seen |
| **Hash-based** | Compare content hash to detect changes |
| **Diff-based** | Compare full content, store delta |

```python
# Incremental extraction
def incremental_scrape(last_run_timestamp):
    new_items = []
    
    for item in scrape_listing():
        if item["updated_at"] > last_run_timestamp:
            new_items.append(item)
        else:
            break  # Assuming sorted by date, stop when old items found
    
    return new_items
```

---

### 6.4 Event-Driven Extraction

Triggered by external events rather than schedule.

**Triggers**:
- Webhook notifications
- RSS feed updates
- Manual requests
- Monitoring alerts

```python
# Event-driven: Webhook trigger
from flask import Flask, request

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    event = request.json
    if event["type"] == "new_product":
        scrape_product(event["product_url"])
    return "OK"
```

---

## 7. Decision Framework

### Choosing Your Approach

```
START
  │
  ▼
Is data in an API? ──Yes──▶ API Extraction
  │                         (REST, GraphQL)
  No
  │
  ▼
Is data in feeds? ──Yes──▶ Feed Extraction
  │                        (RSS, Atom)
  No
  │
  ▼
Is JavaScript needed? ──Yes──▶ Dynamic Extraction
  │                            (Playwright, Puppeteer)
  No
  │
  ▼
Static Extraction
(requests, Scrapy)
```

### Complexity vs. Volume Matrix

|                    | Low Volume | High Volume |
|--------------------|------------|-------------|
| **Simple (Static)** | requests + BS4 | Scrapy |
| **Complex (Dynamic)** | Playwright | Playwright + Queue |
| **API** | requests | async + rate limiting |

### Tool Selection Guide

| Scenario | Recommended Tool |
|----------|-----------------|
| Quick one-off scrape | requests + BeautifulSoup |
| Large-scale static | Scrapy |
| JavaScript-heavy | Playwright |
| API integration | httpx (async) |
| Browser automation | Playwright/Puppeteer |
| Distributed crawling | Scrapy-Redis |
| PDF extraction | pdfplumber |
| Data pipeline | Scrapy + custom pipeline |

---

## 8. Taxonomy Summary Table

| Dimension | Categories |
|-----------|------------|
| **Source Type** | HTML, API, Feed, File |
| **Technique** | Static, Dynamic, Hybrid |
| **Scale** | Single Page, Site-Wide, Web-Scale |
| **Authentication** | Public, Authenticated, Privileged |
| **Data Structure** | Structured, Semi-Structured, Unstructured |
| **Update Pattern** | One-Time, Periodic, Incremental, Event-Driven |

---

## The Leaf Cutter Ant Perspective

Each extraction type maps to ant colony behavior:

| Extraction Type | Ant Equivalent |
|-----------------|----------------|
| **Static HTML** | Cutting leaves from a known plant |
| **Dynamic JS** | Waiting for leaves to unfurl before cutting |
| **API** | Following a trail directly to food |
| **Site-Wide** | Systematically harvesting an entire plant |
| **Incremental** | Returning to check for new growth |

Our ants specialize based on the terrain they face.

---

*This completes the Terminology section. Next: [../01_technical_operations/](../01_technical_operations/) - How the web works for scrapers*
