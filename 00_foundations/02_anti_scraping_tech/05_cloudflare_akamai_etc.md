# Cloudflare, Akamai & Enterprise Protection Services

> **Understanding the Gatekeepers of the Modern Web**

The majority of high-value websites use enterprise anti-bot services. This document covers the major players, how they work, and strategies for working with (not against) them.

---

## The Protection Landscape

```
Website Protection Tiers:

Tier 1: No Protection
├── Direct access
├── Basic rate limiting maybe
└── Easy to scrape

Tier 2: Basic CDN Protection
├── Cloudflare Free/Pro
├── Basic WAF rules
└── Moderate difficulty

Tier 3: Advanced Bot Management
├── Cloudflare Bot Management
├── Akamai Bot Manager
├── PerimeterX / HUMAN
└── High difficulty

Tier 4: Enterprise Custom
├── Multiple layers
├── Custom ML models
├── Legal team backup
└── Extreme difficulty
```

---

## 1. Cloudflare

### 1.1 Cloudflare Protection Tiers

```
Cloudflare Product Hierarchy:

Free Plan:
├── Basic DDoS protection
├── Simple WAF rules
├── Browser Integrity Check
└── Can be bypassed easily

Pro Plan ($20/month):
├── Advanced WAF
├── More rule customization
├── Challenge pages
└── Moderate protection

Business Plan ($200/month):
├── Rate limiting
├── Bot scores
├── Custom rules
└── Stronger protection

Enterprise:
├── Bot Management ($$$)
├── ML-based detection
├── Behavioral analysis
└── Most difficult to bypass
```

### 1.2 How Cloudflare Works

```
Request Flow:

User/Bot                    Cloudflare Edge              Origin Server
    │                            │                            │
    │  1. Request                │                            │
    │ ─────────────────────────▶ │                            │
    │                            │                            │
    │                      ┌─────┴─────┐                      │
    │                      │ Analysis  │                      │
    │                      │ • IP rep  │                      │
    │                      │ • Headers │                      │
    │                      │ • JS check│                      │
    │                      │ • Behavior│                      │
    │                      └─────┬─────┘                      │
    │                            │                            │
    │  2a. Pass ─────────────────┼────────────────────────▶   │
    │                            │                            │
    │  2b. Challenge             │                            │
    │ ◀───────────────────────── │                            │
    │                            │                            │
    │  2c. Block (403)           │                            │
    │ ◀───────────────────────── │                            │
```

### 1.3 Cloudflare Challenge Types

#### JavaScript Challenge (5-Second Page)

```html
<!-- What you see -->
<!DOCTYPE html>
<html>
<head>
    <title>Just a moment...</title>
</head>
<body>
    <div class="main-wrapper">
        <h1>Checking your browser before accessing example.com</h1>
        <p>This process is automatic. Your browser will redirect shortly.</p>
        <div id="challenge-running">Please wait...</div>
    </div>
    <script>
        // Obfuscated JavaScript challenge
        // Must execute to get __cf_bm cookie
    </script>
</body>
</html>
```

#### Managed Challenge (Turnstile)

```html
<!-- Cloudflare Turnstile widget -->
<div class="cf-turnstile" data-sitekey="0x4AAAAAAAA..."></div>

<!-- Results in a token that must be submitted -->
```

#### Interactive Challenge (CAPTCHA)

Only shown when suspicion is high—requires human interaction.

### 1.4 Cloudflare Cookies

| Cookie | Purpose | Lifetime |
|--------|---------|----------|
| `__cf_bm` | Bot management | 30 minutes |
| `cf_clearance` | Challenge passed | Variable |
| `__cflb` | Load balancing | Session |
| `__cfruid` | Rate limiting | Session |

### 1.5 Bypassing Cloudflare

#### Method 1: Unflared (Bypass via Origin)

Sometimes the origin server is accessible directly:

```python
import dns.resolver

def find_origin_ip(domain):
    """Try to find origin server IP."""
    
    # Check historical DNS records
    # Check SSL certificates
    # Check related subdomains
    
    subdomains = ['mail', 'ftp', 'direct', 'origin', 'www2']
    
    for sub in subdomains:
        try:
            answers = dns.resolver.resolve(f"{sub}.{domain}", 'A')
            for answer in answers:
                ip = str(answer)
                # Check if this IP is NOT Cloudflare
                # Cloudflare IPs: 104.16.0.0/12, 172.64.0.0/13, etc.
                if not is_cloudflare_ip(ip):
                    return ip
        except:
            continue
    
    return None

# If origin found, request directly
origin_ip = find_origin_ip("example.com")
if origin_ip:
    response = requests.get(
        f"http://{origin_ip}/page",
        headers={"Host": "example.com"}
    )
```

**Note**: This is increasingly rare as most sites properly configure Cloudflare to block non-Cloudflare requests.

#### Method 2: FlareSolverr

Docker-based Cloudflare bypass:

```python
import requests

FLARESOLVERR_URL = "http://localhost:8191/v1"

def solve_cloudflare(url):
    payload = {
        "cmd": "request.get",
        "url": url,
        "maxTimeout": 60000
    }
    
    response = requests.post(FLARESOLVERR_URL, json=payload)
    result = response.json()
    
    if result["status"] == "ok":
        return {
            "html": result["solution"]["response"],
            "cookies": result["solution"]["cookies"],
            "user_agent": result["solution"]["userAgent"]
        }
    else:
        raise Exception(f"FlareSolverr failed: {result}")

# Usage
solution = solve_cloudflare("https://cloudflare-protected-site.com")
print(solution["html"])
```

#### Method 3: Browser Automation with Stealth

```python
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import time

def bypass_cloudflare(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Visible helps
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        page = context.new_page()
        stealth_sync(page)
        
        # Go to page
        page.goto(url)
        
        # Wait for Cloudflare challenge to complete
        for _ in range(30):
            if "Just a moment" not in page.content():
                break
            time.sleep(1)
        
        # Extra wait for any redirects
        page.wait_for_load_state("networkidle")
        
        # Get cookies for future requests
        cookies = context.cookies()
        cf_clearance = next(
            (c for c in cookies if c["name"] == "cf_clearance"),
            None
        )
        
        html = page.content()
        browser.close()
        
        return html, cookies

# Use obtained cookies with requests
html, cookies = bypass_cloudflare("https://protected-site.com")

# Convert to requests format
session = requests.Session()
for cookie in cookies:
    session.cookies.set(cookie["name"], cookie["value"], domain=cookie["domain"])
```

#### Method 4: Residential Proxies

Cloudflare is more lenient with residential IPs:

```python
proxy = "http://user:pass@residential-proxy.com:8080"

response = requests.get(
    url,
    proxies={"http": proxy, "https": proxy},
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
        # Include other realistic headers
    }
)
```

### 1.6 Cloudflare Detection Signals

```python
def detect_cloudflare(response):
    """Detect if site is behind Cloudflare."""
    
    signals = {
        "cf_ray_header": "CF-RAY" in response.headers,
        "cf_cache_status": "CF-Cache-Status" in response.headers,
        "server_cloudflare": response.headers.get("Server") == "cloudflare",
        "challenge_page": "Just a moment" in response.text,
        "turnstile": "challenges.cloudflare.com" in response.text,
        "cf_error": "__cf_chl_opt" in response.text,
    }
    
    return {
        "is_cloudflare": any(signals.values()),
        "signals": signals
    }
```

---

## 2. Akamai

### 2.1 Akamai Bot Manager

```
Akamai Detection Layers:

Layer 1: Edge Detection
├── IP reputation
├── Request rate
├── Geographic anomalies
└── Known bot signatures

Layer 2: Client-Side Analysis
├── JavaScript execution
├── Browser fingerprinting
├── Cookie generation
└── Sensor data collection

Layer 3: Behavioral Analysis
├── Navigation patterns
├── Session behavior
├── Anomaly detection
└── ML classification
```

### 2.2 Akamai Sensor Data

Akamai collects extensive client data via JavaScript:

```javascript
// Simplified example of what Akamai collects
const sensorData = {
    // Device fingerprint
    screen: `${screen.width}x${screen.height}`,
    colorDepth: screen.colorDepth,
    timezone: new Date().getTimezoneOffset(),
    
    // Browser fingerprint
    userAgent: navigator.userAgent,
    language: navigator.language,
    platform: navigator.platform,
    plugins: Array.from(navigator.plugins).map(p => p.name),
    
    // Interaction data
    mouseMovements: [...],  // All mouse events
    keystrokes: [...],       // Timing data
    touchEvents: [...],      // Mobile interactions
    scrollEvents: [...],     // Scroll patterns
    
    // Timing
    loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
    
    // Canvas/WebGL fingerprint
    canvasHash: "...",
    webglRenderer: "...",
};

// This data is encrypted and sent as a cookie or POST parameter
// Often named "_abck" or "bm_sz"
```

### 2.3 Akamai Cookies

| Cookie | Purpose |
|--------|---------|
| `_abck` | Main bot detection cookie (encrypted sensor data) |
| `bm_sz` | Bot manager size/session |
| `bm_sv` | Bot manager session validation |
| `ak_bmsc` | Bot manager session cookie |
| `bm_mi` | Bot manager market intelligence |

### 2.4 Bypassing Akamai

Akamai is significantly harder than Cloudflare:

#### Approach 1: Full Browser Automation

```python
from playwright.sync_api import sync_playwright
import time

def bypass_akamai(url):
    with sync_playwright() as p:
        # Must use non-headless for Akamai
        browser = p.chromium.launch(headless=False)
        
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        page = context.new_page()
        
        # Add extensive stealth
        page.add_init_script("""
            // Remove automation indicators
            Object.defineProperty(navigator, 'webdriver', {get: () => false});
            
            // Add chrome object
            window.chrome = { runtime: {} };
            
            // Fix plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)
        
        page.goto(url)
        
        # Simulate human behavior to generate valid sensor data
        simulate_human_behavior(page)
        
        # Wait for Akamai to validate
        time.sleep(5)
        
        # Check for valid _abck cookie
        cookies = context.cookies()
        abck = next((c for c in cookies if c["name"] == "_abck"), None)
        
        if abck and is_valid_abck(abck["value"]):
            return page.content(), cookies
        else:
            raise Exception("Failed to bypass Akamai")

def simulate_human_behavior(page):
    """Generate sensor data that looks human."""
    
    # Mouse movements
    for _ in range(20):
        x = random.randint(100, 1800)
        y = random.randint(100, 900)
        page.mouse.move(x, y)
        time.sleep(random.uniform(0.05, 0.15))
    
    # Scroll
    page.mouse.wheel(0, random.randint(100, 500))
    time.sleep(random.uniform(0.5, 1))
    
    # Click somewhere safe
    page.mouse.click(500, 500)
```

#### Approach 2: Specialized Services

Some services specialize in Akamai bypass:

```python
# Using a specialized API service
response = requests.post("https://bypass-service.com/api/akamai", json={
    "url": "https://akamai-protected-site.com/page",
    "session_id": "your_session"
})

result = response.json()
cookies = result["cookies"]  # Valid _abck cookie
```

---

## 3. PerimeterX (HUMAN)

### 3.1 PerimeterX Detection

```
PerimeterX Layers:

1. Request Analysis
   ├── Headers validation
   ├── TLS fingerprint
   └── IP reputation

2. Browser Fingerprinting
   ├── Canvas fingerprint
   ├── WebGL fingerprint
   ├── Audio fingerprint
   └── Font enumeration

3. Behavioral Analysis
   ├── Mouse dynamics
   ├── Keyboard patterns
   ├── Touch gestures
   └── Scroll behavior

4. Network Analysis
   ├── Request timing
   ├── Resource loading
   └── Connection patterns
```

### 3.2 PerimeterX Cookies

| Cookie | Purpose |
|--------|---------|
| `_px3` | Main detection cookie |
| `_pxvid` | Visitor ID |
| `_pxff_*` | Feature flags |
| `_pxhd` | Detection data |

### 3.3 PerimeterX Challenge

```html
<!-- PerimeterX block page -->
<html>
<head>
    <title>Access Denied</title>
</head>
<body>
    <div id="px-captcha">
        <!-- Press and hold CAPTCHA -->
    </div>
    <script src="//captcha.px-cdn.net/..."></script>
</body>
</html>
```

The "press and hold" CAPTCHA is unique to PerimeterX and requires sustained mouse pressure.

---

## 4. DataDome

### 4.1 DataDome Detection

DataDome focuses heavily on:
- Device fingerprinting
- Behavioral analysis
- ML-based classification

### 4.2 DataDome Cookies

| Cookie | Purpose |
|--------|---------|
| `datadome` | Main session cookie |
| `dd_*` | Various tracking cookies |

### 4.3 DataDome Response

```
HTTP/1.1 403 Forbidden
X-DataDome: blocked
X-DataDome-Cid: ...

{
    "url": "https://geo.captcha-delivery.com/captcha/...",
    "cid": "...",
}
```

---

## 5. Kasada

### 5.1 How Kasada Works

Kasada uses a unique approach with client-side proof-of-work:

```javascript
// Kasada requires solving computational challenges
// The browser must compute a "proof of work" that takes time

// This makes it expensive for bots to operate at scale
// Each request requires computational resources
```

### 5.2 Kasada Detection

- JavaScript execution required
- Proof-of-work computation
- Timing analysis
- Device fingerprinting

### 5.3 Kasada Indicators

```python
def detect_kasada(response):
    return {
        "x_kpsdk": "X-KPSDK-CT" in response.headers,
        "ips_js": "/ips.js" in response.text,
        "kpsdk": "_kpsdk" in response.text,
    }
```

---

## 6. Detection Service Identification

### 6.1 Identify Protection Service

```python
def identify_protection(response, url):
    """Identify which protection service is being used."""
    
    # Check headers
    headers = response.headers
    
    # Cloudflare
    if headers.get("Server") == "cloudflare" or "CF-RAY" in headers:
        return "cloudflare"
    
    # Akamai
    if "X-Akamai-Transformed" in headers or "_abck" in response.text:
        return "akamai"
    
    # PerimeterX
    if "_px3" in str(response.cookies) or "px-cdn.net" in response.text:
        return "perimeterx"
    
    # DataDome
    if "datadome" in str(response.cookies) or "X-DataDome" in headers:
        return "datadome"
    
    # Kasada
    if "X-KPSDK" in str(headers) or "/ips.js" in response.text:
        return "kasada"
    
    # Imperva/Incapsula
    if "incap_ses" in str(response.cookies) or "visid_incap" in str(response.cookies):
        return "imperva"
    
    # Shape Security (F5)
    if "_imp_apg_r" in str(response.cookies):
        return "shape"
    
    return "unknown"
```

### 6.2 Comprehensive Check

```python
def analyze_protection(url):
    """Comprehensive protection analysis."""
    
    session = requests.Session()
    
    # First request
    response = session.get(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    
    analysis = {
        "url": url,
        "status_code": response.status_code,
        "protection": identify_protection(response, url),
        "cookies": list(session.cookies.keys()),
        "challenge_detected": False,
        "headers": dict(response.headers)
    }
    
    # Check for challenge pages
    challenge_indicators = [
        "Just a moment",  # Cloudflare
        "Checking your browser",  # Generic
        "Access Denied",  # Various
        "Please verify",  # Various
        "captcha",  # Any CAPTCHA
    ]
    
    for indicator in challenge_indicators:
        if indicator.lower() in response.text.lower():
            analysis["challenge_detected"] = True
            analysis["challenge_type"] = indicator
            break
    
    return analysis
```

---

## 7. General Bypass Strategies

### 7.1 Strategy Matrix

| Protection | Difficulty | Best Approach |
|------------|------------|---------------|
| Cloudflare Free | Easy | Headers + delays |
| Cloudflare Pro | Medium | Browser + stealth |
| Cloudflare Enterprise | Hard | Residential proxies + browser |
| Akamai | Very Hard | Full browser + behavior simulation |
| PerimeterX | Very Hard | Specialized services |
| DataDome | Hard | Browser + behavior |
| Kasada | Very Hard | Browser + wait for PoW |

### 7.2 Universal Best Practices

```python
class ProtectedSiteScraper:
    """General approach for protected sites."""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
    
    def setup(self):
        from playwright.sync_api import sync_playwright
        self.playwright = sync_playwright().start()
        
        # Use visible browser for best results
        self.browser = self.playwright.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
            ]
        )
    
    def create_context(self):
        return self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/New_York",
        )
    
    def scrape(self, url):
        context = self.create_context()
        page = context.new_page()
        
        # Apply stealth
        self.apply_stealth(page)
        
        # Navigate
        page.goto(url)
        
        # Wait for protection to clear
        self.wait_for_protection(page)
        
        # Simulate human behavior
        self.simulate_human(page)
        
        # Get content
        content = page.content()
        cookies = context.cookies()
        
        page.close()
        context.close()
        
        return content, cookies
    
    def apply_stealth(self, page):
        page.add_init_script("""
            // Comprehensive stealth
            Object.defineProperty(navigator, 'webdriver', {get: () => false});
            
            window.chrome = {
                runtime: {},
                app: { isInstalled: false }
            };
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    { name: 'Chrome PDF Plugin' },
                    { name: 'Chrome PDF Viewer' },
                    { name: 'Native Client' }
                ]
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
    
    def wait_for_protection(self, page, timeout=30):
        """Wait for protection challenges to complete."""
        import time
        
        challenge_indicators = [
            "Just a moment",
            "Checking your browser",
            "Access Denied",
            "Please wait",
        ]
        
        start = time.time()
        while time.time() - start < timeout:
            content = page.content()
            
            # Check if still on challenge
            if not any(ind in content for ind in challenge_indicators):
                return True
            
            time.sleep(1)
        
        return False
    
    def simulate_human(self, page):
        """Simulate human behavior."""
        import random
        import time
        
        # Random mouse movements
        for _ in range(5):
            x = random.randint(100, 1800)
            y = random.randint(100, 900)
            page.mouse.move(x, y)
            time.sleep(random.uniform(0.1, 0.3))
        
        # Scroll
        page.mouse.wheel(0, random.randint(200, 500))
        time.sleep(random.uniform(0.5, 1))
```

### 7.3 Fallback Strategies

```python
def scrape_with_fallbacks(url):
    """Try multiple approaches in order of preference."""
    
    strategies = [
        ("requests_simple", try_simple_requests),
        ("requests_stealth", try_stealth_requests),
        ("playwright_headless", try_playwright_headless),
        ("playwright_visible", try_playwright_visible),
        ("flaresolverr", try_flaresolverr),
        ("residential_proxy", try_residential_proxy),
    ]
    
    for name, strategy in strategies:
        try:
            result = strategy(url)
            if result and len(result) > 1000:  # Valid response
                print(f"Success with: {name}")
                return result
        except Exception as e:
            print(f"Failed with {name}: {e}")
            continue
    
    raise Exception("All strategies failed")
```

---

## 8. Summary

### Protection Difficulty Ranking

```
Easiest ──────────────────────────────────────────────▶ Hardest

Cloudflare    Cloudflare    DataDome    Akamai    Kasada
Free          Pro/Business              Bot Mgr   

No protection  Basic WAF    Advanced    Enterprise
                            Bot Mgmt    Custom
```

### Quick Reference

| Service | Key Cookie | JS Required | Bypass Difficulty |
|---------|------------|-------------|-------------------|
| Cloudflare | cf_clearance | Yes | Medium |
| Akamai | _abck | Yes | Very Hard |
| PerimeterX | _px3 | Yes | Very Hard |
| DataDome | datadome | Yes | Hard |
| Kasada | - | Yes (PoW) | Very Hard |
| Imperva | incap_ses | Yes | Medium |

### Key Principles

1. **Identify the protection first** - Different services need different approaches
2. **Start with simplest solution** - Don't over-engineer
3. **Browser automation is often necessary** - For modern protections
4. **Residential proxies help** - Lower suspicion scores
5. **Behavior simulation matters** - For advanced protections
6. **Maintain valid cookies** - Reuse sessions when possible
7. **Have fallback strategies** - Protections change

---

*Next: [06_login_walls_auth_gates.md](06_login_walls_auth_gates.md) - Handling authentication barriers*
