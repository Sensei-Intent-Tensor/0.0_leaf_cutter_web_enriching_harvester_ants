# Dynamic Content & Obfuscation

> **When Sites Fight Back With Code**

Beyond authentication and bot detection, some sites actively make their content difficult to extract through technical obfuscation. This document covers these anti-scraping code techniques.

---

## Why Sites Obfuscate

```
Goal: Make scraping expensive/difficult while keeping human experience smooth

Methods:
├── Hide data in complex structures
├── Load content dynamically
├── Change element identifiers
├── Encrypt or encode content
└── Require computation to decode
```

---

## 1. Dynamic Class Names

### The Problem

Class names that change on every build or request:

```html
<!-- Monday -->
<div class="product-card_a7x9z">
    <span class="price_b2y8w">$99.99</span>
</div>

<!-- Tuesday (after deploy) -->
<div class="product-card_k3m2n">
    <span class="price_j5p9q">$99.99</span>
</div>
```

Your selector `div.product-card_a7x9z` breaks instantly.

### Solutions

#### Use Structural Selectors

```python
# BAD: Relies on class name
soup.select('div.product-card_a7x9z')

# GOOD: Use structure and attributes
soup.select('div[class*="product-card"]')  # Contains
soup.select('div[class^="product-card"]')  # Starts with

# BETTER: Use data attributes (usually stable)
soup.select('div[data-testid="product-card"]')
soup.select('[data-product-id]')

# BEST: Use hierarchical structure
soup.select('article > div:first-child > span')
```

#### Find Patterns in Random Names

```python
import re

def find_element_by_class_pattern(soup, pattern):
    """Find elements where class matches pattern."""
    regex = re.compile(pattern)
    return soup.find_all(class_=regex)

# Usage
products = find_element_by_class_pattern(soup, r'product-card_[a-z0-9]+')
prices = find_element_by_class_pattern(soup, r'price_[a-z0-9]+')
```

#### Use Text Content

```python
# Find by text content instead of class
price_element = soup.find(string=re.compile(r'\$\d+\.\d{2}'))
if price_element:
    price = price_element.parent
```

---

## 2. CSS Content Injection

### The Problem

Content rendered via CSS `::before` or `::after`:

```html
<span class="price" data-value="99.99"></span>

<style>
.price::before {
    content: "$" attr(data-value);
}
</style>
```

Scraping the HTML gives you an empty `<span>`.

### Solutions

#### Extract from Data Attributes

```python
# Get the data attribute
price_elem = soup.select_one('.price')
price = price_elem.get('data-value')  # "99.99"
```

#### Use Browser Automation

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url)
    
    # Get computed text (includes CSS content)
    price = page.evaluate('''
        window.getComputedStyle(
            document.querySelector('.price'), 
            '::before'
        ).content
    ''')
    
    # Or just get visible text
    visible_price = page.inner_text('.price')
```

---

## 3. Font-Based Obfuscation

### The Problem

Custom fonts that map different characters:

```
In the font file:
'A' displays as '7'
'B' displays as '3'
'C' displays as '9'

HTML: <span class="price">ABC</span>
User sees: 739
Scraper sees: ABC
```

### Detection

```python
def detect_custom_font_obfuscation(soup):
    """Check for custom font usage on price elements."""
    
    # Look for custom font-face declarations
    styles = soup.find_all('style')
    for style in styles:
        if '@font-face' in style.text:
            if any(x in style.text.lower() for x in ['price', 'number', 'digit']):
                return True
    
    # Look for inline font styles
    elements = soup.find_all(style=re.compile(r'font-family.*[\'"][^\'"]+[\'"]'))
    return len(elements) > 0
```

### Solutions

#### Map the Font

```python
# Download and analyze the font file
from fontTools.ttLib import TTFont

def get_font_mapping(font_url):
    """Extract character mapping from custom font."""
    
    # Download font
    response = requests.get(font_url)
    font = TTFont(io.BytesIO(response.content))
    
    # Get cmap (character map)
    cmap = font.getBestCmap()
    
    # Build mapping
    mapping = {}
    for code, glyph_name in cmap.items():
        # Analyze glyph shapes to determine actual character
        # This is complex and font-specific
        pass
    
    return mapping
```

#### Use OCR

```python
from playwright.sync_api import sync_playwright
import pytesseract
from PIL import Image
import io

def extract_with_ocr(page, selector):
    """Screenshot element and OCR it."""
    
    element = page.query_selector(selector)
    screenshot = element.screenshot()
    
    image = Image.open(io.BytesIO(screenshot))
    text = pytesseract.image_to_string(image)
    
    return text.strip()
```

#### Browser Computed Text

```python
# Sometimes browser returns the visual text
page.goto(url)
price = page.inner_text('.price')  # May show actual number
```

---

## 4. Canvas-Rendered Content

### The Problem

Content drawn on HTML canvas, not in DOM:

```html
<canvas id="price-display" width="100" height="30"></canvas>

<script>
const ctx = document.getElementById('price-display').getContext('2d');
ctx.fillText('$99.99', 10, 20);
</script>
```

No text in HTML to scrape.

### Solutions

#### OCR the Canvas

```python
def extract_canvas_text(page, canvas_selector):
    """Extract text from canvas using OCR."""
    
    # Screenshot just the canvas
    canvas = page.query_selector(canvas_selector)
    screenshot = canvas.screenshot()
    
    # OCR
    image = Image.open(io.BytesIO(screenshot))
    text = pytesseract.image_to_string(image)
    
    return text
```

#### Intercept Canvas Drawing

```python
# Inject script to intercept fillText calls
page.add_init_script('''
    window.__canvasText = [];
    const originalFillText = CanvasRenderingContext2D.prototype.fillText;
    CanvasRenderingContext2D.prototype.fillText = function(text, x, y) {
        window.__canvasText.push({text, x, y});
        return originalFillText.apply(this, arguments);
    };
''')

page.goto(url)
page.wait_for_timeout(2000)

# Get intercepted text
canvas_text = page.evaluate('window.__canvasText')
```

---

## 5. Infinite Scroll Pagination

### The Problem

No page numbers, content loads as you scroll:

```
Page Load: Items 1-20
Scroll Down: Items 21-40 load
Scroll More: Items 41-60 load
...continues...
```

### Solutions

#### Scroll and Collect

```python
def scrape_infinite_scroll(page, item_selector, max_items=1000):
    """Scroll through infinite content."""
    
    items = []
    last_height = 0
    
    while len(items) < max_items:
        # Get current items
        new_items = page.query_selector_all(item_selector)
        items = list(set(items + new_items))  # Dedupe
        
        # Scroll to bottom
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        page.wait_for_timeout(2000)
        
        # Check if we've reached the end
        new_height = page.evaluate('document.body.scrollHeight')
        if new_height == last_height:
            break
        last_height = new_height
    
    return items[:max_items]
```

#### Find the API

```python
# Intercept XHR requests to find pagination API
api_calls = []

def handle_request(request):
    if 'api' in request.url and 'page' in request.url:
        api_calls.append(request.url)

page.on('request', handle_request)
page.goto(url)
page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
page.wait_for_timeout(2000)

# Now call API directly
for api_url in api_calls:
    response = requests.get(api_url)
    data = response.json()
```

---

## 6. WebSocket Data Loading

### The Problem

Data loaded via WebSocket, not HTTP:

```javascript
const ws = new WebSocket('wss://site.com/data');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updatePrices(data);
};
```

### Solutions

#### Intercept WebSocket Messages

```python
from playwright.sync_api import sync_playwright

websocket_messages = []

def handle_ws_message(ws, message):
    websocket_messages.append(message)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    
    # Listen for WebSocket
    page.on('websocket', lambda ws: ws.on('framereceived', 
            lambda payload: websocket_messages.append(payload)))
    
    page.goto(url)
    page.wait_for_timeout(5000)
    
    # Process messages
    for msg in websocket_messages:
        data = json.loads(msg)
```

---

## 7. GraphQL with Dynamic Queries

### The Problem

Complex GraphQL that requires specific query structures:

```javascript
const query = gql`
    query GetProducts($cursor: String, $filters: FilterInput!) {
        products(after: $cursor, filters: $filters) {
            edges {
                node {
                    id
                    name
                    price
                }
            }
            pageInfo {
                hasNextPage
                endCursor
            }
        }
    }
`;
```

### Solutions

#### Capture and Replay

```python
# Intercept GraphQL requests
graphql_queries = []

def handle_request(request):
    if 'graphql' in request.url:
        graphql_queries.append({
            'url': request.url,
            'body': request.post_data
        })

page.on('request', handle_request)
page.goto(url)
# ... interact with page

# Replay queries
for query in graphql_queries:
    response = requests.post(
        query['url'],
        json=json.loads(query['body']),
        headers={'Content-Type': 'application/json'}
    )
```

---

## 8. JavaScript-Only Data

### The Problem

Data embedded in JavaScript, not HTML:

```html
<script>
window.__INITIAL_STATE__ = {
    products: [
        {id: 1, name: "Widget", price: 99.99},
        {id: 2, name: "Gadget", price: 149.99}
    ]
};
</script>

<div id="app"></div>
```

### Solutions

#### Extract from Script Tags

```python
import json
import re

def extract_json_from_script(html, variable_name):
    """Extract JSON data from JavaScript variable."""
    
    # Pattern for window.VAR = {...}
    pattern = rf'{variable_name}\s*=\s*(\{{.*?\}});'
    match = re.search(pattern, html, re.DOTALL)
    
    if match:
        json_str = match.group(1)
        return json.loads(json_str)
    
    return None

# Usage
soup = BeautifulSoup(html, 'html.parser')
scripts = soup.find_all('script')

for script in scripts:
    if script.string and '__INITIAL_STATE__' in script.string:
        data = extract_json_from_script(script.string, '__INITIAL_STATE__')
        products = data['products']
```

#### Evaluate in Browser

```python
page.goto(url)
data = page.evaluate('window.__INITIAL_STATE__')
products = data['products']
```

---

## 9. Anti-Debugging Techniques

### The Problem

Sites detect DevTools and change behavior:

```javascript
// Detect DevTools
setInterval(() => {
    const start = performance.now();
    debugger;  // Pauses if DevTools open
    if (performance.now() - start > 100) {
        // DevTools detected!
        hideContent();
    }
}, 1000);
```

### Solutions

#### Disable Breakpoints

```python
# In Playwright
page.add_init_script('''
    // Remove debugger statements
    const originalEval = window.eval;
    window.eval = function(code) {
        return originalEval(code.replace(/debugger/g, ''));
    };
''')
```

---

## Detection and Adaptation Pattern

```python
class AdaptiveScraper:
    """Scraper that adapts to obfuscation techniques."""
    
    def __init__(self, url):
        self.url = url
        self.techniques_detected = []
    
    def analyze_page(self, html):
        """Detect obfuscation techniques."""
        
        # Check for dynamic classes
        if re.search(r'class="[a-z]+_[a-z0-9]{5,}"', html):
            self.techniques_detected.append('dynamic_classes')
        
        # Check for custom fonts
        if '@font-face' in html and 'woff' in html:
            self.techniques_detected.append('custom_fonts')
        
        # Check for canvas
        if '<canvas' in html:
            self.techniques_detected.append('canvas_content')
        
        # Check for WebSocket
        if 'WebSocket' in html or 'wss://' in html:
            self.techniques_detected.append('websocket')
        
        return self.techniques_detected
    
    def get_extraction_strategy(self):
        """Choose best extraction method based on detected techniques."""
        
        if 'canvas_content' in self.techniques_detected:
            return 'ocr'
        elif 'websocket' in self.techniques_detected:
            return 'intercept_ws'
        elif 'dynamic_classes' in self.techniques_detected:
            return 'structural_selectors'
        else:
            return 'standard'
```

---

## Summary

| Technique | Detection | Solution |
|-----------|-----------|----------|
| **Dynamic classes** | Regex pattern in class names | Partial match selectors |
| **CSS content** | Empty elements with data-* | Extract from attributes |
| **Custom fonts** | @font-face for prices | OCR or font mapping |
| **Canvas rendering** | `<canvas>` for text | OCR |
| **Infinite scroll** | No pagination links | Scroll automation |
| **WebSocket data** | wss:// in source | Intercept messages |
| **Embedded JSON** | `__INITIAL_STATE__` | Script tag extraction |

### Key Takeaways

1. **Analyze the page first** - Understand what you're dealing with
2. **Browser automation helps** - Many techniques fail against real browsers
3. **Find the data source** - Often easier than scraping rendered HTML
4. **OCR as fallback** - Works when all else fails
5. **Intercept, don't scrape** - Capture data at the source

---

*This completes the Anti-Scraping Tech section. Next: [../03_legal_ethical/](../03_legal_ethical/) - Legal and ethical considerations*
