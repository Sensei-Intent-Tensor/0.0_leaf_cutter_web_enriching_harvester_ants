# Python Scraping Stack

> **The Complete Python Toolkit for Web Scraping**

Python is the dominant language for web scraping. This document covers the full ecosystem of libraries and tools available.

---

## The Python Scraping Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                    HIGH-LEVEL FRAMEWORKS                        │
│                    Scrapy, Crawlee                              │
├─────────────────────────────────────────────────────────────────┤
│                    BROWSER AUTOMATION                           │
│                    Playwright, Selenium, Puppeteer              │
├─────────────────────────────────────────────────────────────────┤
│                    HTTP CLIENTS                                 │
│                    requests, httpx, aiohttp                     │
├─────────────────────────────────────────────────────────────────┤
│                    PARSING                                      │
│                    BeautifulSoup, lxml, parsel                  │
├─────────────────────────────────────────────────────────────────┤
│                    DATA PROCESSING                              │
│                    pandas, json, csv                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. HTTP Clients

### requests

The most popular HTTP library. Simple and intuitive.

```python
import requests

# Basic GET
response = requests.get('https://example.com')

# With headers and params
response = requests.get(
    'https://example.com/search',
    params={'q': 'python', 'page': 1},
    headers={'User-Agent': 'MyBot/1.0'},
    timeout=30
)

# POST with form data
response = requests.post(
    'https://example.com/login',
    data={'username': 'user', 'password': 'pass'}
)

# POST with JSON
response = requests.post(
    'https://api.example.com/data',
    json={'key': 'value'}
)

# Session (maintains cookies)
session = requests.Session()
session.get('https://example.com/login')
session.post('https://example.com/login', data=credentials)
session.get('https://example.com/dashboard')  # Now authenticated
```

**When to use:** Most scraping projects. Simple, synchronous requests.

### httpx

Modern async-capable HTTP client. Similar API to requests.

```python
import httpx

# Sync usage (like requests)
response = httpx.get('https://example.com')

# Async usage
import asyncio

async def fetch_all(urls):
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return responses

# HTTP/2 support
client = httpx.Client(http2=True)
```

**When to use:** Need async support, HTTP/2, or drop-in requests replacement.

### aiohttp

Pure async HTTP client for high-concurrency scraping.

```python
import aiohttp
import asyncio

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)

# Run
urls = ['https://example.com/1', 'https://example.com/2']
results = asyncio.run(fetch_all(urls))
```

**When to use:** High-volume concurrent scraping.

### curl_cffi

Impersonates real browser TLS fingerprints.

```python
from curl_cffi import requests

# Impersonate Chrome
response = requests.get(
    'https://protected-site.com',
    impersonate='chrome'
)
```

**When to use:** Sites that detect TLS fingerprints.

---

## 2. HTML Parsing

### BeautifulSoup

Most beginner-friendly parser. Forgiving of bad HTML.

```python
from bs4 import BeautifulSoup

html = '<div class="product"><h2>Widget</h2><span class="price">$99</span></div>'
soup = BeautifulSoup(html, 'html.parser')  # or 'lxml' for speed

# Find elements
title = soup.find('h2').text  # 'Widget'
price = soup.find('span', class_='price').text  # '$99'

# CSS selectors
products = soup.select('div.product')
prices = soup.select('.product .price')

# Find all
all_links = soup.find_all('a')
all_divs_with_class = soup.find_all('div', class_='item')

# Navigate tree
parent = soup.find('h2').parent
siblings = soup.find('h2').next_siblings
```

**When to use:** Most HTML parsing tasks, especially with messy HTML.

### lxml

Fastest parser. Also supports XPath.

```python
from lxml import html

tree = html.fromstring(page_content)

# XPath
titles = tree.xpath('//h2/text()')
prices = tree.xpath('//span[@class="price"]/text()')
links = tree.xpath('//a/@href')

# CSS selectors (via cssselect)
products = tree.cssselect('div.product')
```

**When to use:** High-volume parsing, need XPath, or performance-critical.

### parsel

Combines best of BeautifulSoup and lxml. Used by Scrapy.

```python
from parsel import Selector

sel = Selector(text=html)

# CSS selectors
titles = sel.css('h2::text').getall()
prices = sel.css('.price::text').get()

# XPath
links = sel.xpath('//a/@href').getall()

# Chaining
products = sel.css('div.product')
for product in products:
    title = product.css('h2::text').get()
    price = product.xpath('.//span[@class="price"]/text()').get()
```

**When to use:** When you want both CSS and XPath in one interface.

---

## 3. Browser Automation

### Playwright

Modern, fast browser automation. Recommended choice.

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    page.goto('https://example.com')
    page.wait_for_selector('.product')
    
    # Interact
    page.fill('input[name="search"]', 'python')
    page.click('button[type="submit"]')
    
    # Extract
    products = page.query_selector_all('.product')
    for product in products:
        title = product.query_selector('h2').inner_text()
    
    # Get HTML for BeautifulSoup
    html = page.content()
    
    browser.close()

# Async version
from playwright.async_api import async_playwright

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://example.com')
        # ...
```

**When to use:** JavaScript-rendered sites, complex interactions, modern default.

### Selenium

Established browser automation. Large ecosystem.

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Setup
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

try:
    driver.get('https://example.com')
    
    # Wait for element
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.product')))
    
    # Find elements
    products = driver.find_elements(By.CSS_SELECTOR, '.product')
    
    # Interact
    search = driver.find_element(By.NAME, 'search')
    search.send_keys('python')
    search.submit()
    
finally:
    driver.quit()
```

**When to use:** Legacy projects, specific browser testing needs.

### undetected-chromedriver

Selenium wrapper that bypasses bot detection.

```python
import undetected_chromedriver as uc

driver = uc.Chrome(headless=True)
driver.get('https://protected-site.com')
```

**When to use:** Sites with strong bot detection using Selenium.

---

## 4. Scraping Frameworks

### Scrapy

Industrial-strength scraping framework.

```python
import scrapy

class ProductSpider(scrapy.Spider):
    name = 'products'
    start_urls = ['https://example.com/products']
    
    def parse(self, response):
        for product in response.css('div.product'):
            yield {
                'title': product.css('h2::text').get(),
                'price': product.css('.price::text').get(),
                'url': product.css('a::attr(href)').get(),
            }
        
        # Follow pagination
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

# Run: scrapy crawl products -o products.json
```

**Features:**
- Built-in concurrency
- Request scheduling
- Item pipelines
- Middleware system
- robots.txt handling
- Caching

**When to use:** Large-scale scraping, complex crawls, production systems.

### Crawlee (Python)

Modern scraping framework from Apify.

```python
from crawlee.playwright_crawler import PlaywrightCrawler

async def main():
    crawler = PlaywrightCrawler()
    
    @crawler.router.default_handler
    async def request_handler(context):
        page = context.page
        await page.wait_for_selector('.product')
        
        products = await page.query_selector_all('.product')
        for product in products:
            title = await product.inner_text()
            context.log.info(f'Found: {title}')
    
    await crawler.run(['https://example.com'])

asyncio.run(main())
```

**When to use:** Modern alternative to Scrapy with better async support.

---

## 5. Anti-Detection Tools

### cloudscraper

Bypasses Cloudflare protection.

```python
import cloudscraper

scraper = cloudscraper.create_scraper()
response = scraper.get('https://cloudflare-protected.com')
```

### playwright-stealth

Makes Playwright less detectable.

```python
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    stealth_sync(page)  # Apply stealth
    page.goto('https://bot-detection-site.com')
```

### fake-useragent

Generates random user agents.

```python
from fake_useragent import UserAgent

ua = UserAgent()
headers = {'User-Agent': ua.random}
```

---

## 6. Data Processing

### pandas

Data manipulation and analysis.

```python
import pandas as pd

# From scraped data
data = [
    {'title': 'Widget', 'price': 99.99},
    {'title': 'Gadget', 'price': 149.99},
]
df = pd.DataFrame(data)

# Clean and transform
df['price'] = df['price'].astype(float)
df = df.drop_duplicates()

# Export
df.to_csv('products.csv', index=False)
df.to_json('products.json', orient='records')
```

### json / csv

Standard library for data export.

```python
import json
import csv

# JSON
with open('data.json', 'w') as f:
    json.dump(scraped_data, f, indent=2)

# JSONL (one JSON per line)
with open('data.jsonl', 'w') as f:
    for item in scraped_data:
        f.write(json.dumps(item) + '\n')

# CSV
with open('data.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['title', 'price'])
    writer.writeheader()
    writer.writerows(scraped_data)
```

---

## 7. Specialty Tools

### pdfplumber

Extract text and tables from PDFs.

```python
import pdfplumber

with pdfplumber.open('document.pdf') as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        tables = page.extract_tables()
```

### pytesseract

OCR for image-based text.

```python
import pytesseract
from PIL import Image

image = Image.open('screenshot.png')
text = pytesseract.image_to_string(image)
```

### feedparser

Parse RSS/Atom feeds.

```python
import feedparser

feed = feedparser.parse('https://example.com/rss')
for entry in feed.entries:
    print(entry.title, entry.link)
```

---

## Quick Reference

| Task | Library | Install |
|------|---------|---------|
| HTTP requests | requests | `pip install requests` |
| Async HTTP | httpx, aiohttp | `pip install httpx` |
| HTML parsing | BeautifulSoup | `pip install beautifulsoup4` |
| Fast parsing | lxml | `pip install lxml` |
| Browser automation | Playwright | `pip install playwright` |
| Framework | Scrapy | `pip install scrapy` |
| Cloudflare bypass | cloudscraper | `pip install cloudscraper` |
| Data processing | pandas | `pip install pandas` |
| PDF extraction | pdfplumber | `pip install pdfplumber` |
| OCR | pytesseract | `pip install pytesseract` |

---

## Recommended Stacks

### Simple Scraping
```
requests + BeautifulSoup + json
```

### JavaScript Sites
```
Playwright + BeautifulSoup + pandas
```

### Large Scale
```
Scrapy + lxml + custom pipelines
```

### Maximum Stealth
```
curl_cffi + playwright-stealth + residential proxies
```

---

*Next: [02_browser_automation_compared.md](02_browser_automation_compared.md) - Playwright vs Selenium vs Puppeteer*
