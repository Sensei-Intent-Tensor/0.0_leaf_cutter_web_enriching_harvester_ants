# Browser Automation Compared

> **Playwright vs Selenium vs Puppeteer**

When you need to render JavaScript or interact with pages, you need browser automation. This document compares the major options.

---

## Overview Comparison

| Feature | Playwright | Selenium | Puppeteer |
|---------|------------|----------|-----------|
| **Languages** | Python, JS, .NET, Java | All major | JavaScript only |
| **Browsers** | Chromium, Firefox, WebKit | All major | Chromium (+ Firefox) |
| **Speed** | Fast | Slower | Fast |
| **Modern API** | Yes | Legacy feel | Yes |
| **Auto-wait** | Yes | Manual | Partial |
| **Network intercept** | Yes | Limited | Yes |
| **Headless** | Yes | Yes | Yes |
| **Stealth** | Good with plugins | Poor | Good with plugins |

---

## Playwright

### Why Playwright

- Modern async-first design
- Cross-browser (Chromium, Firefox, WebKit)
- Auto-wait for elements
- Network interception built-in
- Excellent debugging tools
- Active development

### Installation

```bash
pip install playwright
playwright install  # Downloads browsers
```

### Basic Usage

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    page.goto('https://example.com')
    page.wait_for_selector('.product')
    
    title = page.inner_text('h1')
    print(title)
    
    browser.close()
```

### Key Features

```python
# Auto-wait (no manual waits needed)
page.click('button')  # Waits automatically until button is clickable

# Network interception
def handle_route(route):
    if route.request.resource_type == 'image':
        route.abort()  # Block images
    else:
        route.continue_()

page.route('**/*', handle_route)

# Multiple browsers
for browser_type in [p.chromium, p.firefox, p.webkit]:
    browser = browser_type.launch()
    # Test across browsers

# Screenshots and PDFs
page.screenshot(path='screenshot.png', full_page=True)
page.pdf(path='page.pdf')

# Contexts (isolated sessions)
context = browser.new_context(
    viewport={'width': 1920, 'height': 1080},
    user_agent='Custom UA'
)
page = context.new_page()
```

### Async Usage

```python
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://example.com')
        content = await page.content()
        await browser.close()
        return content

result = asyncio.run(main())
```

---

## Selenium

### Why Selenium

- Longest history, most documentation
- Supports all browsers
- Large ecosystem
- Industry standard for testing
- Works with grid for distributed testing

### Installation

```bash
pip install selenium webdriver-manager
```

### Basic Usage

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Setup driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

try:
    driver.get('https://example.com')
    
    # Explicit wait
    wait = WebDriverWait(driver, 10)
    element = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.product'))
    )
    
    title = driver.find_element(By.TAG_NAME, 'h1').text
    print(title)
    
finally:
    driver.quit()
```

### Key Features

```python
# Headless mode
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

# Find elements
elements = driver.find_elements(By.CSS_SELECTOR, '.product')
element = driver.find_element(By.XPATH, '//div[@class="price"]')
element = driver.find_element(By.ID, 'main-content')

# Interactions
element.click()
element.send_keys('text to type')
element.clear()

# Execute JavaScript
result = driver.execute_script('return document.title')
driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')

# Cookies
cookies = driver.get_cookies()
driver.add_cookie({'name': 'key', 'value': 'value'})
```

### Wait Strategies

```python
from selenium.webdriver.support import expected_conditions as EC

# Wait for element present
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'myElement'))
)

# Wait for element clickable
element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button'))
)

# Wait for text
element = WebDriverWait(driver, 10).until(
    EC.text_to_be_present_in_element((By.ID, 'status'), 'Complete')
)

# Custom condition
def custom_condition(driver):
    return len(driver.find_elements(By.CSS_SELECTOR, '.item')) > 5

WebDriverWait(driver, 10).until(custom_condition)
```

---

## Puppeteer

### Why Puppeteer

- Chrome/Chromium focused
- Developed by Chrome DevTools team
- Excellent performance
- Good for Chrome-specific features
- Node.js native

### Installation

```bash
npm install puppeteer
```

### Basic Usage (JavaScript)

```javascript
const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({headless: true});
    const page = await browser.newPage();
    
    await page.goto('https://example.com');
    await page.waitForSelector('.product');
    
    const title = await page.$eval('h1', el => el.textContent);
    console.log(title);
    
    await browser.close();
})();
```

### Puppeteer in Python (pyppeteer)

```python
import asyncio
from pyppeteer import launch

async def main():
    browser = await launch(headless=True)
    page = await browser.newPage()
    
    await page.goto('https://example.com')
    await page.waitForSelector('.product')
    
    title = await page.evaluate('document.querySelector("h1").textContent')
    print(title)
    
    await browser.close()

asyncio.run(main())
```

---

## Head-to-Head Comparison

### Syntax Comparison

**Wait for element and click:**

```python
# Playwright
page.click('button.submit')  # Auto-waits

# Selenium
wait = WebDriverWait(driver, 10)
button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.submit')))
button.click()

# Puppeteer (JS)
await page.waitForSelector('button.submit');
await page.click('button.submit');
```

**Extract text from multiple elements:**

```python
# Playwright
texts = page.locator('.item').all_inner_texts()

# Selenium
elements = driver.find_elements(By.CSS_SELECTOR, '.item')
texts = [el.text for el in elements]

# Puppeteer (JS)
const texts = await page.$$eval('.item', els => els.map(el => el.textContent));
```

**Network interception:**

```python
# Playwright
def block_images(route):
    if route.request.resource_type == 'image':
        route.abort()
    else:
        route.continue_()
page.route('**/*', block_images)

# Selenium - Not natively supported, need proxy or extension

# Puppeteer (JS)
await page.setRequestInterception(true);
page.on('request', request => {
    if (request.resourceType() === 'image') {
        request.abort();
    } else {
        request.continue();
    }
});
```

### Performance

| Metric | Playwright | Selenium | Puppeteer |
|--------|------------|----------|-----------|
| Launch time | Fast | Slow | Fast |
| Page load | Fast | Medium | Fast |
| Element finding | Fast | Medium | Fast |
| Memory usage | Medium | High | Medium |
| Parallel sessions | Excellent | Good | Excellent |

### Bot Detection

| Aspect | Playwright | Selenium | Puppeteer |
|--------|------------|----------|-----------|
| Detectable by default | Medium | High | Medium |
| navigator.webdriver | Can patch | Visible | Can patch |
| With stealth plugin | Good | Poor | Good |
| Best stealth | playwright-stealth | undetected-chromedriver | puppeteer-stealth |

---

## When to Use What

### Choose Playwright When:

- ✅ Starting a new project
- ✅ Need cross-browser support
- ✅ Want modern async API
- ✅ Need network interception
- ✅ Want best debugging experience
- ✅ Using Python, JavaScript, or .NET

### Choose Selenium When:

- ✅ Need a specific browser (Safari, Opera)
- ✅ Have existing Selenium infrastructure
- ✅ Need Selenium Grid for distribution
- ✅ Want maximum community resources
- ✅ Team already knows Selenium

### Choose Puppeteer When:

- ✅ JavaScript/Node.js only project
- ✅ Chrome-specific features needed
- ✅ Want Google's direct support
- ✅ Building Chrome extensions

---

## Stealth Configuration

### Playwright with Stealth

```python
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0...'
    )
    page = context.new_page()
    stealth_sync(page)
    page.goto('https://example.com')
```

### Selenium with undetected-chromedriver

```python
import undetected_chromedriver as uc

driver = uc.Chrome(headless=True, version_main=120)
driver.get('https://example.com')
```

### Puppeteer with Stealth

```javascript
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

puppeteer.use(StealthPlugin());

const browser = await puppeteer.launch({headless: true});
```

---

## Summary

| Decision Factor | Recommendation |
|-----------------|----------------|
| **New Python project** | Playwright |
| **New JS project** | Playwright or Puppeteer |
| **Existing Selenium** | Keep Selenium |
| **Cross-browser needed** | Playwright or Selenium |
| **Maximum stealth** | undetected-chromedriver (Selenium) |
| **Network manipulation** | Playwright or Puppeteer |
| **Simplest API** | Playwright |

---

*Next: [03_parsing_libraries_guide.md](03_parsing_libraries_guide.md) - BeautifulSoup, lxml, and more*
