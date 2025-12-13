# 04_tools_ecosystem

> **The Complete Scraper's Toolbox**

This section covers the tools, libraries, and services that make up the web scraping ecosystem. From HTTP clients to cloud storage, everything you need to know.

---

## 📚 Documents in This Section

| # | Document | Lines | Description |
|---|----------|-------|-------------|
| 01 | [Python Scraping Stack](01_python_scraping_stack.md) | 555 | Complete Python toolkit overview |
| 02 | [Browser Automation Compared](02_browser_automation_compared.md) | 438 | Playwright vs Selenium vs Puppeteer |
| 03 | [Parsing Libraries Guide](03_parsing_libraries_guide.md) | 519 | BeautifulSoup, lxml, parsel, and more |
| 04 | [Proxy Services Overview](04_proxy_services_overview.md) | 418 | Commercial proxy providers |
| 05 | [Data Storage Options](05_data_storage_options.md) | 531 | Files, databases, and cloud storage |

**Total: 2,461 lines of practical tool guidance**

---

## 🎯 Quick Tool Selection

### By Task

| Task | Recommended Tool |
|------|------------------|
| **Simple HTTP requests** | requests |
| **Async HTTP** | httpx or aiohttp |
| **HTML parsing** | BeautifulSoup (easy) or lxml (fast) |
| **JavaScript sites** | Playwright |
| **Large-scale crawling** | Scrapy |
| **Cloudflare bypass** | cloudscraper |
| **Anti-detection** | playwright-stealth |
| **Data export** | pandas or json |

### By Skill Level

```
Beginner:
├── requests + BeautifulSoup
├── json for storage
└── No proxies (start simple)

Intermediate:
├── Playwright for JS sites
├── SQLite for storage
├── Smartproxy for proxies
└── cloudscraper for protection bypass

Advanced:
├── Scrapy for scale
├── Custom middleware
├── PostgreSQL/MongoDB
├── Bright Data for enterprise proxies
```

---

## 🛠️ The Recommended Stack

### Minimal Setup
```bash
pip install requests beautifulsoup4
```

### Standard Setup
```bash
pip install requests beautifulsoup4 lxml pandas
pip install playwright && playwright install
```

### Full Setup
```bash
pip install requests beautifulsoup4 lxml pandas
pip install playwright && playwright install
pip install scrapy cloudscraper fake-useragent
pip install aiohttp httpx
```

---

## 📊 Tool Comparison Summary

### HTTP Clients

| Library | Async | Speed | Ease | When to Use |
|---------|-------|-------|------|-------------|
| **requests** | No | Medium | Easy | Default choice |
| **httpx** | Yes | Fast | Easy | Need async or HTTP/2 |
| **aiohttp** | Yes | Fast | Medium | High concurrency |
| **curl_cffi** | Yes | Fast | Medium | TLS fingerprinting |

### Parsers

| Library | Speed | XPath | CSS | Best For |
|---------|-------|-------|-----|----------|
| **BeautifulSoup** | Medium | No | Yes | Messy HTML, beginners |
| **lxml** | Fast | Yes | Yes | Performance, XPath |
| **parsel** | Fast | Yes | Yes | Scrapy users |

### Browser Automation

| Tool | Speed | Stealth | API | Best For |
|------|-------|---------|-----|----------|
| **Playwright** | Fast | Good | Modern | New projects |
| **Selenium** | Slow | Poor | Legacy | Existing code |
| **Puppeteer** | Fast | Good | Modern | Node.js projects |

### Storage

| Option | Scale | Queries | Setup | Best For |
|--------|-------|---------|-------|----------|
| **JSONL** | Small | None | None | Quick prototypes |
| **SQLite** | Medium | SQL | Minimal | Local projects |
| **PostgreSQL** | Large | SQL | Moderate | Production |
| **MongoDB** | Large | Limited | Moderate | Flexible schemas |
| **S3/GCS** | Huge | None | Moderate | Archive |

---

## 🔗 Related Sections

- **[01_technical_operations/](../01_technical_operations/)** - HTTP fundamentals these tools use
- **[02_anti_scraping_tech/](../02_anti_scraping_tech/)** - What you're using these tools against
- **[03_legal_ethical/](../03_legal_ethical/)** - Using these tools responsibly

---

## 💡 Common Stacks

### E-commerce Scraping
```python
# Stack: requests + BeautifulSoup + pandas
import requests
from bs4 import BeautifulSoup
import pandas as pd

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'lxml')
# Extract products...
df = pd.DataFrame(products)
df.to_csv('products.csv')
```

### JavaScript-Heavy Sites
```python
# Stack: Playwright + BeautifulSoup
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url)
    page.wait_for_selector('.product')
    html = page.content()
    browser.close()

soup = BeautifulSoup(html, 'lxml')
# Extract data...
```

### Large-Scale Crawling
```python
# Stack: Scrapy
import scrapy

class ProductSpider(scrapy.Spider):
    name = 'products'
    start_urls = ['https://example.com']
    
    def parse(self, response):
        for product in response.css('.product'):
            yield {
                'title': product.css('h2::text').get(),
                'price': product.css('.price::text').get()
            }
```

---

## 📈 Performance Tips

```python
# 1. Use sessions
session = requests.Session()  # Reuses connections

# 2. Use lxml parser
soup = BeautifulSoup(html, 'lxml')  # Faster than html.parser

# 3. Block unnecessary resources in browser
page.route("**/*.{png,jpg,css}", lambda r: r.abort())

# 4. Use async for volume
async with aiohttp.ClientSession() as session:
    tasks = [fetch(session, url) for url in urls]
    results = await asyncio.gather(*tasks)
```

---

*This completes the 00_foundations wiki for the Leaf Cutter Web Enriching Harvester Ants framework.*
