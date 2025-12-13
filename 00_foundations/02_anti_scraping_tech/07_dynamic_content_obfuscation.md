# Dynamic Content & Obfuscation

> **When Sites Deliberately Hide Data**

Beyond standard bot detection, some sites actively obfuscate their data to make scraping difficult. This document covers the techniques used and how to handle them.

---

## Why Sites Obfuscate

- **Protect proprietary data** - Prices, inventory, contact info
- **Prevent aggregation** - Stop comparison shopping sites
- **Reduce server load** - Make scraping uneconomical
- **Legal protection** - Create technical barriers to cite in lawsuits

---

## 1. CSS-Based Obfuscation

### Randomized Class Names

```html
<!-- Instead of: -->
<div class="price">$99.99</div>

<!-- They use: -->
<div class="a7x9f2k">$99.99</div>
```

**Solution:** Use structural selectors or text matching:

```python
# By position/structure
price = soup.select_one('div.product > div:nth-child(3)')

# By text pattern
import re
price_pattern = re.compile(r'\$[\d,.]+')
for div in soup.find_all('div'):
    if price_pattern.match(div.text.strip()):
        price = div.text.strip()
```

### CSS Content Injection

```html
<style>
.price::before { content: "$99"; }
.price::after { content: ".99"; }
</style>
<div class="price"></div>
<!-- Displays "$99.99" but HTML is empty -->
```

**Solution:** Use browser automation to get rendered text:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url)
    
    # Get computed/rendered text
    price = page.evaluate('''
        const el = document.querySelector('.price');
        window.getComputedStyle(el, '::before').content +
        window.getComputedStyle(el, '::after').content
    ''')
```

### Character Shuffling with CSS

```html
<style>
.c1 { order: 3; }
.c2 { order: 1; }
.c3 { order: 2; }
</style>
<div style="display:flex">
    <span class="c1">9</span>
    <span class="c2">$</span>
    <span class="c3">9</span>
</div>
<!-- HTML order: 9, $, 9 -->
<!-- Display order: $, 9, 9 = "$99" -->
```

**Solution:** Respect CSS order or get innerText:

```python
# Browser automation gets visual order
text = page.inner_text('.price-container')  # "$99"
```

### Font-Based Substitution

```css
@font-face {
    font-family: 'PriceFont';
    src: url('custom-font.woff2');
}
.price { font-family: 'PriceFont'; }
```

The custom font maps characters differently:
- HTML shows: `BCDE`
- Display shows: `$99.99`

**Solution:** Map the font or use OCR:

```python
# Option 1: Decode the font mapping
from fontTools.ttLib import TTFont

font = TTFont('custom-font.woff2')
cmap = font.getBestCmap()
# Reverse engineer the character mapping

# Option 2: Screenshot and OCR
page.screenshot(path='price.png', clip={'x': 100, 'y': 200, 'width': 50, 'height': 20})
import pytesseract
price = pytesseract.image_to_string('price.png')
```

---

## 2. JavaScript Obfuscation

### Dynamic Content Loading

```javascript
// Data loaded after page load
fetch('/api/prices')
    .then(r => r.json())
    .then(data => {
        document.querySelector('.price').textContent = data.price;
    });
```

**Solution:** Wait for content or intercept API:

```python
# Wait for content
page.wait_for_selector('.price:not(:empty)')

# Or intercept the API call
def handle_response(response):
    if '/api/prices' in response.url:
        print(response.json())

page.on('response', handle_response)
page.goto(url)
```

### Encoded Data in JavaScript

```javascript
// Data embedded in script tag
var _0x1234 = ['JDk5Ljk5'];  // Base64: "$99.99"
document.querySelector('.price').textContent = atob(_0x1234[0]);
```

**Solution:** Extract and decode:

```python
import re
import base64

# Find encoded strings
script = soup.find('script', string=re.compile(r'_0x\w+'))
encoded = re.findall(r"'([A-Za-z0-9+/=]+)'", script.string)

for enc in encoded:
    try:
        decoded = base64.b64decode(enc).decode('utf-8')
        print(f"Decoded: {decoded}")
    except:
        pass
```

### Obfuscated JavaScript

```javascript
// Original:
function getPrice() { return "$99.99"; }

// Obfuscated:
var _0xabc=["\x67\x65\x74\x50\x72\x69\x63\x65"];
function _0x123(){return "\x24\x39\x39\x2e\x39\x39";}
```

**Solution:** Use browser to execute and extract:

```python
# Let the browser handle it
page.goto(url)
price = page.evaluate('getPrice()')  # Browser executes JS
```

---

## 3. Data Fragmentation

### Split Across Elements

```html
<span class="d">$</span>
<span class="d">9</span>
<span class="d">9</span>
<span class="d">.</span>
<span class="d">9</span>
<span class="d">9</span>
```

**Solution:** Combine elements:

```python
# Gather all fragments
fragments = soup.select('.d')
price = ''.join(f.text for f in fragments)  # "$99.99"
```

### Interleaved Dummy Characters

```html
<span class="real">$</span>
<span class="fake">X</span>
<span class="real">9</span>
<span class="fake">Y</span>
<span class="real">9</span>
```

**Solution:** Filter by class or visibility:

```python
# By class
real = soup.select('.real')
price = ''.join(r.text for r in real)

# By visibility (in browser)
price = page.evaluate('''
    Array.from(document.querySelectorAll('.price span'))
        .filter(el => window.getComputedStyle(el).display !== 'none')
        .map(el => el.textContent)
        .join('')
''')
```

### Data in Attributes

```html
<div class="price" 
     data-int="99" 
     data-dec="99" 
     data-cur="USD">
</div>
```

**Solution:** Extract from attributes:

```python
div = soup.select_one('.price')
price = f"${div['data-int']}.{div['data-dec']}"
```

---

## 4. Image-Based Content

### Text as Images

```html
<img src="/prices/product123.png" alt="">
<!-- Image contains "$99.99" -->
```

**Solution:** OCR:

```python
import pytesseract
from PIL import Image
import requests
from io import BytesIO

# Download image
img_url = soup.select_one('.price img')['src']
response = requests.get(img_url)
img = Image.open(BytesIO(response.content))

# OCR
text = pytesseract.image_to_string(img)
print(text)  # "$99.99"
```

### Canvas Rendering

```javascript
const canvas = document.getElementById('priceCanvas');
const ctx = canvas.getContext('2d');
ctx.fillText('$99.99', 10, 50);
```

**Solution:** Screenshot and OCR:

```python
# Screenshot specific element
element = page.query_selector('#priceCanvas')
element.screenshot(path='canvas.png')

# OCR
import pytesseract
text = pytesseract.image_to_string('canvas.png')
```

### SVG Text

```html
<svg viewBox="0 0 100 20">
    <text x="0" y="15">$99.99</text>
</svg>
```

**Solution:** Parse SVG:

```python
svg = soup.select_one('svg')
text = svg.select_one('text').text  # "$99.99"
```

---

## 5. API Obfuscation

### Encrypted API Responses

```json
{
    "data": "U2FsdGVkX1+abc123encrypted..."
}
```

**Solution:** Find decryption logic in JavaScript:

```python
# Search for crypto libraries/patterns
scripts = soup.find_all('script')
for script in scripts:
    if script.string and 'decrypt' in script.string.lower():
        # Analyze the decryption method
        pass

# Or use browser to decrypt
decrypted = page.evaluate('''
    // Call their decryption function
    window.decrypt(encryptedData)
''')
```

### Signed Requests

```javascript
// Request requires signature
fetch('/api/data', {
    headers: {
        'X-Signature': generateSignature(timestamp, nonce),
        'X-Timestamp': timestamp,
        'X-Nonce': nonce
    }
});
```

**Solution:** Reverse engineer signature or use browser:

```python
# Option 1: Capture in browser
page.on('request', lambda req: print(req.headers))
page.goto(url)

# Option 2: Reverse engineer
# Analyze generateSignature function and replicate
```

### GraphQL with Persisted Queries

```javascript
// Instead of sending query, send hash
fetch('/graphql', {
    body: JSON.stringify({
        extensions: {
            persistedQuery: {
                sha256Hash: "abc123...",
                version: 1
            }
        },
        variables: { id: "123" }
    })
});
```

**Solution:** Find the query mapping or replay requests:

```python
# Capture the original query via browser
# Then use the hash in subsequent requests
```

---

## 6. Anti-Pattern Detection

### Request Pattern Analysis

Sites may block if:
- Sequential page access (page 1, 2, 3, 4...)
- Alphabetical access (a.html, b.html, c.html...)
- Predictable timing

**Solution:** Randomize:

```python
import random

urls = list(urls)
random.shuffle(urls)  # Random order

for url in urls:
    delay = random.uniform(2, 10)  # Random delay
    time.sleep(delay)
    scrape(url)
```

### Behavioral Triggers

```javascript
// Track if user interacts before accessing "protected" content
let hasInteracted = false;
document.addEventListener('mousemove', () => hasInteracted = true);

// Show content only if interacted
if (hasInteracted) {
    showPrices();
}
```

**Solution:** Simulate interaction:

```python
# Move mouse before scraping
page.mouse.move(100, 100)
page.mouse.move(200, 300)
page.wait_for_timeout(1000)
# Now scrape
```

---

## 7. Defeating Obfuscation Patterns

### General Strategy

```python
def scrape_obfuscated_site(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # 1. Load page fully
        page.goto(url)
        page.wait_for_load_state('networkidle')
        
        # 2. Trigger interactions if needed
        page.mouse.move(100, 100)
        page.evaluate('window.scrollTo(0, 500)')
        
        # 3. Wait for dynamic content
        page.wait_for_timeout(2000)
        
        # 4. Get rendered text (not HTML)
        data = page.evaluate('''
            () => {
                const priceEl = document.querySelector('.price');
                return {
                    // Get computed/visible text
                    price: priceEl?.innerText || 
                           window.getComputedStyle(priceEl).content,
                    
                    // Get data from attributes
                    attrs: {
                        int: priceEl?.dataset?.int,
                        dec: priceEl?.dataset?.dec,
                    }
                };
            }
        ''')
        
        browser.close()
        return data
```

### OCR as Fallback

```python
def ocr_fallback(page, selector):
    """Screenshot element and OCR if text extraction fails."""
    
    element = page.query_selector(selector)
    
    # Try normal text extraction first
    text = element.inner_text().strip()
    if text and is_valid_price(text):
        return text
    
    # Fallback to OCR
    screenshot = element.screenshot()
    
    import pytesseract
    from PIL import Image
    from io import BytesIO
    
    img = Image.open(BytesIO(screenshot))
    text = pytesseract.image_to_string(img)
    
    return text.strip()
```

---

## 8. Site-Specific Patterns

### E-commerce Price Obfuscation

```python
def extract_ecommerce_price(page):
    """Handle common e-commerce obfuscation."""
    
    strategies = [
        # Strategy 1: Direct text
        lambda: page.inner_text('.price'),
        
        # Strategy 2: Data attributes
        lambda: f"${page.get_attribute('.price', 'data-price')}",
        
        # Strategy 3: JSON in script
        lambda: extract_json_price(page),
        
        # Strategy 4: Computed style
        lambda: page.evaluate('''
            getComputedStyle(document.querySelector('.price'), '::before').content
        '''),
        
        # Strategy 5: OCR fallback
        lambda: ocr_fallback(page, '.price'),
    ]
    
    for strategy in strategies:
        try:
            result = strategy()
            if result and '$' in str(result):
                return result
        except:
            continue
    
    return None
```

### Contact Info Obfuscation

```python
def extract_email(page):
    """Handle email obfuscation."""
    
    # Check for cloudflare email protection
    protected = page.query_selector('[data-cfemail]')
    if protected:
        encoded = protected.get_attribute('data-cfemail')
        return decode_cf_email(encoded)
    
    # Check for JavaScript-assembled email
    email = page.evaluate('''
        () => {
            // Find mailto links
            const mailto = document.querySelector('a[href^="mailto:"]');
            if (mailto) return mailto.href.replace('mailto:', '');
            
            // Find email in onclick handlers
            const onclick = document.querySelector('[onclick*="@"]');
            if (onclick) {
                const match = onclick.getAttribute('onclick').match(/[\\w.]+@[\\w.]+/);
                return match ? match[0] : null;
            }
            
            return null;
        }
    ''')
    
    return email

def decode_cf_email(encoded):
    """Decode Cloudflare email protection."""
    r = int(encoded[:2], 16)
    email = ''.join(
        chr(int(encoded[i:i+2], 16) ^ r)
        for i in range(2, len(encoded), 2)
    )
    return email
```

---

## Summary

| Obfuscation Type | Detection | Solution |
|------------------|-----------|----------|
| **Random classes** | Changing class names | Structural selectors |
| **CSS content** | Empty elements with ::before/after | Computed styles |
| **Character shuffle** | Flexbox reordering | Get innerText |
| **Custom fonts** | Font substitution | Font analysis or OCR |
| **JS loading** | Empty initial HTML | Wait for content |
| **Encoded data** | Base64/hex in scripts | Decode or execute |
| **Fragmentation** | Split across elements | Combine fragments |
| **Images** | No text in HTML | OCR |
| **Canvas** | No accessible text | Screenshot + OCR |

### Key Takeaways

1. **Browser > Requests** - Rendered content bypasses most obfuscation
2. **innerText > innerHTML** - Get visual text, not HTML
3. **Intercept APIs** - Often cleaner than parsing obfuscated HTML
4. **OCR as backup** - When all else fails
5. **Analyze patterns** - Each site has consistent obfuscation
6. **Update regularly** - Obfuscation changes over time

---

*This completes the Anti-Scraping Tech section. Next: [../03_legal_ethical/](../03_legal_ethical/) - Legal and ethical considerations*
