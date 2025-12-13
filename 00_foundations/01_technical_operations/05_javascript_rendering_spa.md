# JavaScript Rendering & Single Page Applications

> **When Static Scraping Isn't Enough**

Modern web applications rely heavily on JavaScript to render content. This document explains when you need browser automation, how it works, and strategies for efficient JS-heavy scraping.

---

## The Problem

### Static HTML (Easy)

```
Server sends:         You see:
<h1>Products</h1>     <h1>Products</h1>
<div>Item 1</div>     <div>Item 1</div>
<div>Item 2</div>     <div>Item 2</div>
```

### JavaScript-Rendered (Harder)

```
Server sends:           After JS runs:
<div id="app"></div>    <div id="app">
<script src="app.js">     <h1>Products</h1>
</script>                  <div>Item 1</div>
                          <div>Item 2</div>
                        </div>
```

**With static scraping, you only get the empty `<div id="app">`.**

---

## Detecting JavaScript-Rendered Content

### Method 1: View Source vs. Inspect

1. **View Page Source** (Ctrl+U): Shows raw HTML from server
2. **Inspect Element** (F12): Shows HTML after JavaScript runs

If they're different, JavaScript is rendering content.

### Method 2: Disable JavaScript

1. Open DevTools → Settings → Disable JavaScript
2. Reload the page
3. If content disappears, it's JavaScript-rendered

### Method 3: Compare Static vs. Browser Response

```python
import requests
from playwright.sync_api import sync_playwright

url = "https://example.com"

# Static request
static_html = requests.get(url).text

# Browser-rendered
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url)
    rendered_html = page.content()

# Compare lengths
print(f"Static: {len(static_html)} chars")
print(f"Rendered: {len(rendered_html)} chars")

# If rendered is significantly larger, JS is adding content
```

---

## Understanding SPAs

### Single Page Application Architecture

```
Traditional Site:
Page 1 ─── /page1.html ─── Full HTML
Page 2 ─── /page2.html ─── Full HTML
Page 3 ─── /page3.html ─── Full HTML

SPA:
All Pages ─── /index.html ─── JavaScript Shell
         └── JS fetches data ─── JSON API
         └── JS renders content ─── Updates DOM
```

### Common SPA Frameworks

| Framework | Detection Signs |
|-----------|----------------|
| **React** | `<div id="root">`, `__NEXT_DATA__`, `data-reactroot` |
| **Vue** | `<div id="app">`, `data-v-*` attributes |
| **Angular** | `<app-root>`, `ng-*` attributes |
| **Next.js** | `__NEXT_DATA__` script tag |
| **Nuxt** | `__NUXT__` variable |

### Finding Data in SPAs

Often, the data is embedded in the page:

```python
from bs4 import BeautifulSoup
import json

html = requests.get(url).text
soup = BeautifulSoup(html, "html.parser")

# Next.js embeds data in a script tag
next_data = soup.select_one("#__NEXT_DATA__")
if next_data:
    data = json.loads(next_data.string)
    # Data is here without running JavaScript!

# Some sites embed data in window objects
import re
match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html)
if match:
    data = json.loads(match.group(1))
```

---

## Browser Automation Options

### Playwright (Recommended)

Modern, fast, multi-browser support.

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # Launch browser
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Navigate
    page.goto("https://example.com")
    
    # Wait for content
    page.wait_for_selector("div.products")
    
    # Extract
    products = page.query_selector_all("div.product")
    for product in products:
        name = product.query_selector("h2").inner_text()
        price = product.query_selector(".price").inner_text()
        print(f"{name}: {price}")
    
    browser.close()
```

### Puppeteer (Node.js)

Chrome-focused, mature ecosystem.

```javascript
const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({headless: true});
    const page = await browser.newPage();
    
    await page.goto('https://example.com');
    await page.waitForSelector('div.products');
    
    const products = await page.$$eval('div.product', elements =>
        elements.map(el => ({
            name: el.querySelector('h2').innerText,
            price: el.querySelector('.price').innerText
        }))
    );
    
    console.log(products);
    await browser.close();
})();
```

### Selenium

Older but widely supported.

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("https://example.com")

# Wait for content
wait = WebDriverWait(driver, 10)
products = wait.until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.product"))
)

for product in products:
    name = product.find_element(By.CSS_SELECTOR, "h2").text
    price = product.find_element(By.CSS_SELECTOR, ".price").text
    print(f"{name}: {price}")

driver.quit()
```

### Comparison

| Feature | Playwright | Puppeteer | Selenium |
|---------|------------|-----------|----------|
| **Speed** | Fast | Fast | Slower |
| **Browsers** | Chrome, Firefox, WebKit | Chrome | All major |
| **Language** | Python, JS, .NET, Java | JavaScript | Many |
| **Auto-wait** | Built-in | Manual | Manual |
| **Async** | Yes | Yes | Limited |
| **Setup** | Easy | Easy | More complex |

---

## Waiting Strategies

### The Problem

JavaScript loads content asynchronously. You need to wait for it.

```python
# ❌ This won't work - content not loaded yet
page.goto("https://example.com")
products = page.query_selector_all("div.product")  # Empty!

# ✅ Wait for content to appear
page.goto("https://example.com")
page.wait_for_selector("div.product")
products = page.query_selector_all("div.product")  # Has data!
```

### Wait Methods

#### Wait for Selector

```python
# Wait for element to exist
page.wait_for_selector("div.products")

# Wait for element to be visible
page.wait_for_selector("div.products", state="visible")

# Wait for element to be hidden
page.wait_for_selector("div.loading", state="hidden")
```

#### Wait for Load State

```python
# Wait for network to be idle
page.goto(url, wait_until="networkidle")

# Wait for DOM content loaded
page.goto(url, wait_until="domcontentloaded")

# Wait for full load
page.goto(url, wait_until="load")
```

#### Wait for Function

```python
# Wait for custom condition
page.wait_for_function("window.dataLoaded === true")

# Wait for array to have items
page.wait_for_function("document.querySelectorAll('.product').length > 0")
```

#### Fixed Timeout (Last Resort)

```python
import time

# ❌ Avoid if possible - unreliable
time.sleep(5)

# ✅ Better: wait for specific condition with timeout
page.wait_for_selector("div.products", timeout=10000)
```

---

## Handling Dynamic Content

### Infinite Scroll

```python
def scrape_infinite_scroll(page, item_selector, max_items=100):
    items = []
    
    while len(items) < max_items:
        # Get current items
        current_items = page.query_selector_all(item_selector)
        new_count = len(current_items)
        
        if new_count == len(items):
            # No new items loaded, we're done
            break
        
        items = current_items
        
        # Scroll to bottom
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        
        # Wait for new content
        page.wait_for_timeout(1000)
    
    return items

# Usage
page.goto("https://example.com/feed")
items = scrape_infinite_scroll(page, "div.post", max_items=200)
```

### Load More Button

```python
def click_load_more(page, button_selector, item_selector, max_clicks=10):
    clicks = 0
    
    while clicks < max_clicks:
        # Try to find and click the button
        button = page.query_selector(button_selector)
        
        if not button or not button.is_visible():
            break
        
        # Get current count
        before_count = len(page.query_selector_all(item_selector))
        
        # Click load more
        button.click()
        
        # Wait for new items
        page.wait_for_function(
            f"document.querySelectorAll('{item_selector}').length > {before_count}",
            timeout=5000
        )
        
        clicks += 1
    
    return page.query_selector_all(item_selector)
```

### Lazy Loading Images

```python
# Scroll through page to trigger lazy loading
def trigger_lazy_load(page):
    # Get page height
    height = page.evaluate("document.body.scrollHeight")
    
    # Scroll in increments
    position = 0
    while position < height:
        page.evaluate(f"window.scrollTo(0, {position})")
        page.wait_for_timeout(200)
        position += 500
        
        # Update height (page might have grown)
        height = page.evaluate("document.body.scrollHeight")
```

---

## Performance Optimization

### Block Unnecessary Resources

```python
def block_resources(route):
    """Block images, fonts, stylesheets for faster loading."""
    if route.request.resource_type in ["image", "font", "stylesheet"]:
        route.abort()
    else:
        route.continue_()

page.route("**/*", block_resources)
page.goto("https://example.com")  # Much faster!
```

### More Aggressive Blocking

```python
BLOCKED_RESOURCES = [
    "image", "font", "stylesheet", "media", 
    "texttrack", "object", "beacon", "csp_report", "imageset"
]

BLOCKED_URLS = [
    "google-analytics.com",
    "googletagmanager.com",
    "facebook.com",
    "doubleclick.net",
    "hotjar.com",
]

def should_block(route):
    # Block by resource type
    if route.request.resource_type in BLOCKED_RESOURCES:
        return True
    
    # Block by URL pattern
    url = route.request.url
    for blocked in BLOCKED_URLS:
        if blocked in url:
            return True
    
    return False

def handle_route(route):
    if should_block(route):
        route.abort()
    else:
        route.continue_()

page.route("**/*", handle_route)
```

### Reuse Browser Instances

```python
# ❌ Slow: New browser for each page
for url in urls:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        # ...

# ✅ Fast: Reuse browser, new pages
with sync_playwright() as p:
    browser = p.chromium.launch()
    
    for url in urls:
        page = browser.new_page()
        page.goto(url)
        # ... extract data ...
        page.close()  # Close page, keep browser
    
    browser.close()
```

### Browser Context for Isolation

```python
with sync_playwright() as p:
    browser = p.chromium.launch()
    
    # Create isolated context (fresh cookies, storage)
    context = browser.new_context()
    
    # Pages in same context share cookies
    page1 = context.new_page()
    page2 = context.new_page()
    
    # New context = fresh state
    context2 = browser.new_context()
```

---

## Intercepting Network Requests

### Capture API Responses

```python
api_data = []

def capture_api(response):
    if "/api/products" in response.url:
        api_data.append(response.json())

page.on("response", capture_api)
page.goto("https://example.com/products")

# Now api_data contains the JSON responses
print(api_data)
```

### Mock API Responses

```python
def mock_api(route):
    if "/api/products" in route.request.url:
        # Return custom data
        route.fulfill(
            status=200,
            content_type="application/json",
            body='[{"name": "Test Product", "price": 99.99}]'
        )
    else:
        route.continue_()

page.route("**/api/**", mock_api)
```

### Extract Data from XHR

```python
# Often faster: intercept the API call instead of parsing HTML
products = []

def handle_response(response):
    if "api.example.com/products" in response.url:
        data = response.json()
        products.extend(data["items"])

page.on("response", handle_response)
page.goto("https://example.com")
page.wait_for_load_state("networkidle")

# Products extracted directly from API, no HTML parsing needed
print(products)
```

---

## When to Use What

### Decision Tree

```
Is content in initial HTML?
├── Yes → Use static scraping (requests + BeautifulSoup)
└── No → Is data in embedded JSON?
    ├── Yes → Extract JSON from HTML (still static)
    └── No → Is there a hidden API?
        ├── Yes → Call API directly (static)
        └── No → Use browser automation
```

### Hybrid Approach

Use browser once to discover API, then use static requests:

```python
# Step 1: Use browser to find API endpoint
api_urls = []

def capture_apis(response):
    if response.request.resource_type == "xhr":
        api_urls.append(response.url)

page.on("response", capture_apis)
page.goto("https://example.com")
page.wait_for_load_state("networkidle")

print("Discovered APIs:", api_urls)

# Step 2: Call API directly (much faster)
for api_url in api_urls:
    if "products" in api_url:
        data = requests.get(api_url, headers=browser_headers).json()
        # Process without browser!
```

---

## Summary

| Scenario | Solution |
|----------|----------|
| **Static HTML** | `requests` + `BeautifulSoup` |
| **Data in `__NEXT_DATA__`** | Extract JSON from HTML |
| **Hidden API discovered** | Direct API calls |
| **Must render JavaScript** | Playwright/Puppeteer |
| **Infinite scroll** | Browser + scroll automation |
| **Complex interactions** | Full browser automation |

### Key Principles

1. **Try static first** - It's always faster
2. **Look for embedded data** - Check `__NEXT_DATA__`, `window.__INITIAL_STATE__`
3. **Find hidden APIs** - Use DevTools Network tab
4. **Block unnecessary resources** - Speed up browser automation
5. **Intercept, don't parse** - Get data from API responses directly
6. **Reuse browser instances** - Don't restart for each page

---

*Next: [06_rate_limiting_throttling.md](06_rate_limiting_throttling.md) - Controlling request speed*
