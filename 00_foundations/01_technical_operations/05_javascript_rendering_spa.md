# JavaScript Rendering & SPAs

> **When Static Scraping Isn't Enough**

Modern websites increasingly rely on JavaScript to render content. If your scraper only sees an empty page or "Loading...", this document is for you.

---

## The Problem

### Server-Rendered (Traditional)
```
Browser Request → Server → Complete HTML → Browser Displays

What you GET:
<html>
  <body>
    <div class="products">
      <div class="product">Real Product Data</div>
      <div class="product">More Products</div>
    </div>
  </body>
</html>
```

### Client-Rendered (Modern SPA)
```
Browser Request → Server → Skeleton HTML + JavaScript → JS Fetches Data → JS Renders

What you GET (without JS execution):
<html>
  <body>
    <div id="root"></div>
    <script src="bundle.js"></script>
  </body>
</html>
```

The actual content is loaded and rendered by JavaScript AFTER the page loads.

---

## How to Detect JavaScript-Rendered Content

### Method 1: View Source vs Inspect

1. **View Page Source** (Ctrl+U): Shows raw HTML from server
2. **Inspect Element** (F12): Shows rendered DOM after JavaScript

If they differ significantly, the page uses client-side rendering.

### Method 2: Disable JavaScript

1. Open DevTools → Settings → Debugger → Disable JavaScript
2. Reload the page
3. If content disappears, it's JavaScript-rendered

### Method 3: Check Your Scraper Output

```python
import requests
from bs4 import BeautifulSoup

response = requests.get("https://spa-site.com/products")
soup = BeautifulSoup(response.text, "html.parser")

products = soup.select("div.product")
print(f"Found: {len(products)} products")  # 0 if JS-rendered
```

### Method 4: Look for SPA Frameworks

```html
<!-- React -->
<div id="root"></div>
<div id="__next"></div>  <!-- Next.js -->

<!-- Vue -->
<div id="app"></div>

<!-- Angular -->
<app-root></app-root>

<!-- Common indicators -->
<script src="bundle.js"></script>
<script src="main.chunk.js"></script>
```

---

## Solutions Overview

| Solution | Speed | Resources | Complexity | JS Support |
|----------|-------|-----------|------------|------------|
| **Find the API** | ⚡ Fast | Low | Medium | Not needed |
| **Playwright/Puppeteer** | 🐢 Slow | High | Medium | Full |
| **Selenium** | 🐢 Slow | High | Medium | Full |
| **Splash** | 🐢 Slow | Medium | High | Full |
| **requests-html** | Medium | Medium | Low | Limited |

---

## Solution 1: Find the Hidden API (Best!)

Most SPAs fetch data from JSON APIs. Find it and call it directly.

### How to Find the API

1. Open DevTools → Network tab
2. Filter by "XHR" or "Fetch"
3. Interact with the page (load products, paginate, etc.)
4. Look for JSON responses

```
Network Tab:
Name                          Method    Status    Type
/api/products?page=1          GET       200       json
/api/products/123             GET       200       json
/graphql                      POST      200       json
```

### Call the API Directly

```python
import requests

# Instead of scraping the HTML page:
# response = requests.get("https://spa-site.com/products")

# Call the API directly:
response = requests.get(
    "https://spa-site.com/api/products",
    params={"page": 1, "limit": 20},
    headers={
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0...",
    }
)

products = response.json()["data"]
# Clean, structured data!
```

### GraphQL APIs

```python
# GraphQL uses POST with query in body
response = requests.post(
    "https://spa-site.com/graphql",
    json={
        "query": """
            query GetProducts($page: Int!) {
                products(page: $page) {
                    id
                    name
                    price
                }
            }
        """,
        "variables": {"page": 1}
    },
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
)

products = response.json()["data"]["products"]
```

---

## Solution 2: Playwright (Recommended)

Modern, fast, reliable browser automation.

### Installation

```bash
pip install playwright
playwright install  # Downloads browser binaries
```

### Basic Usage

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # Launch browser
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Navigate
    page.goto("https://spa-site.com/products")
    
    # Wait for content to load
    page.wait_for_selector("div.product")
    
    # Extract data
    products = page.query_selector_all("div.product")
    for product in products:
        name = product.query_selector("h2").inner_text()
        price = product.query_selector(".price").inner_text()
        print(f"{name}: {price}")
    
    browser.close()
```

### Waiting Strategies

```python
# Wait for specific element
page.wait_for_selector("div.product")

# Wait for element to be visible
page.wait_for_selector("div.product", state="visible")

# Wait for network to be idle
page.wait_for_load_state("networkidle")

# Wait for specific number of elements
page.wait_for_function("document.querySelectorAll('.product').length >= 10")

# Wait for text to appear
page.wait_for_selector("text=Product loaded")

# Custom timeout
page.wait_for_selector("div.product", timeout=30000)  # 30 seconds
```

### Handling Infinite Scroll

```python
from playwright.sync_api import sync_playwright

def scrape_infinite_scroll(url, max_items=100):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        
        items = []
        last_count = 0
        
        while len(items) < max_items:
            # Scroll to bottom
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            # Wait for new content
            page.wait_for_timeout(2000)  # 2 seconds
            
            # Get current items
            items = page.query_selector_all("div.item")
            
            # Check if we got new items
            if len(items) == last_count:
                break  # No more content
            last_count = len(items)
        
        # Extract data
        data = []
        for item in items[:max_items]:
            data.append({
                "title": item.query_selector("h3").inner_text(),
                "link": item.query_selector("a").get_attribute("href"),
            })
        
        browser.close()
        return data
```

### Clicking and Interacting

```python
# Click a button
page.click("button.load-more")

# Fill a form
page.fill("input#search", "python")
page.press("input#search", "Enter")

# Select dropdown
page.select_option("select#category", "electronics")

# Hover
page.hover("div.tooltip-trigger")

# Wait and click
page.wait_for_selector("button.submit")
page.click("button.submit")
```

### Extracting Data

```python
# Get text
text = page.inner_text("h1")

# Get attribute
href = page.get_attribute("a.link", "href")

# Get HTML
html = page.inner_html("div.content")

# Get full page HTML (after JS)
full_html = page.content()

# Use BeautifulSoup on rendered HTML
from bs4 import BeautifulSoup
soup = BeautifulSoup(page.content(), "html.parser")
```

### Capturing Network Requests

```python
from playwright.sync_api import sync_playwright

api_responses = []

def handle_response(response):
    if "/api/" in response.url:
        api_responses.append({
            "url": response.url,
            "status": response.status,
            "body": response.json() if "json" in response.headers.get("content-type", "") else None
        })

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    
    # Listen for responses
    page.on("response", handle_response)
    
    page.goto("https://spa-site.com/products")
    page.wait_for_load_state("networkidle")
    
    # Now api_responses contains all API calls the page made
    for resp in api_responses:
        print(f"API: {resp['url']}")
        print(f"Data: {resp['body']}")
```

---

## Solution 3: Puppeteer (Node.js)

Similar to Playwright, but JavaScript-only.

```javascript
const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({headless: true});
    const page = await browser.newPage();
    
    await page.goto('https://spa-site.com/products');
    await page.waitForSelector('div.product');
    
    const products = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('div.product')).map(el => ({
            name: el.querySelector('h2').innerText,
            price: el.querySelector('.price').innerText,
        }));
    });
    
    console.log(products);
    await browser.close();
})();
```

---

## Solution 4: Selenium (Legacy)

Older but still widely used.

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Setup headless Chrome
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

try:
    driver.get("https://spa-site.com/products")
    
    # Wait for element
    wait = WebDriverWait(driver, 10)
    products = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.product"))
    )
    
    for product in products:
        name = product.find_element(By.CSS_SELECTOR, "h2").text
        price = product.find_element(By.CSS_SELECTOR, ".price").text
        print(f"{name}: {price}")
        
finally:
    driver.quit()
```

---

## Hybrid Approach: Browser + Requests

Use browser to solve the hard parts, then switch to fast requests.

```python
from playwright.sync_api import sync_playwright
import requests

def hybrid_scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Use browser to login and get session
        page.goto("https://spa-site.com/login")
        page.fill("#username", "user")
        page.fill("#password", "pass")
        page.click("#submit")
        page.wait_for_url("**/dashboard")
        
        # Extract cookies
        cookies = context.cookies()
        
        # Also capture any API calls to find endpoints
        # ...
        
        browser.close()
    
    # Now use fast requests with the cookies
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie["name"], cookie["value"])
    
    # Scrape efficiently
    for page_num in range(1, 100):
        response = session.get(f"https://spa-site.com/api/products?page={page_num}")
        data = response.json()
        process(data)
```

---

## Performance Optimization

### Playwright Optimization

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--disable-setuid-sandbox",
            "--no-sandbox",
        ]
    )
    
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0...",
        # Block unnecessary resources
    )
    
    page = context.new_page()
    
    # Block images, CSS, fonts to speed up
    page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2}", lambda route: route.abort())
    
    page.goto(url)
```

### Reuse Browser Instance

```python
# DON'T: Launch browser for each page
for url in urls:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # ...

# DO: Reuse browser, create new pages
with sync_playwright() as p:
    browser = p.chromium.launch()
    
    for url in urls:
        page = browser.new_page()
        page.goto(url)
        # Extract data
        page.close()  # Close page, not browser
    
    browser.close()
```

### Parallel Pages

```python
import asyncio
from playwright.async_api import async_playwright

async def scrape_page(browser, url):
    page = await browser.new_page()
    await page.goto(url)
    await page.wait_for_selector("div.content")
    content = await page.inner_text("div.content")
    await page.close()
    return content

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        urls = ["https://site.com/1", "https://site.com/2", "https://site.com/3"]
        tasks = [scrape_page(browser, url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        await browser.close()
        return results

results = asyncio.run(main())
```

---

## Common Challenges

### Challenge: Content Behind Click

```python
# Click to reveal content
page.click("button.show-details")
page.wait_for_selector("div.details")
details = page.inner_text("div.details")
```

### Challenge: Lazy-Loaded Images

```python
# Scroll to trigger lazy loading
page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
page.wait_for_timeout(1000)

# Or scroll to specific element
page.evaluate("document.querySelector('.last-item').scrollIntoView()")
```

### Challenge: Shadow DOM

```python
# Pierce shadow DOM
element = page.locator("custom-element").locator("internal:shadow=div.inside-shadow")
text = element.inner_text()

# Or evaluate JavaScript
text = page.evaluate("""
    document.querySelector('custom-element')
        .shadowRoot
        .querySelector('div.inside-shadow')
        .innerText
""")
```

### Challenge: iframes

```python
# Get iframe
iframe = page.frame_locator("iframe#content-frame")

# Interact with iframe content
iframe.locator("button.submit").click()
text = iframe.locator("div.result").inner_text()
```

---

## Decision Flowchart

```
Is content visible in View Source?
│
├── YES → Use static scraping (requests + BeautifulSoup)
│
└── NO → Is there a JSON API?
         │
         ├── YES → Call API directly (best option!)
         │
         └── NO → Use browser automation
                  │
                  ├── Need speed? → Playwright (recommended)
                  ├── Already know Selenium? → Selenium
                  └── Need Node.js? → Puppeteer
```

---

## Summary

| Approach | When to Use | Pros | Cons |
|----------|-------------|------|------|
| **Find API** | Always try first | Fast, clean data | Not always available |
| **Playwright** | JS-heavy sites | Modern, fast, reliable | Resource heavy |
| **Selenium** | Legacy projects | Mature, documented | Slower, flaky |
| **Hybrid** | Complex auth + data | Best of both | More complex |

### Key Takeaways

1. **Always look for the API first** - It's faster and gives cleaner data
2. **Playwright is the modern standard** - Use it for new projects
3. **Wait properly** - Most issues are timing-related
4. **Block unnecessary resources** - Speed up by blocking images/CSS
5. **Reuse browser instances** - Don't launch for each page

---

*Next: [06_rate_limiting_throttling.md](06_rate_limiting_throttling.md) - Controlling request speed*
