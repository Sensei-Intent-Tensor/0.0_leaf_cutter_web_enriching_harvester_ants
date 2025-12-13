# Cloudflare, Akamai & Other WAFs

> **The Gatekeepers of the Modern Web**

Web Application Firewalls (WAFs) and Content Delivery Networks (CDNs) with bot protection are the most common barriers you'll encounter. Understanding how they work is essential for any serious scraping project.

---

## The Landscape

### Market Share of Bot Protection

```
┌─────────────────────────────────────────────────────────┐
│  Cloudflare     ████████████████████████████  ~40%     │
│  Akamai         ██████████████                ~20%     │
│  AWS WAF        ████████                      ~12%     │
│  Imperva        ██████                        ~10%     │
│  Fastly         ████                          ~6%      │
│  PerimeterX     ███                           ~5%      │
│  DataDome       ██                            ~3%      │
│  Others         ██                            ~4%      │
└─────────────────────────────────────────────────────────┘
```

---

## 1. Cloudflare

### What Cloudflare Does

Cloudflare sits between users and websites:

```
User Request ──▶ Cloudflare ──▶ Origin Server
                    │
                    ├── DDoS Protection
                    ├── Bot Detection
                    ├── JavaScript Challenges
                    ├── CAPTCHA (Turnstile)
                    └── Rate Limiting
```

### Detection Levels

| Level | Name | Protection |
|-------|------|------------|
| **Off** | Essentially Off | Minimal |
| **Low** | Low | Basic bot blocking |
| **Medium** | Medium | JS challenges for suspicious |
| **High** | High | JS challenges for most |
| **I'm Under Attack** | Maximum | Challenge everyone |

### Cloudflare Challenges

#### JavaScript Challenge

```
1. Initial request arrives
2. Cloudflare returns JS challenge page
3. Browser executes JavaScript
4. JavaScript computes proof-of-work
5. Browser submits solution
6. Cloudflare sets cf_clearance cookie
7. Subsequent requests pass with cookie
```

**The Challenge Page:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Just a moment...</title>
</head>
<body>
    <div id="challenge-running">
        Checking your browser...
    </div>
    <script src="/cdn-cgi/challenge-platform/scripts/..."></script>
</body>
</html>
```

#### Turnstile (CAPTCHA Alternative)

Cloudflare's privacy-focused CAPTCHA:
- Usually invisible
- No image puzzles
- Behavioral analysis
- Falls back to visible challenge if suspicious

### Cloudflare Cookies

| Cookie | Purpose | Lifetime |
|--------|---------|----------|
| `__cf_bm` | Bot management | 30 min |
| `cf_clearance` | Challenge passed | Hours/days |
| `__cflb` | Load balancing | Session |
| `__cfruid` | Rate limiting | Session |

### Bypassing Cloudflare

#### Method 1: Undetected ChromeDriver

```python
import undetected_chromedriver as uc

driver = uc.Chrome(headless=True, version_main=120)
driver.get("https://cloudflare-protected.com")

# Wait for challenge to complete
import time
time.sleep(10)

# Get cookies for requests
cookies = driver.get_cookies()
cf_clearance = next(c for c in cookies if c['name'] == 'cf_clearance')
```

#### Method 2: cloudscraper

```python
import cloudscraper

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

response = scraper.get("https://cloudflare-protected.com")
print(response.text)
```

#### Method 3: FlareSolverr (Proxy Service)

```python
import requests

# FlareSolverr running as service
response = requests.post(
    "http://localhost:8191/v1",
    json={
        "cmd": "request.get",
        "url": "https://cloudflare-protected.com",
        "maxTimeout": 60000
    }
)

data = response.json()
html = data['solution']['response']
cookies = data['solution']['cookies']
```

#### Method 4: Real Browser Session

```python
from playwright.sync_api import sync_playwright
import pickle

def get_cloudflare_cookies(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Must be visible
        page = browser.new_page()
        
        page.goto(url)
        
        # Wait for challenge
        page.wait_for_timeout(15000)
        
        # Check if we passed
        if "cf_clearance" in str(page.context.cookies()):
            cookies = page.context.cookies()
            browser.close()
            return cookies
        
        browser.close()
        return None
```

### Cloudflare Detection Signatures

```python
def is_cloudflare_protected(response):
    """Detect if response is Cloudflare challenge."""
    
    indicators = [
        response.status_code == 403 and 'cloudflare' in response.text.lower(),
        response.status_code == 503 and 'cloudflare' in response.text.lower(),
        'cf-ray' in response.headers,
        'cf-cache-status' in response.headers,
        '__cf_bm' in response.cookies,
        'checking your browser' in response.text.lower(),
        'cdn-cgi/challenge-platform' in response.text,
    ]
    
    return any(indicators)
```

---

## 2. Akamai Bot Manager

### How Akamai Works

Akamai uses advanced fingerprinting and behavioral analysis:

```
Request ──▶ Akamai Edge Server
                │
                ├── Sensor Data Collection
                │   ├── Browser fingerprint
                │   ├── Mouse movements
                │   ├── Keyboard patterns
                │   └── Device signals
                │
                ├── Risk Scoring
                │   └── Machine learning model
                │
                └── Action
                    ├── Allow
                    ├── Challenge
                    └── Block
```

### Akamai Sensor Script

Akamai injects a sensor script that collects:

```javascript
// Simplified - actual script is obfuscated
const sensorData = {
    // Device
    userAgent: navigator.userAgent,
    screen: [screen.width, screen.height],
    colorDepth: screen.colorDepth,
    timezone: new Date().getTimezoneOffset(),
    
    // Browser
    plugins: getPluginList(),
    canvas: getCanvasFingerprint(),
    webgl: getWebGLFingerprint(),
    
    // Behavior
    mouseMovements: [],
    keyPresses: [],
    touchEvents: [],
    scrollEvents: [],
    
    // Timing
    pageLoadTime: performance.now(),
    interactionTimes: [],
};
```

### Akamai Cookies

| Cookie | Purpose |
|--------|---------|
| `_abck` | Bot management token |
| `bm_sz` | Bot manager session |
| `ak_bmsc` | Session identifier |
| `bm_sv` | Sensor validation |

### Bypassing Akamai

#### The Challenge

Akamai is significantly harder than Cloudflare because:
- Sensor data must be generated correctly
- Behavioral patterns are analyzed
- Fingerprints must be consistent
- Cookie generation is complex

#### Method 1: Full Browser Automation

```python
from playwright.sync_api import sync_playwright

def scrape_akamai_protected(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # Akamai often detects headless
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = context.new_page()
        
        # Add human-like behavior
        page.goto(url)
        
        # Simulate mouse movements
        page.mouse.move(100, 100)
        page.wait_for_timeout(500)
        page.mouse.move(300, 200)
        page.wait_for_timeout(500)
        
        # Scroll naturally
        page.evaluate('window.scrollTo(0, 300)')
        page.wait_for_timeout(1000)
        
        content = page.content()
        browser.close()
        return content
```

#### Method 2: Akamai Solver Services

Commercial services that handle Akamai:
- **Capsolver** - API for Akamai tokens
- **Bright Data** - Proxy network with unblocking

```python
# Using a solving service (example)
def get_akamai_token(url):
    response = requests.post(
        "https://api.capsolver.com/createTask",
        json={
            "clientKey": "YOUR_KEY",
            "task": {
                "type": "AntiAkamaiTask",
                "websiteURL": url
            }
        }
    )
    # ... poll for result
```

---

## 3. PerimeterX (HUMAN)

### How PerimeterX Works

PerimeterX (now HUMAN) uses behavioral biometrics:

```
┌─────────────────────────────────────────┐
│         PerimeterX Detection            │
├─────────────────────────────────────────┤
│  Signal Collection                      │
│  ├── Device fingerprint                 │
│  ├── Network characteristics            │
│  ├── Mouse dynamics                     │
│  ├── Touch patterns                     │
│  └── Sensor timing                      │
├─────────────────────────────────────────┤
│  Machine Learning Analysis              │
│  └── Compare to known bot patterns      │
├─────────────────────────────────────────┤
│  Risk Score: 0-100                      │
│  └── Action based on threshold          │
└─────────────────────────────────────────┘
```

### PerimeterX Cookies

| Cookie | Purpose |
|--------|---------|
| `_px3` | Primary token |
| `_pxvid` | Visitor ID |
| `_pxde` | Data envelope |
| `_pxhd` | Header data |

### Detection Signs

```python
def is_perimeterx_protected(response):
    indicators = [
        '_px' in str(response.cookies),
        'perimeterx' in response.text.lower(),
        'human-challenge' in response.text.lower(),
        'px-captcha' in response.text,
        response.status_code == 403 and 'blocked' in response.text.lower(),
    ]
    return any(indicators)
```

---

## 4. DataDome

### How DataDome Works

DataDome focuses on real-time bot detection:

```
Request ──▶ DataDome Edge
                │
                ├── Real-time ML scoring
                ├── Fingerprint analysis
                ├── Behavioral patterns
                └── IP reputation
                    │
                    ▼
            ┌───────────────┐
            │   Decision    │
            ├───────────────┤
            │ Allow         │
            │ Challenge     │
            │ CAPTCHA       │
            │ Block         │
            └───────────────┘
```

### DataDome Cookies

| Cookie | Purpose |
|--------|---------|
| `datadome` | Primary session token |

### DataDome Challenge

```html
<!-- DataDome CAPTCHA page -->
<div id="datadome-captcha">
    <iframe src="https://geo.captcha-delivery.com/..."></iframe>
</div>
```

---

## 5. Imperva (Incapsula)

### How Imperva Works

Imperva uses multiple detection layers:

```
Layer 1: IP Reputation
├── Known bad IPs
├── Datacenter detection
└── Geographic anomalies

Layer 2: Browser Validation
├── JavaScript challenge
├── Cookie validation
└── Fingerprinting

Layer 3: Behavioral Analysis
├── Request patterns
├── Session analysis
└── ML classification
```

### Imperva Cookies

| Cookie | Purpose |
|--------|---------|
| `incap_ses_*` | Session |
| `visid_incap_*` | Visitor ID |
| `___utmvc` | Validation |

### Bypassing Imperva

```python
import cloudscraper

# cloudscraper handles many Imperva challenges
scraper = cloudscraper.create_scraper()
response = scraper.get("https://imperva-protected.com")
```

---

## 6. AWS WAF

### How AWS WAF Works

AWS WAF is rule-based:

```
Request ──▶ AWS WAF Rules
                │
                ├── Rate limiting
                ├── IP blacklists
                ├── SQL injection detection
                ├── XSS detection
                ├── Bot control (optional)
                └── Custom rules
```

### AWS WAF Bot Control

```
Bot Control Managed Rule Group:
├── CategoryAdvertising
├── CategoryArchiver
├── CategoryContentFetcher
├── CategoryHttpLibrary    ← python-requests!
├── CategoryLinkChecker
├── CategoryMiscellaneous
├── CategoryMonitoring
├── CategoryScrapingFramework  ← Scrapy!
├── CategorySearchEngine
├── CategorySecurity
├── CategorySeo
├── CategorySocialMedia
└── CategoryVerifiedBot
```

### Bypassing AWS WAF

AWS WAF is easier than Cloudflare/Akamai:

```python
import requests

# Usually just need good headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
}

response = requests.get(url, headers=headers)
```

---

## Detection Comparison

| WAF | Detection Level | Bypass Difficulty | Common Method |
|-----|-----------------|-------------------|---------------|
| **Cloudflare** | Medium-High | Medium | cloudscraper, FlareSolverr |
| **Akamai** | Very High | Very Hard | Full browser, services |
| **PerimeterX** | Very High | Very Hard | Full browser, services |
| **DataDome** | High | Hard | Browser automation |
| **Imperva** | Medium | Medium | cloudscraper |
| **AWS WAF** | Low-Medium | Easy | Good headers |

---

## General Bypass Strategies

### Strategy 1: Detect and Adapt

```python
def smart_request(url, session=None):
    """Detect WAF and use appropriate bypass."""
    
    session = session or requests.Session()
    response = session.get(url)
    
    if is_cloudflare_protected(response):
        return bypass_cloudflare(url)
    elif is_akamai_protected(response):
        return bypass_akamai(url)
    elif is_datadome_protected(response):
        return bypass_datadome(url)
    else:
        return response
```

### Strategy 2: Browser-First

```python
def browser_first_approach(url):
    """Use real browser, extract session for requests."""
    
    # Get authenticated session via browser
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(10000)  # Wait for challenges
        
        cookies = page.context.cookies()
        browser.close()
    
    # Use cookies with requests
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    
    return session
```

### Strategy 3: Residential Proxies

Many WAFs are less aggressive with residential IPs:

```python
def use_residential_proxy(url):
    proxy = "http://user:pass@residential.proxy.com:8080"
    
    response = requests.get(
        url,
        proxies={"http": proxy, "https": proxy},
        headers=get_browser_headers()
    )
    
    return response
```

---

## Summary

| WAF | Key Challenge | Best Bypass |
|-----|---------------|-------------|
| **Cloudflare** | JS Challenge | cloudscraper, undetected-chromedriver |
| **Akamai** | Sensor data | Full browser + behavior |
| **PerimeterX** | Behavioral | Full browser + behavior |
| **DataDome** | Real-time ML | Browser + residential proxy |
| **Imperva** | Cookie validation | cloudscraper |
| **AWS WAF** | Rule matching | Good headers |

### Key Takeaways

1. **Identify the WAF first** - Different strategies for each
2. **Start with libraries** - cloudscraper handles many cases
3. **Use real browsers** - For tough targets
4. **Add human behavior** - Mouse, scroll, timing
5. **Consider residential proxies** - Lower detection rates
6. **Use solver services** - When automation fails

---

*Next: [06_login_walls_auth_gates.md](06_login_walls_auth_gates.md) - Handling authentication barriers*
