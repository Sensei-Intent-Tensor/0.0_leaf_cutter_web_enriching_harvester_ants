# Cloudflare, Akamai & Other WAFs

> **The Enterprise Gatekeepers**

Web Application Firewalls (WAFs) and CDN providers are the first line of defense for many websites. Understanding how they work is essential for scraping protected sites.

---

## What Are WAFs and CDNs?

### CDN (Content Delivery Network)

Distributes content across global servers for speed:

```
Without CDN:
User (Tokyo) ────────────────────▶ Server (New York)
                 High latency

With CDN:
User (Tokyo) ──▶ Edge Server (Tokyo) ──cache──▶ Origin (New York)
                 Low latency
```

### WAF (Web Application Firewall)

Filters malicious traffic before it reaches the server:

```
                      ┌─────────────┐
Internet Traffic ───▶ │     WAF     │ ───▶ Origin Server
                      │             │
                      │ ✓ Allow     │
                      │ ✗ Block     │
                      │ ? Challenge │
                      └─────────────┘
```

### Combined Services

Most providers offer both CDN + WAF + Bot Protection:

| Provider | CDN | WAF | Bot Protection |
|----------|-----|-----|----------------|
| **Cloudflare** | ✅ | ✅ | ✅ |
| **Akamai** | ✅ | ✅ | ✅ |
| **AWS CloudFront + WAF** | ✅ | ✅ | ✅ |
| **Fastly** | ✅ | ✅ | ✅ |
| **Imperva (Incapsula)** | ✅ | ✅ | ✅ |
| **PerimeterX** | ❌ | ✅ | ✅ |
| **DataDome** | ❌ | ✅ | ✅ |

---

## Cloudflare

**Market share: ~80% of protected sites**

### Detection Signs

```python
def is_cloudflare(response):
    """Detect if site uses Cloudflare."""
    
    headers = response.headers
    
    # Header indicators
    if 'cf-ray' in headers:
        return True
    if 'cf-cache-status' in headers:
        return True
    if headers.get('server', '').lower() == 'cloudflare':
        return True
    
    # Cookie indicators
    if '__cf_bm' in response.cookies:
        return True
    if 'cf_clearance' in response.cookies:
        return True
    
    # Content indicators
    if 'cloudflare' in response.text.lower():
        if 'challenge' in response.text.lower():
            return True
    
    return False
```

### Challenge Types

#### 1. JavaScript Challenge (5-Second Wait)

```html
<!-- Classic "Checking your browser" page -->
<div id="cf-wrapper">
    <h1>Checking your browser before accessing example.com</h1>
    <p>This process is automatic. Your browser will redirect shortly.</p>
    <p>Please wait up to 5 seconds...</p>
</div>
```

What it does:
- Runs JavaScript to compute a challenge
- Sets `cf_clearance` cookie on success
- Cookie valid for ~30 minutes

#### 2. Interactive Challenge (CAPTCHA)

```html
<!-- Cloudflare Turnstile or hCaptcha -->
<div class="cf-turnstile" data-sitekey="..."></div>
```

Triggered when:
- JavaScript challenge fails
- Suspicious behavior detected
- High-risk IP address

#### 3. Managed Challenge

Cloudflare decides dynamically:
- Low risk → JavaScript challenge
- Medium risk → Turnstile
- High risk → Block

### Cloudflare Bot Management Tiers

| Tier | Protection Level | Bypass Difficulty |
|------|------------------|-------------------|
| **Free** | Basic JS challenge | Easy |
| **Pro** | JS + rate limiting | Medium |
| **Business** | Advanced challenges | Hard |
| **Enterprise** | ML-based detection | Very Hard |

### Bypassing Cloudflare

#### Method 1: Browser Automation

```python
from playwright.sync_api import sync_playwright

def bypass_cloudflare(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Visible often helps
        context = browser.new_context()
        page = context.new_page()
        
        page.goto(url)
        
        # Wait for challenge to complete
        page.wait_for_function('''
            () => !document.querySelector('#cf-wrapper')
        ''', timeout=30000)
        
        # Get cookies for future requests
        cookies = context.cookies()
        cf_clearance = next(
            (c for c in cookies if c['name'] == 'cf_clearance'),
            None
        )
        
        content = page.content()
        browser.close()
        
        return content, cf_clearance
```

#### Method 2: cloudscraper Library

```python
import cloudscraper

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False
    }
)

response = scraper.get("https://cloudflare-protected-site.com")
print(response.text)
```

#### Method 3: FlareSolverr (Docker Service)

```python
import requests

# FlareSolverr running on localhost:8191
def solve_cloudflare(url):
    response = requests.post(
        "http://localhost:8191/v1",
        json={
            "cmd": "request.get",
            "url": url,
            "maxTimeout": 60000
        }
    )
    
    result = response.json()
    return result['solution']['response']
```

#### Method 4: Cookie Reuse

```python
# Get cf_clearance once via browser
cf_clearance = "abc123..."

# Reuse in requests
session = requests.Session()
session.cookies.set('cf_clearance', cf_clearance, domain='.example.com')
session.headers.update({
    'User-Agent': 'Same UA used to get cookie'
})

# Use until cookie expires (~30 min)
response = session.get("https://example.com/data")
```

---

## Akamai Bot Manager

**Used by: Major retailers, airlines, banks**

### Detection Signs

```python
def is_akamai(response):
    """Detect Akamai protection."""
    
    headers = response.headers
    
    # Header indicators
    if 'akamai' in headers.get('server', '').lower():
        return True
    if 'x-akamai-transformed' in headers:
        return True
    
    # Cookie indicators
    cookies = ['_abck', 'ak_bmsc', 'bm_sv', 'bm_sz']
    for cookie in cookies:
        if cookie in response.cookies:
            return True
    
    # Script indicators
    if '_acxmBM' in response.text or 'akamai' in response.text.lower():
        return True
    
    return False
```

### How Akamai Works

1. **Sensor Data Collection** - JavaScript collects browser fingerprint
2. **_abck Cookie** - Contains encrypted sensor data
3. **Server Validation** - Akamai validates the sensor data
4. **Challenge/Block** - If validation fails

### Akamai Sensor Data

```javascript
// Akamai's script collects:
const sensorData = {
    // Browser info
    userAgent: navigator.userAgent,
    language: navigator.language,
    platform: navigator.platform,
    
    // Screen info
    screenWidth: screen.width,
    screenHeight: screen.height,
    colorDepth: screen.colorDepth,
    
    // Mouse movements
    mouseMovements: [],
    
    // Keyboard events
    keyEvents: [],
    
    // Touch events
    touchEvents: [],
    
    // Canvas fingerprint
    canvasFingerprint: getCanvasHash(),
    
    // WebGL fingerprint
    webglFingerprint: getWebGLHash(),
    
    // Audio fingerprint
    audioFingerprint: getAudioHash(),
    
    // Timing data
    timestamps: [],
};
```

### Bypassing Akamai

#### Method 1: Full Browser Automation

```python
from playwright.sync_api import sync_playwright
import time

def bypass_akamai(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # Headed mode often required
            args=['--disable-blink-features=AutomationControlled']
        )
        
        page = browser.new_page()
        
        # Navigate
        page.goto(url)
        
        # Perform human-like actions to generate sensor data
        page.mouse.move(100, 100)
        time.sleep(0.5)
        page.mouse.move(200, 200)
        time.sleep(0.3)
        
        # Scroll
        page.evaluate('window.scrollBy(0, 300)')
        time.sleep(1)
        
        # Wait for _abck cookie to be valid
        page.wait_for_timeout(5000)
        
        cookies = page.context.cookies()
        content = page.content()
        
        browser.close()
        return content, cookies
```

#### Method 2: Sensor Data Generation

Some services attempt to generate valid sensor data:

```python
# Using a hypothetical sensor generator
from akamai_sensor import generate_sensor

sensor_data = generate_sensor(
    user_agent="Mozilla/5.0...",
    screen_width=1920,
    screen_height=1080,
)

# Submit with request
response = requests.post(url, cookies={
    '_abck': sensor_data
})
```

**Note:** This is extremely difficult and changes frequently.

---

## PerimeterX (HUMAN)

**Used by: Ticketmaster, StubHub, many e-commerce**

### Detection Signs

```python
def is_perimeterx(response):
    """Detect PerimeterX protection."""
    
    # Cookie indicators
    px_cookies = ['_px', '_pxvid', '_pxff_', '_pxhd']
    for cookie in px_cookies:
        if any(cookie in c for c in response.cookies.keys()):
            return True
    
    # Script indicators
    if 'captcha.px-cdn.net' in response.text:
        return True
    if '/px/client/' in response.text:
        return True
    
    return False
```

### PerimeterX Challenge Types

1. **Block Page** - Complete denial
2. **CAPTCHA** - Press & Hold challenge
3. **Rate Limiting** - Slow down responses

### Bypassing PerimeterX

Extremely difficult due to:
- Advanced fingerprinting
- Behavioral analysis
- Frequent algorithm updates

Best approaches:
- Residential proxies
- Full browser with stealth
- Very slow, human-like behavior
- Sometimes just not possible

---

## DataDome

**Used by: Reddit, many European sites**

### Detection Signs

```python
def is_datadome(response):
    """Detect DataDome protection."""
    
    # Cookie indicators
    if 'datadome' in str(response.cookies).lower():
        return True
    
    # Header indicators
    if 'x-datadome' in str(response.headers).lower():
        return True
    
    # Content indicators
    if 'datadome' in response.text.lower():
        return True
    if 'geo.captcha-delivery.com' in response.text:
        return True
    
    return False
```

### DataDome Characteristics

- CAPTCHA challenges with device check
- Slider challenges
- Geographic verification
- Device fingerprinting

---

## Imperva (Incapsula)

**Used by: Banks, government sites, healthcare**

### Detection Signs

```python
def is_imperva(response):
    """Detect Imperva/Incapsula protection."""
    
    # Cookie indicators
    imperva_cookies = ['incap_ses_', 'visid_incap_', 'nlbi_']
    for cookie in imperva_cookies:
        if any(cookie in c for c in response.cookies.keys()):
            return True
    
    # Header indicators
    if 'x-iinfo' in response.headers:
        return True
    
    return False
```

### Imperva Challenge

Usually JavaScript-based with cookie validation.

---

## AWS WAF

**Used by: Sites on AWS infrastructure**

### Detection Signs

```python
def is_aws_waf(response):
    """Detect AWS WAF."""
    
    # Error responses
    if response.status_code == 403:
        if 'Request blocked' in response.text:
            return True
        if 'aws' in response.text.lower():
            return True
    
    # Headers
    if 'x-amzn-waf' in str(response.headers).lower():
        return True
    
    return False
```

### AWS WAF Characteristics

- Rule-based blocking
- Rate limiting
- IP reputation
- Custom rules per customer

---

## General Bypass Strategies

### Strategy 1: Identify the Protection

```python
def identify_protection(url):
    """Identify which WAF/bot protection is in use."""
    
    response = requests.get(url, allow_redirects=False)
    
    protections = {
        'cloudflare': is_cloudflare(response),
        'akamai': is_akamai(response),
        'perimeterx': is_perimeterx(response),
        'datadome': is_datadome(response),
        'imperva': is_imperva(response),
        'aws_waf': is_aws_waf(response),
    }
    
    detected = [k for k, v in protections.items() if v]
    return detected

# Usage
protections = identify_protection("https://target-site.com")
print(f"Detected: {protections}")
```

### Strategy 2: Layered Approach

```python
def scrape_protected_site(url):
    """Try multiple bypass methods."""
    
    # Level 1: Simple request with good headers
    response = requests.get(url, headers=BROWSER_HEADERS)
    if response.status_code == 200:
        return response.text
    
    # Level 2: cloudscraper
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    if response.status_code == 200:
        return response.text
    
    # Level 3: Browser automation
    content = browser_bypass(url)
    if content:
        return content
    
    # Level 4: FlareSolverr or similar
    content = flaresolverr_bypass(url)
    if content:
        return content
    
    raise Exception("All bypass methods failed")
```

### Strategy 3: Session Persistence

```python
class ProtectedSiteScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.cookies = {}
        self.last_solved = 0
    
    def ensure_access(self):
        """Ensure we have valid cookies."""
        # Cookies expire after ~30 min typically
        if time.time() - self.last_solved > 1800:
            self.solve_challenge()
    
    def solve_challenge(self):
        """Solve WAF challenge and get cookies."""
        # Use browser automation
        cookies = browser_solve(self.base_url)
        
        for cookie in cookies:
            self.session.cookies.set(
                cookie['name'],
                cookie['value'],
                domain=cookie.get('domain')
            )
        
        self.last_solved = time.time()
    
    def get(self, path):
        """Make request with valid session."""
        self.ensure_access()
        return self.session.get(f"{self.base_url}{path}")
```

---

## Difficulty Rankings

| Protection | Bypass Difficulty | Best Approach |
|------------|-------------------|---------------|
| **Cloudflare Free** | Easy | cloudscraper |
| **Cloudflare Pro** | Medium | Browser automation |
| **Cloudflare Enterprise** | Hard | Residential + stealth |
| **Akamai Standard** | Hard | Full browser + behavior |
| **Akamai Enterprise** | Very Hard | May not be possible |
| **PerimeterX** | Very Hard | Residential + slow |
| **DataDome** | Hard | Browser + challenges |
| **Imperva** | Medium | Browser automation |
| **AWS WAF** | Varies | Depends on rules |

---

## Summary

| Provider | Detection Headers/Cookies | Primary Challenge |
|----------|---------------------------|-------------------|
| **Cloudflare** | cf-ray, cf_clearance | JavaScript/Turnstile |
| **Akamai** | _abck, ak_bmsc | Sensor data |
| **PerimeterX** | _px, _pxvid | Behavioral |
| **DataDome** | datadome | CAPTCHA + device |
| **Imperva** | incap_ses_, visid_incap_ | JavaScript |

### Key Takeaways

1. **Identify first** - Know what you're dealing with
2. **Start simple** - Try basic methods first
3. **Escalate gradually** - Move to browser automation if needed
4. **Reuse sessions** - Don't solve challenges repeatedly
5. **Be patient** - Some sites may not be worth the effort

---

*Next: [06_login_walls_auth_gates.md](06_login_walls_auth_gates.md) - Handling authentication barriers*
