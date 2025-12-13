# Honeypots & Traps

> **The Hidden Snares That Catch Bots**

Honeypots are invisible traps designed to catch automated visitors. A human never sees them, but bots fall right in.

---

## What Are Honeypots?

A honeypot is a decoy element that:
- Is hidden from human users (via CSS or positioning)
- Appears normal to bots parsing HTML
- Triggers detection when interacted with

```
Human sees:         Bot sees:
┌─────────────┐    ┌─────────────┐
│ Name: [___] │    │ Name: [___] │
│ Email:[___] │    │ Email:[___] │
│ [Submit]    │    │ Phone:[___] │  ← Hidden field!
└─────────────┘    │ [Submit]    │
                   └─────────────┘
```

---

## Types of Honeypots

### 1. Hidden Form Fields

The most common honeypot type.

```html
<!-- Honeypot field - hidden with CSS -->
<form action="/submit">
    <input type="text" name="name" placeholder="Name">
    <input type="email" name="email" placeholder="Email">
    
    <!-- Honeypot: human never sees this -->
    <input type="text" name="phone" style="display:none">
    
    <!-- Alternative hiding methods -->
    <input type="text" name="website" class="hidden-field">
    <input type="text" name="address" aria-hidden="true">
    
    <button type="submit">Submit</button>
</form>

<style>
.hidden-field {
    position: absolute;
    left: -9999px;
}
</style>
```

**Detection logic:**
```python
# Server-side
if request.form.get('phone'):
    # Bot detected! Human would never fill this
    block_request()
```

### 2. Invisible Links

Links hidden from view but present in HTML.

```html
<!-- Normal navigation -->
<nav>
    <a href="/products">Products</a>
    <a href="/about">About</a>
    <a href="/contact">Contact</a>
</nav>

<!-- Honeypot link - invisible to humans -->
<a href="/trap" style="display:none">Special Offers</a>
<a href="/catch-bot" class="invisible-link">Click Here</a>

<style>
.invisible-link {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
}
</style>
```

**Detection logic:**
```python
# Server-side: /trap endpoint
def trap_endpoint():
    ip = request.remote_addr
    add_to_blocklist(ip)
    log_bot_activity(ip, request.headers)
    return "Gotcha!", 403
```

### 3. CSS Trap Elements

Elements that look clickable to parsers but are hidden:

```html
<div class="product-listing">
    <div class="product">Real Product</div>
    <div class="product">Real Product</div>
    
    <!-- Honeypot product -->
    <div class="product honeypot" style="visibility:hidden; height:0; overflow:hidden;">
        <a href="/fake-product-12345">Fake Product</a>
    </div>
</div>
```

### 4. JavaScript Honeypots

Content revealed only to non-JS clients:

```html
<noscript>
    <!-- Only visible if JavaScript disabled -->
    <a href="/bot-trap">Enable JavaScript</a>
</noscript>

<script>
// Remove honeypot for real browsers
document.querySelector('.js-trap')?.remove();
</script>
```

### 5. Timing Honeypots

Forms that are submitted too quickly:

```html
<form id="contact-form">
    <input type="hidden" name="timestamp" id="form-timestamp">
    <input type="text" name="message">
    <button type="submit">Send</button>
</form>

<script>
document.getElementById('form-timestamp').value = Date.now();
</script>
```

**Server-side:**
```python
def handle_form():
    timestamp = int(request.form.get('timestamp', 0))
    current_time = int(time.time() * 1000)
    
    # If form submitted in less than 3 seconds
    if current_time - timestamp < 3000:
        # Probably a bot
        block_request()
```

### 6. CAPTCHA Honeypots

Pre-filled CAPTCHA that should be cleared:

```html
<form>
    <input type="text" name="captcha" value="remove-this-text" 
           onfocus="this.value=''">
    <p>Clear the text above and type 'HUMAN'</p>
</form>
```

Bots often submit without modifying the pre-filled value.

---

## Detecting Honeypots (As a Scraper)

### Visual Indicators

```python
def is_honeypot_field(element):
    """Check if form field is likely a honeypot."""
    
    # Get computed style
    style = element.get_attribute('style') or ''
    class_name = element.get_attribute('class') or ''
    
    # Check for hiding patterns
    hiding_patterns = [
        'display:none', 'display: none',
        'visibility:hidden', 'visibility: hidden',
        'position:absolute', 'left:-9999',
        'height:0', 'width:0',
        'opacity:0',
    ]
    
    for pattern in hiding_patterns:
        if pattern in style.lower():
            return True
    
    # Suspicious class names
    suspicious_classes = [
        'hidden', 'hide', 'invisible', 'offscreen',
        'trap', 'honeypot', 'hp', 'special-field'
    ]
    
    for cls in suspicious_classes:
        if cls in class_name.lower():
            return True
    
    # Check aria-hidden
    if element.get_attribute('aria-hidden') == 'true':
        return True
    
    # Check type="hidden"
    if element.get_attribute('type') == 'hidden':
        # Not necessarily honeypot, but don't modify
        return True
    
    return False
```

### Common Honeypot Field Names

```python
HONEYPOT_FIELD_NAMES = [
    # Generic
    'honeypot', 'hp', 'trap', 'gotcha',
    
    # Fake contact fields
    'phone2', 'email2', 'address2',
    'fax', 'pager', 'telex',
    
    # Enticing names
    'website', 'url', 'homepage',
    'company', 'organization',
    
    # Obvious bait
    'leave-blank', 'do-not-fill',
    'not-for-humans',
    
    # Hidden with prefixes
    'hp_name', 'trap_email',
]
```

### Link Honeypot Detection

```python
from playwright.sync_api import sync_playwright

def find_honeypot_links(page):
    """Identify links that are hidden honeypots."""
    
    honeypot_links = []
    
    links = page.query_selector_all('a')
    for link in links:
        # Check if visually hidden
        is_visible = link.is_visible()
        
        # Get bounding box
        box = link.bounding_box()
        
        if not is_visible:
            honeypot_links.append(link.get_attribute('href'))
        elif box and (box['width'] <= 1 or box['height'] <= 1):
            honeypot_links.append(link.get_attribute('href'))
    
    return honeypot_links

# Usage
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com")
    
    traps = find_honeypot_links(page)
    print(f"Honeypot links to avoid: {traps}")
```

---

## Safe Scraping Strategies

### Strategy 1: Only Interact with Visible Elements

```python
from playwright.sync_api import sync_playwright

def safe_fill_form(page, form_selector, data):
    """Only fill visible form fields."""
    
    form = page.query_selector(form_selector)
    inputs = form.query_selector_all('input, textarea, select')
    
    for input_elem in inputs:
        name = input_elem.get_attribute('name')
        
        # Skip if hidden
        if not input_elem.is_visible():
            print(f"Skipping hidden field: {name}")
            continue
        
        # Skip if no data for this field
        if name not in data:
            continue
        
        # Fill the field
        input_elem.fill(data[name])
```

### Strategy 2: Check Element Visibility Before Click

```python
def safe_click(page, selector):
    """Only click if element is truly visible."""
    
    element = page.query_selector(selector)
    
    if not element:
        return False
    
    # Check visibility
    if not element.is_visible():
        print(f"Element not visible, skipping: {selector}")
        return False
    
    # Check size
    box = element.bounding_box()
    if not box or box['width'] < 5 or box['height'] < 5:
        print(f"Element too small, likely honeypot: {selector}")
        return False
    
    # Check if in viewport
    if box['y'] < 0 or box['x'] < 0:
        print(f"Element outside viewport: {selector}")
        return False
    
    element.click()
    return True
```

### Strategy 3: Follow Rendered Links Only

```python
def get_safe_links(page, base_url):
    """Get only visible, clickable links."""
    
    safe_links = []
    links = page.query_selector_all('a[href]')
    
    for link in links:
        href = link.get_attribute('href')
        
        # Must be visible
        if not link.is_visible():
            continue
        
        # Must have reasonable size
        box = link.bounding_box()
        if not box or box['width'] < 2 or box['height'] < 2:
            continue
        
        # Check for honeypot indicators
        text = link.inner_text().lower()
        if any(trap in text for trap in ['trap', 'honeypot', 'click here']):
            continue
        
        # Resolve relative URLs
        if href.startswith('/'):
            href = base_url + href
        
        safe_links.append(href)
    
    return safe_links
```

---

## Advanced Honeypots

### JavaScript-Generated Traps

```html
<script>
// Create honeypot dynamically
setTimeout(() => {
    const trap = document.createElement('a');
    trap.href = '/dynamic-trap';
    trap.style.cssText = 'position:fixed;top:-1000px;';
    trap.textContent = 'Free Stuff!';
    document.body.appendChild(trap);
}, 1000);
</script>
```

**Defense:** Wait for page to fully load, then check visibility.

### Data-Attribute Traps

```html
<a href="/legit" data-actual-href="/trap">Click Me</a>

<script>
document.querySelectorAll('a[data-actual-href]').forEach(a => {
    a.addEventListener('click', (e) => {
        e.preventDefault();
        window.location = a.dataset.actualHref;
    });
});
</script>
```

**Defense:** Use browser automation that respects JavaScript.

### Canvas/Image Traps

```html
<canvas id="trap-canvas" width="1" height="1"></canvas>
<script>
const canvas = document.getElementById('trap-canvas');
const ctx = canvas.getContext('2d');
// Draw "invisible" link coordinates
ctx.fillStyle = 'rgba(0,0,0,0.01)';
ctx.fillRect(0, 0, 1, 1);
// Track clicks on canvas
canvas.onclick = () => reportBot();
</script>
```

---

## Honeypot Detection Checklist

```python
def is_safe_to_interact(element, page):
    """Comprehensive honeypot check."""
    
    checks = {
        'is_visible': element.is_visible(),
        'has_dimensions': False,
        'in_viewport': False,
        'not_hidden_style': True,
        'not_suspicious_class': True,
        'not_suspicious_name': True,
    }
    
    # Check dimensions
    box = element.bounding_box()
    if box:
        checks['has_dimensions'] = box['width'] > 1 and box['height'] > 1
        checks['in_viewport'] = box['x'] >= 0 and box['y'] >= 0
    
    # Check style
    style = element.evaluate('el => window.getComputedStyle(el).cssText')
    hidden_styles = ['display: none', 'visibility: hidden', 'opacity: 0']
    checks['not_hidden_style'] = not any(s in style for s in hidden_styles)
    
    # Check class
    class_name = element.get_attribute('class') or ''
    suspicious = ['hidden', 'trap', 'honeypot', 'invisible']
    checks['not_suspicious_class'] = not any(s in class_name.lower() for s in suspicious)
    
    # Check name
    name = element.get_attribute('name') or ''
    suspicious_names = ['honeypot', 'trap', 'hp', 'gotcha']
    checks['not_suspicious_name'] = not any(s in name.lower() for s in suspicious_names)
    
    # All checks must pass
    return all(checks.values()), checks
```

---

## Summary

| Honeypot Type | Detection Method | Avoidance |
|---------------|------------------|-----------|
| **Hidden fields** | Check visibility, style | Skip hidden inputs |
| **Invisible links** | Check bounding box | Only click visible links |
| **CSS traps** | Computed style check | Use browser rendering |
| **JS honeypots** | Wait for full load | Respect JavaScript |
| **Timing traps** | N/A | Add human-like delays |
| **Name-based** | Check field names | Filter suspicious names |

### Key Takeaways

1. **Use browser automation** - See what humans see
2. **Check visibility** - Before ANY interaction
3. **Verify dimensions** - 0x0 or 1x1 = trap
4. **Inspect styles** - Look for hiding techniques
5. **Add delays** - Don't submit forms instantly
6. **Test carefully** - One wrong click = blocked

---

*Next: [05_cloudflare_akamai_etc.md](05_cloudflare_akamai_etc.md) - Major WAF and CDN providers*
