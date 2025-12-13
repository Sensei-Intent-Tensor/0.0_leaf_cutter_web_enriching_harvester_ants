# Honeypots & Traps

> **Invisible Detection Mechanisms That Catch Bots**

Honeypots are hidden elements specifically designed to catch automated scrapers. Real users never interact with them, but bots fall right in. This document reveals common trap types and how to avoid them.

---

## The Honeypot Concept

```
Visible Page (What Humans See):       Actual HTML (What Bots See):
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│  [Name: ___________]            │   │  [Name: ___________]            │
│                                 │   │  [Hidden: ___________] ← TRAP!  │
│  [Email: __________]            │   │  [Email: __________]            │
│                                 │   │                                 │
│  [Submit]                       │   │  [Submit]                       │
└─────────────────────────────────┘   └─────────────────────────────────┘

Human fills in Name and Email → PASS
Bot fills in ALL fields (including hidden) → CAUGHT!
```

---

## 1. Form Field Honeypots

### 1.1 Hidden Input Fields

The most common honeypot type—form fields that are invisible to users.

```html
<!-- Visible form -->
<form action="/submit" method="POST">
    <label>Name: <input type="text" name="name"></label>
    
    <!-- HONEYPOT: Hidden field -->
    <input type="text" name="email2" style="display:none">
    
    <!-- Another HONEYPOT: Different hiding method -->
    <div style="position:absolute;left:-9999px">
        <input type="text" name="website" tabindex="-1" autocomplete="off">
    </div>
    
    <!-- Real email field -->
    <label>Email: <input type="email" name="email"></label>
    
    <button type="submit">Submit</button>
</form>
```

**Hiding techniques used**:
| Technique | CSS | Detection Risk |
|-----------|-----|----------------|
| `display: none` | `display: none` | Easy to detect |
| `visibility: hidden` | `visibility: hidden` | Medium |
| Off-screen | `position: absolute; left: -9999px` | Medium |
| Zero size | `width: 0; height: 0; overflow: hidden` | Medium |
| Opacity zero | `opacity: 0` | Medium |
| Same color as background | `color: white; background: white` | Hard to detect |

### 1.2 Detection Code

```python
from bs4 import BeautifulSoup
import re

def detect_honeypot_fields(html):
    """Identify likely honeypot form fields."""
    soup = BeautifulSoup(html, 'html.parser')
    honeypots = []
    
    for input_elem in soup.find_all(['input', 'textarea']):
        reasons = []
        
        # Check inline styles
        style = input_elem.get('style', '')
        if 'display:none' in style.replace(' ', '').lower():
            reasons.append('display:none')
        if 'visibility:hidden' in style.replace(' ', '').lower():
            reasons.append('visibility:hidden')
        if 'position:absolute' in style.replace(' ', '').lower():
            if '-9999' in style or '-1000' in style:
                reasons.append('positioned off-screen')
        if 'opacity:0' in style.replace(' ', '').lower():
            reasons.append('opacity:0')
        
        # Check parent elements
        parent = input_elem.parent
        while parent and parent.name:
            parent_style = parent.get('style', '')
            if 'display:none' in parent_style.replace(' ', '').lower():
                reasons.append('parent display:none')
                break
            parent = parent.parent
        
        # Check common honeypot class names
        classes = input_elem.get('class', [])
        class_str = ' '.join(classes).lower()
        honeypot_indicators = [
            'honeypot', 'hp-', 'trap', 'pot', 'hidden-field',
            'leave-blank', 'do-not-fill', 'anti-spam'
        ]
        for indicator in honeypot_indicators:
            if indicator in class_str:
                reasons.append(f'suspicious class: {indicator}')
        
        # Check suspicious field names
        name = (input_elem.get('name', '') or '').lower()
        id_attr = (input_elem.get('id', '') or '').lower()
        suspicious_names = [
            'website', 'url', 'email2', 'address2', 'fax',
            'phone2', 'company2', 'hp', 'honeypot', 'trap'
        ]
        for susp in suspicious_names:
            if susp in name or susp in id_attr:
                reasons.append(f'suspicious name: {name or id_attr}')
        
        # Check tabindex=-1 (can't be reached by keyboard)
        if input_elem.get('tabindex') == '-1':
            reasons.append('tabindex=-1')
        
        # Check autocomplete="off" (unusual for legitimate fields)
        if input_elem.get('autocomplete') == 'off':
            reasons.append('autocomplete=off')
        
        if reasons:
            honeypots.append({
                'element': str(input_elem)[:100],
                'name': input_elem.get('name'),
                'reasons': reasons
            })
    
    return honeypots

# Usage
html = requests.get(url).text
honeypots = detect_honeypot_fields(html)
for hp in honeypots:
    print(f"Potential honeypot: {hp['name']}")
    print(f"  Reasons: {', '.join(hp['reasons'])}")
```

### 1.3 Safe Form Filling

```python
from playwright.sync_api import sync_playwright

def safe_fill_form(page, form_data):
    """Fill form while avoiding honeypots."""
    
    for field_name, value in form_data.items():
        # Find the field
        field = page.query_selector(f"[name='{field_name}']")
        
        if not field:
            continue
        
        # Check if field is visible
        is_visible = field.is_visible()
        
        # Get computed style
        box = field.bounding_box()
        
        # Skip if not visible
        if not is_visible:
            print(f"Skipping hidden field: {field_name}")
            continue
        
        # Skip if off-screen or zero-size
        if box:
            if box['width'] == 0 or box['height'] == 0:
                print(f"Skipping zero-size field: {field_name}")
                continue
            if box['x'] < -1000 or box['y'] < -1000:
                print(f"Skipping off-screen field: {field_name}")
                continue
        
        # Safe to fill
        field.fill(value)
```

---

## 2. Link Honeypots

### 2.1 Hidden Links

Links that humans can't see but scrapers follow.

```html
<div class="content">
    <p>Welcome to our site!</p>
    
    <!-- Normal visible link -->
    <a href="/products">View Products</a>
    
    <!-- HONEYPOT: Hidden link -->
    <a href="/trap/bot-detector" style="display:none">Free Money</a>
    
    <!-- HONEYPOT: Positioned off-screen -->
    <a href="/trap/caught-you" 
       style="position:absolute;left:-9999px;font-size:0">
        Click Here
    </a>
    
    <!-- HONEYPOT: Same color as background -->
    <a href="/trap/invisible" style="color:white;text-decoration:none">
        .
    </a>
</div>
```

### 2.2 robots.txt Honeypots

```
# robots.txt
User-agent: *
Disallow: /admin/
Disallow: /private/
Disallow: /trap/  # HONEYPOT: This path is ONLY for catching bots!
```

**The trap**:
1. Website puts `/trap/` in robots.txt Disallow
2. Good bots respect robots.txt and don't visit `/trap/`
3. Bad bots ignore robots.txt and visit `/trap/`
4. Any request to `/trap/` = bot detected, IP blocked

### 2.3 Safe Link Following

```python
def is_safe_link(link_element):
    """Determine if a link is safe to follow (not a honeypot)."""
    
    # Check visibility
    if not link_element.is_visible():
        return False
    
    # Check bounding box
    box = link_element.bounding_box()
    if not box:
        return False
    
    # Check size (real links have reasonable size)
    if box['width'] < 1 or box['height'] < 1:
        return False
    
    # Check position (not off-screen)
    if box['x'] < -100 or box['y'] < -100:
        return False
    
    # Check href for trap indicators
    href = link_element.get_attribute('href') or ''
    trap_patterns = [
        '/trap', '/honeypot', '/bot', '/caught',
        '/spam', '/blocked', '/detected'
    ]
    for pattern in trap_patterns:
        if pattern in href.lower():
            return False
    
    return True

def get_safe_links(page):
    """Get all safe-to-follow links from page."""
    all_links = page.query_selector_all('a[href]')
    safe_links = []
    
    for link in all_links:
        if is_safe_link(link):
            href = link.get_attribute('href')
            safe_links.append(href)
    
    return safe_links
```

---

## 3. CSS Honeypots

### 3.1 Display-Based Traps

```css
/* Honeypot styles - elements with these classes are traps */
.hp-field, .honeypot-input {
    display: none !important;
}

.trap-link {
    position: absolute;
    left: -9999px;
    visibility: hidden;
}

/* Trick: looks visible in HTML, hidden by external CSS */
.legitimate-looking-class {
    /* This class name doesn't hint at honeypot */
    opacity: 0;
    height: 0;
    overflow: hidden;
}
```

### 3.2 Detecting CSS-Hidden Elements

```python
def get_computed_visibility(page, selector):
    """Check if element is truly visible using computed styles."""
    
    result = page.evaluate(f"""
        (selector) => {{
            const el = document.querySelector(selector);
            if (!el) return {{ exists: false }};
            
            const style = window.getComputedStyle(el);
            const rect = el.getBoundingClientRect();
            
            return {{
                exists: true,
                display: style.display,
                visibility: style.visibility,
                opacity: parseFloat(style.opacity),
                width: rect.width,
                height: rect.height,
                top: rect.top,
                left: rect.left,
                pointerEvents: style.pointerEvents,
                clip: style.clip,
                clipPath: style.clipPath,
            }};
        }}
    """, selector)
    
    if not result['exists']:
        return False
    
    # Check all visibility conditions
    if result['display'] == 'none':
        return False
    if result['visibility'] == 'hidden':
        return False
    if result['opacity'] == 0:
        return False
    if result['width'] == 0 or result['height'] == 0:
        return False
    if result['left'] < -1000 or result['top'] < -1000:
        return False
    if result['pointerEvents'] == 'none':
        return False
    if result['clip'] == 'rect(0px, 0px, 0px, 0px)':
        return False
    
    return True
```

---

## 4. JavaScript Honeypots

### 4.1 Dynamic Honeypot Creation

```javascript
// Site creates honeypots dynamically after page load
document.addEventListener('DOMContentLoaded', function() {
    // Create honeypot field after 2 seconds
    setTimeout(function() {
        const form = document.querySelector('form');
        const honeypot = document.createElement('input');
        honeypot.type = 'text';
        honeypot.name = 'hp_' + Math.random().toString(36).substr(2, 9);
        honeypot.style.cssText = 'position:absolute;left:-9999px';
        honeypot.setAttribute('tabindex', '-1');
        honeypot.setAttribute('autocomplete', 'off');
        form.appendChild(honeypot);
        
        // Store expected empty value
        window.__honeypotField = honeypot.name;
    }, 2000);
});

// On form submit, check honeypot
document.querySelector('form').addEventListener('submit', function(e) {
    const hpField = document.querySelector(`[name="${window.__honeypotField}"]`);
    if (hpField && hpField.value !== '') {
        // Bot detected!
        e.preventDefault();
        // Log or block
        fetch('/api/bot-detected', {
            method: 'POST',
            body: JSON.stringify({ ip: 'logged-server-side' })
        });
    }
});
```

### 4.2 Event-Based Honeypots

```javascript
// Track if user actually focused on legitimate fields
let humanInteraction = false;

document.querySelectorAll('input:not(.honeypot)').forEach(input => {
    input.addEventListener('focus', () => {
        humanInteraction = true;
    });
});

// Honeypot: Invisible field that shouldn't receive focus
const trap = document.querySelector('.honeypot-field');
trap.addEventListener('focus', () => {
    // Bot detected! Real users can't tab to this
    sendBotAlert();
});

// On submit, verify human interaction
document.querySelector('form').addEventListener('submit', (e) => {
    if (!humanInteraction) {
        e.preventDefault();
        // Likely bot - no field was ever focused
    }
});
```

### 4.3 Timing-Based Honeypots

```javascript
// Record when form was loaded
const formLoadTime = Date.now();

document.querySelector('form').addEventListener('submit', (e) => {
    const submitTime = Date.now();
    const fillTime = submitTime - formLoadTime;
    
    // If form was filled in less than 2 seconds, likely bot
    if (fillTime < 2000) {
        e.preventDefault();
        console.log('Bot detected: form filled too fast');
        return;
    }
    
    // If form took more than 30 minutes, session may be stale
    if (fillTime > 30 * 60 * 1000) {
        // Refresh CSRF token or show CAPTCHA
    }
});
```

---

## 5. Data Honeypots

### 5.1 Fake Data Insertion

Sites insert fake data that only scrapers would collect.

```html
<!-- Product listing page -->
<div class="product" data-id="12345">
    <h2>Real Product</h2>
    <span class="price">$99.99</span>
</div>

<!-- HONEYPOT: Fake product hidden from view -->
<div class="product honeypot-product" data-id="TRAP-99999" 
     style="height:0;overflow:hidden;opacity:0">
    <h2>Trap Product XYZ-MONITOR</h2>
    <span class="price">$0.01</span>
</div>

<div class="product" data-id="12346">
    <h2>Another Real Product</h2>
    <span class="price">$149.99</span>
</div>
```

**How it works**:
1. Site inserts fake products with unique identifiers
2. Scraper collects all products including fake ones
3. If fake product appears on competitor's site → caught!
4. Site can now prove scraping occurred

### 5.2 Watermarked Content

```html
<!-- Article content with invisible watermark -->
<article>
    <p>This is the article content that everyone can read.</p>
    
    <!-- Invisible unique identifier -->
    <span style="font-size:0;color:transparent" 
          data-watermark="USR-8472-SESS-28374">&#8203;</span>
    
    <p>More article content here.</p>
    
    <!-- Another watermark using zero-width characters -->
    <p>Final paragraph.&#8203;&#8204;&#8205;</p>
    <!-- Those invisible chars encode: 101 = user ID -->
</article>
```

### 5.3 Detecting Fake Data

```python
def detect_data_honeypots(items):
    """Identify likely honeypot data entries."""
    suspicious = []
    
    for item in items:
        reasons = []
        
        # Check for trap indicators in IDs
        item_id = str(item.get('id', ''))
        if 'trap' in item_id.lower() or 'honeypot' in item_id.lower():
            reasons.append('suspicious ID')
        
        # Check for suspiciously low prices
        price = item.get('price', 0)
        if price <= 0.01:
            reasons.append('suspicious price')
        
        # Check for unusual patterns in names
        name = item.get('name', '')
        if 'MONITOR' in name.upper() or 'TRAP' in name.upper():
            reasons.append('suspicious name')
        
        # Check for missing required fields
        required_fields = ['name', 'price', 'description']
        missing = [f for f in required_fields if not item.get(f)]
        if missing:
            reasons.append(f'missing fields: {missing}')
        
        if reasons:
            suspicious.append({
                'item': item,
                'reasons': reasons
            })
    
    return suspicious
```

---

## 6. Behavioral Honeypots

### 6.1 Mouse Movement Traps

```javascript
// Track mouse movements
const movements = [];
document.addEventListener('mousemove', (e) => {
    movements.push({
        x: e.clientX,
        y: e.clientY,
        time: Date.now()
    });
});

// Honeypot area - any movement here is suspicious
const trapArea = { x: -100, y: -100, width: 50, height: 50 };

document.addEventListener('mousemove', (e) => {
    if (e.clientX >= trapArea.x && e.clientX <= trapArea.x + trapArea.width &&
        e.clientY >= trapArea.y && e.clientY <= trapArea.y + trapArea.height) {
        // Mouse moved through off-screen area - likely automated
        flagAsSuspicious('mouse_trap');
    }
});

// On form submit, analyze movement patterns
function analyzeMovements() {
    if (movements.length < 10) {
        return 'suspicious';  // Too few movements
    }
    
    // Calculate path characteristics
    let totalDistance = 0;
    let straightLineDistance = 0;
    
    for (let i = 1; i < movements.length; i++) {
        const dx = movements[i].x - movements[i-1].x;
        const dy = movements[i].y - movements[i-1].y;
        totalDistance += Math.sqrt(dx*dx + dy*dy);
    }
    
    const firstPoint = movements[0];
    const lastPoint = movements[movements.length - 1];
    straightLineDistance = Math.sqrt(
        Math.pow(lastPoint.x - firstPoint.x, 2) +
        Math.pow(lastPoint.y - firstPoint.y, 2)
    );
    
    // Ratio close to 1 = straight line = bot
    const ratio = straightLineDistance / totalDistance;
    if (ratio > 0.95) {
        return 'suspicious';
    }
    
    return 'human';
}
```

### 6.2 Interaction Sequence Traps

```javascript
// Expected human interaction sequence
const expectedSequence = ['focus_name', 'focus_email', 'focus_message'];
const actualSequence = [];

document.querySelector('[name="name"]').addEventListener('focus', () => {
    actualSequence.push('focus_name');
});
document.querySelector('[name="email"]').addEventListener('focus', () => {
    actualSequence.push('focus_email');
});
document.querySelector('[name="message"]').addEventListener('focus', () => {
    actualSequence.push('focus_message');
});

// Honeypot: This field shouldn't be interacted with
document.querySelector('.hidden-field').addEventListener('focus', () => {
    actualSequence.push('focus_honeypot');  // RED FLAG
});

function validateSequence() {
    // Check if honeypot was focused
    if (actualSequence.includes('focus_honeypot')) {
        return false;
    }
    
    // Check if sequence makes sense (some flexibility)
    if (actualSequence.length === 0) {
        return false;  // No interaction at all
    }
    
    return true;
}
```

---

## 7. Network-Level Honeypots

### 7.1 IP Reputation Traps

```python
# Server-side honeypot checking
def check_ip_reputation(ip_address):
    """Check if IP has hit honeypot endpoints."""
    
    # Check against honeypot hit log
    honeypot_hits = db.query(
        "SELECT * FROM honeypot_logs WHERE ip = ?", 
        ip_address
    )
    
    if honeypot_hits:
        return {
            'is_bot': True,
            'reason': 'hit_honeypot',
            'hits': len(honeypot_hits)
        }
    
    return {'is_bot': False}
```

### 7.2 Request Pattern Traps

```python
# Server-side analysis
def analyze_request_patterns(session_id):
    """Detect bot-like request patterns."""
    
    requests = get_session_requests(session_id)
    
    # Check for sequential URL access (bots often follow HTML order)
    urls = [r['url'] for r in requests]
    
    # Compare to expected human navigation patterns
    # Humans: homepage → category → product → cart
    # Bots: page1 → page2 → page3 → page4 (sequential)
    
    # Check for honeypot URL access
    honeypot_urls = ['/trap/', '/honeypot/', '/admin/fake/']
    for url in urls:
        for trap in honeypot_urls:
            if trap in url:
                return {'is_bot': True, 'reason': 'accessed_honeypot_url'}
    
    # Check timing patterns
    if requests:
        intervals = []
        for i in range(1, len(requests)):
            interval = requests[i]['time'] - requests[i-1]['time']
            intervals.append(interval)
        
        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            variance = sum((x - avg_interval)**2 for x in intervals) / len(intervals)
            
            # Very low variance = bot (exact timing)
            if variance < 0.1 and avg_interval < 1:
                return {'is_bot': True, 'reason': 'timing_too_consistent'}
    
    return {'is_bot': False}
```

---

## 8. Avoiding Honeypots

### 8.1 Comprehensive Honeypot Detection

```python
class HoneypotDetector:
    """Detect and avoid various types of honeypots."""
    
    def __init__(self, page):
        self.page = page
    
    def is_element_visible(self, element):
        """Check if element is truly visible to users."""
        if not element:
            return False
        
        # Use JavaScript for accurate visibility check
        return self.page.evaluate("""
            (el) => {
                if (!el) return false;
                
                const style = window.getComputedStyle(el);
                const rect = el.getBoundingClientRect();
                
                // Check CSS properties
                if (style.display === 'none') return false;
                if (style.visibility === 'hidden') return false;
                if (parseFloat(style.opacity) === 0) return false;
                
                // Check dimensions
                if (rect.width === 0 || rect.height === 0) return false;
                
                // Check position
                if (rect.left < -1000 || rect.top < -1000) return false;
                if (rect.right < 0 || rect.bottom < 0) return false;
                
                // Check if covered by other elements
                const centerX = rect.left + rect.width / 2;
                const centerY = rect.top + rect.height / 2;
                const topElement = document.elementFromPoint(centerX, centerY);
                
                if (topElement !== el && !el.contains(topElement)) {
                    return false;  // Covered by another element
                }
                
                return true;
            }
        """, element)
    
    def analyze_form(self, form_selector):
        """Analyze form for honeypot fields."""
        form = self.page.query_selector(form_selector)
        if not form:
            return {'error': 'Form not found'}
        
        fields = form.query_selector_all('input, textarea, select')
        
        safe_fields = []
        honeypot_fields = []
        
        for field in fields:
            field_name = field.get_attribute('name')
            
            if self.is_element_visible(field):
                safe_fields.append(field_name)
            else:
                honeypot_fields.append(field_name)
        
        return {
            'safe_fields': safe_fields,
            'honeypot_fields': honeypot_fields
        }
    
    def get_safe_links(self):
        """Get all safe-to-follow links."""
        links = self.page.query_selector_all('a[href]')
        
        safe = []
        for link in links:
            href = link.get_attribute('href')
            
            # Skip obvious traps
            if any(trap in href.lower() for trap in 
                   ['/trap', '/honeypot', '/bot', '/caught']):
                continue
            
            # Skip hidden links
            if not self.is_element_visible(link):
                continue
            
            safe.append(href)
        
        return safe
```

### 8.2 Safe Scraping Patterns

```python
class SafeScraper:
    """Scraper with honeypot avoidance."""
    
    def __init__(self):
        self.detector = None
    
    def scrape_page(self, page, url):
        page.goto(url)
        
        self.detector = HoneypotDetector(page)
        
        # Wait for dynamic honeypots to load
        page.wait_for_timeout(3000)
        
        # Get safe content only
        data = {
            'links': self.get_safe_content_links(page),
            'products': self.get_safe_products(page),
            'text': self.get_safe_text(page)
        }
        
        return data
    
    def get_safe_content_links(self, page):
        """Extract only visible, safe links."""
        return self.detector.get_safe_links()
    
    def get_safe_products(self, page):
        """Extract only visible product data."""
        products = []
        
        for elem in page.query_selector_all('.product'):
            if not self.detector.is_element_visible(elem):
                continue
            
            # Extract product data
            name = elem.query_selector('.name')
            price = elem.query_selector('.price')
            
            if name and price:
                products.append({
                    'name': name.inner_text(),
                    'price': price.inner_text()
                })
        
        return products
    
    def fill_form_safely(self, page, form_selector, data):
        """Fill form while avoiding honeypots."""
        analysis = self.detector.analyze_form(form_selector)
        
        for field_name, value in data.items():
            if field_name in analysis['safe_fields']:
                field = page.query_selector(f"[name='{field_name}']")
                field.fill(value)
            else:
                print(f"Skipping honeypot field: {field_name}")
```

---

## 9. Testing for Honeypots

### 9.1 Manual Testing Checklist

```
Before scraping a site, check:

□ View page source vs. rendered page
  └── Look for hidden elements

□ Check robots.txt
  └── Note any suspicious Disallow entries

□ Inspect forms
  └── Look for hidden/invisible fields
  └── Check for unusual field names
  └── Note tabindex=-1 attributes

□ Check CSS files
  └── Search for "honeypot", "trap", "hidden"

□ Monitor network requests
  └── Look for /trap/, /honeypot/ endpoints

□ Test with different speeds
  └── Fast = caught, slow = passed?
```

### 9.2 Automated Testing

```python
def test_for_honeypots(url):
    """Comprehensive honeypot detection test."""
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        
        results = {
            'form_honeypots': [],
            'link_honeypots': [],
            'data_honeypots': [],
            'timing_traps': False
        }
        
        # Test form honeypots
        forms = page.query_selector_all('form')
        for form in forms:
            detector = HoneypotDetector(page)
            analysis = detector.analyze_form('form')
            if analysis.get('honeypot_fields'):
                results['form_honeypots'].extend(analysis['honeypot_fields'])
        
        # Test link honeypots
        all_links = page.query_selector_all('a[href]')
        for link in all_links:
            href = link.get_attribute('href')
            if not HoneypotDetector(page).is_element_visible(link):
                results['link_honeypots'].append(href)
        
        # Test timing (try fast submission)
        # ... implementation depends on form
        
        browser.close()
        return results
```

---

## 10. Summary

### Honeypot Types

| Type | What It Is | How to Detect |
|------|------------|---------------|
| **Form Field** | Hidden input fields | Check visibility, CSS |
| **Link** | Invisible/trap links | Check visibility, path |
| **CSS** | Elements hidden via CSS | Computed styles |
| **JavaScript** | Dynamically created traps | Wait for page load |
| **Data** | Fake content entries | Pattern analysis |
| **Behavioral** | Movement/timing analysis | Hard to detect |
| **Network** | Trap URLs | robots.txt, patterns |

### Detection Priorities

```
Check in this order:
1. CSS visibility (display, visibility, opacity)
2. Element position (off-screen)
3. Element size (zero dimensions)
4. Suspicious names/classes
5. robots.txt Disallow entries
6. URL patterns
```

### Key Principles

1. **Never interact with invisible elements**
2. **Respect robots.txt (usually)**
3. **Add human-like delays**
4. **Verify element visibility before interaction**
5. **Skip suspiciously named fields/links**
6. **Monitor for pattern changes**

---

*Next: [05_cloudflare_akamai_etc.md](05_cloudflare_akamai_etc.md) - Major protection services*
