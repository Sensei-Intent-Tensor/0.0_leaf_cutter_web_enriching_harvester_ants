# CAPTCHA Systems

> **The Most Visible Anti-Bot Measure: A Complete Guide**

CAPTCHA (Completely Automated Public Turing test to tell Computers and Humans Apart) is the most recognizable anti-bot technology. This document covers every major CAPTCHA system, how they work, and approaches to handling them.

---

## The Evolution of CAPTCHAs

```
Timeline of CAPTCHA Evolution:

1997-2003: Text Distortion Era
┌─────────────────────────────────────┐
│  "7rK9mP"  ← Distorted text         │
│  Type what you see                  │
└─────────────────────────────────────┘
Problem: OCR got good at solving these

2007-2014: reCAPTCHA v1 (Text + Audio)
┌─────────────────────────────────────┐
│  Two words from scanned books       │
│  Also helped digitize books!        │
└─────────────────────────────────────┘
Problem: ML advances defeated text recognition

2014-2018: reCAPTCHA v2 ("I'm not a robot")
┌─────────────────────────────────────┐
│  ☑ I'm not a robot                  │
│  + Image selection challenges       │
└─────────────────────────────────────┘
Problem: Click farms, behavioral analysis

2018-Present: reCAPTCHA v3 (Invisible)
┌─────────────────────────────────────┐
│  No visible challenge               │
│  Behavioral scoring (0.0 - 1.0)     │
└─────────────────────────────────────┘
Current state: Continuous arms race
```

---

## 1. reCAPTCHA (Google)

### 1.1 reCAPTCHA v2 ("I'm not a robot")

**How it works**:
```
User Action                    Google's Analysis
     │                              │
     ▼                              ▼
┌─────────────┐              ┌─────────────────────────┐
│ Click       │              │ • Mouse movement path   │
│ checkbox    │ ────────────▶│ • Click timing/position │
│             │              │ • Browser fingerprint   │
│ ☑ I'm not   │              │ • Cookie history        │
│   a robot   │              │ • IP reputation         │
└─────────────┘              │ • Previous interactions │
                             └─────────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
              Pass silently      Image challenge      Hard challenge
              (high trust)       (medium trust)       (low trust)
```

**Image challenges**:
```
┌─────────────────────────────────────────────────────────┐
│ Select all images with traffic lights                   │
│ ┌─────┬─────┬─────┐                                    │
│ │  🚦 │  🏠 │  🚗 │                                    │
│ ├─────┼─────┼─────┤                                    │
│ │  🌲 │  🚦 │  🏢 │                                    │
│ ├─────┼─────┼─────┤                                    │
│ │  🚦 │  🚶 │  🚌 │                                    │
│ └─────┴─────┴─────┘                                    │
│                                    [Verify]             │
└─────────────────────────────────────────────────────────┘
```

**Common image challenge types**:
- Traffic lights
- Crosswalks
- Bicycles
- Buses
- Fire hydrants
- Motorcycles
- Stairs
- Bridges
- Storefronts
- Chimneys

**Detection factors**:
1. **Mouse dynamics**: Speed, acceleration, path curvature
2. **Click precision**: Exact click location within checkbox
3. **Browser environment**: Canvas fingerprint, WebGL, fonts
4. **Behavioral history**: Previous Google interactions
5. **Network signals**: IP reputation, VPN detection

### 1.2 reCAPTCHA v3 (Invisible)

**How it works**:
```
Page Load                    Continuous Monitoring
    │                              │
    ▼                              ▼
┌─────────────┐              ┌─────────────────────────┐
│ reCAPTCHA   │              │ • All mouse movements   │
│ script      │ ────────────▶│ • Scroll behavior       │
│ loads       │              │ • Keystroke dynamics    │
│             │              │ • Time on page          │
│ (invisible) │              │ • Interaction patterns  │
└─────────────┘              │ • Navigation flow       │
                             └─────────────────────────┘
                                        │
                                        ▼
                             ┌─────────────────────────┐
                             │ Score: 0.0 to 1.0       │
                             │ • 0.9+ = Likely human   │
                             │ • 0.5  = Uncertain      │
                             │ • 0.1- = Likely bot     │
                             └─────────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
              Allow action       Additional verify    Block/CAPTCHA
```

**Implementation by website**:
```javascript
// Website must decide what to do with score
grecaptcha.ready(function() {
    grecaptcha.execute('SITE_KEY', {action: 'submit'})
    .then(function(token) {
        // Send token to backend
        // Backend calls Google API to get score
        // Score: 0.0 (bot) to 1.0 (human)
        
        // Website decides threshold:
        // if (score < 0.5) → show CAPTCHA or block
        // if (score >= 0.5) → allow
    });
});
```

**Key insight**: reCAPTCHA v3 doesn't block by itself—the website chooses what to do with the score.

### 1.3 reCAPTCHA Enterprise

**Advanced features**:
- Multi-factor risk analysis
- Custom risk thresholds per action
- Account defender integration
- Password leak detection
- Detailed analytics dashboard

**Pricing**: Based on API calls, typically $1-8 per 1000 assessments

---

## 2. hCaptcha

### 2.1 Overview

**Why hCaptcha exists**: 
- Privacy-focused alternative to reCAPTCHA
- Pays websites for traffic (vs. Google using it for ML training)
- GDPR-compliant by design

**Market position**:
```
CAPTCHA Market Share (Approximate):
├── reCAPTCHA: 70%
├── hCaptcha: 15%
├── Others: 15%
```

### 2.2 How It Works

```
┌─────────────────────────────────────────────────────────┐
│ Select all images containing a motorcycle              │
│ ┌─────┬─────┬─────┬─────┐                              │
│ │  🏍 │  🚗 │  🏍 │  🚲 │                              │
│ ├─────┼─────┼─────┼─────┤                              │
│ │  🚌 │  🏍 │  🚛 │  🏍 │                              │
│ └─────┴─────┴─────┴─────┘                              │
│                                    [Verify]             │
└─────────────────────────────────────────────────────────┘
```

**Challenge types**:
- Image classification (like reCAPTCHA)
- Image labeling tasks
- Object detection
- Occasionally unusual categories (helps train ML models)

### 2.3 hCaptcha Detection Methods

```
Detection Signals:
├── Browser fingerprinting
│   ├── Canvas fingerprint
│   ├── WebGL fingerprint
│   ├── Audio fingerprint
│   └── Font enumeration
├── Behavioral analysis
│   ├── Mouse movement patterns
│   ├── Challenge completion time
│   └── Selection patterns
├── Network analysis
│   ├── IP reputation
│   ├── ASN classification
│   └── VPN/proxy detection
└── Historical data
    ├── Previous solve rate
    └── Account-level signals
```

### 2.4 hCaptcha Accessibility

**Accessibility cookie**: hCaptcha offers accessibility bypass for users with disabilities.

```
To get accessibility cookie:
1. Visit https://www.hcaptcha.com/accessibility
2. Register email
3. Receive cookie that bypasses visual challenges
4. Cookie valid for limited time

Note: Abuse of accessibility features is unethical and may be illegal
```

---

## 3. Other CAPTCHA Systems

### 3.1 FunCaptcha (Arkose Labs)

**Unique approach**: Game-based challenges

```
┌─────────────────────────────────────────────────────────┐
│ Rotate the image to be right-side up                   │
│                                                         │
│              🔄 [Rotated animal image]                 │
│                                                         │
│         ◀────────────────────────▶                     │
│              Rotation slider                            │
│                                    [Verify]             │
└─────────────────────────────────────────────────────────┘
```

**Challenge types**:
- Image rotation
- Puzzle matching
- Icon matching
- 3D object manipulation

**Why it's harder**:
- Gamified challenges are less automatable
- Requires understanding of object orientation
- Multiple challenge types increase complexity

### 3.2 GeeTest

**Popular in**: China, Asia-Pacific region

**Challenge types**:
```
Slider CAPTCHA:
┌─────────────────────────────────────────────────────────┐
│ Drag the slider to complete the puzzle                 │
│                                                         │
│ [Image with missing piece]  [Puzzle piece]             │
│                                                         │
│ ────●──────────────────────────────────▶               │
│     Drag to complete                                    │
└─────────────────────────────────────────────────────────┘

Click CAPTCHA:
┌─────────────────────────────────────────────────────────┐
│ Click on: 摄 照 机                                      │
│ (Click on characters in order shown)                   │
│                                                         │
│ [Image with scattered Chinese characters]              │
└─────────────────────────────────────────────────────────┘
```

### 3.3 KeyCAPTCHA

**Approach**: Puzzle assembly

```
┌─────────────────────────────────────────────────────────┐
│ Assemble the puzzle                                     │
│                                                         │
│ [Scrambled image pieces]                               │
│                                                         │
│ Drag pieces to correct positions                       │
└─────────────────────────────────────────────────────────┘
```

### 3.4 Text-Based CAPTCHAs (Legacy)

**Still used by**: Smaller sites, legacy systems

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│     𝓢𝓶𝓧7𝓚ℜ                                            │
│                                                         │
│ Enter the text above: [____________]                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Weaknesses**:
- OCR technology has advanced significantly
- ML models can solve most text CAPTCHAs
- Audio alternatives often easier to solve

### 3.5 Audio CAPTCHAs

**Accessibility feature** for visually impaired users:

```
[🔊 Play Audio]

Audio: "Seven... three... nine... two... four"
       (with background noise)

Enter what you hear: [____________]
```

**Weakness**: Speech recognition has improved dramatically, making audio CAPTCHAs easier to solve than visual ones.

---

## 4. CAPTCHA Solving Approaches

### 4.1 Manual Solving (Yourself)

```python
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Show browser
    page = browser.new_page()
    page.goto("https://example.com/with-captcha")
    
    # Wait for CAPTCHA to appear
    page.wait_for_selector("iframe[title*='reCAPTCHA']")
    
    # Pause for manual solving
    print("Please solve the CAPTCHA manually...")
    input("Press Enter when done...")
    
    # Continue automation
    page.click("#submit")
```

**When to use**: Low volume, one-time tasks

### 4.2 CAPTCHA Solving Services

**How they work**:
```
Your Scraper                 Solving Service              Human Workers
     │                            │                            │
     │  1. Send CAPTCHA image     │                            │
     │ ─────────────────────────▶ │                            │
     │                            │  2. Route to worker        │
     │                            │ ─────────────────────────▶ │
     │                            │                            │
     │                            │  3. Solution               │
     │                            │ ◀───────────────────────── │
     │  4. Return solution        │                            │
     │ ◀───────────────────────── │                            │
     │                            │                            │
     │  Average time: 10-60 sec   │                            │
```

**Major services**:

| Service | Price (per 1000) | Speed | Accuracy |
|---------|-----------------|-------|----------|
| **2Captcha** | $2-3 | 10-60s | 95%+ |
| **Anti-Captcha** | $2-3 | 10-60s | 95%+ |
| **CapMonster** | $1-2 | 5-30s | 90%+ |
| **DeathByCaptcha** | $1-3 | 10-60s | 95%+ |
| **AZCaptcha** | $1-2 | 10-60s | 90%+ |

### 4.3 Using 2Captcha API

```python
import requests
import time

class CaptchaSolver:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://2captcha.com"
    
    def solve_recaptcha_v2(self, site_key, page_url):
        """Solve reCAPTCHA v2"""
        
        # Step 1: Submit CAPTCHA
        submit_url = f"{self.base_url}/in.php"
        payload = {
            "key": self.api_key,
            "method": "userrecaptcha",
            "googlekey": site_key,
            "pageurl": page_url,
            "json": 1
        }
        
        response = requests.post(submit_url, data=payload)
        result = response.json()
        
        if result["status"] != 1:
            raise Exception(f"Submit failed: {result}")
        
        task_id = result["request"]
        
        # Step 2: Poll for solution
        result_url = f"{self.base_url}/res.php"
        
        for _ in range(60):  # Max 60 attempts
            time.sleep(5)
            
            response = requests.get(result_url, params={
                "key": self.api_key,
                "action": "get",
                "id": task_id,
                "json": 1
            })
            
            result = response.json()
            
            if result["status"] == 1:
                return result["request"]  # The g-recaptcha-response token
            
            if result["request"] != "CAPCHA_NOT_READY":
                raise Exception(f"Solve failed: {result}")
        
        raise Exception("Timeout waiting for solution")
    
    def solve_recaptcha_v3(self, site_key, page_url, action="submit", min_score=0.7):
        """Solve reCAPTCHA v3"""
        
        submit_url = f"{self.base_url}/in.php"
        payload = {
            "key": self.api_key,
            "method": "userrecaptcha",
            "googlekey": site_key,
            "pageurl": page_url,
            "version": "v3",
            "action": action,
            "min_score": min_score,
            "json": 1
        }
        
        response = requests.post(submit_url, data=payload)
        result = response.json()
        
        if result["status"] != 1:
            raise Exception(f"Submit failed: {result}")
        
        task_id = result["request"]
        
        # Poll for solution (same as v2)
        # ... (same polling logic)
    
    def solve_hcaptcha(self, site_key, page_url):
        """Solve hCaptcha"""
        
        submit_url = f"{self.base_url}/in.php"
        payload = {
            "key": self.api_key,
            "method": "hcaptcha",
            "sitekey": site_key,
            "pageurl": page_url,
            "json": 1
        }
        
        # ... (same pattern)
    
    def solve_image_captcha(self, image_base64):
        """Solve image-based CAPTCHA"""
        
        submit_url = f"{self.base_url}/in.php"
        payload = {
            "key": self.api_key,
            "method": "base64",
            "body": image_base64,
            "json": 1
        }
        
        # ... (same pattern)

# Usage
solver = CaptchaSolver("YOUR_API_KEY")

# For reCAPTCHA v2
token = solver.solve_recaptcha_v2(
    site_key="6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
    page_url="https://example.com/page-with-captcha"
)

# Inject token into page
page.evaluate(f"""
    document.getElementById('g-recaptcha-response').value = '{token}';
""")
```

### 4.4 Using Anti-Captcha API

```python
from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless

def solve_with_anticaptcha(api_key, site_key, url):
    solver = recaptchaV2Proxyless()
    solver.set_verbose(1)
    solver.set_key(api_key)
    solver.set_website_url(url)
    solver.set_website_key(site_key)
    
    g_response = solver.solve_and_return_solution()
    
    if g_response != 0:
        return g_response
    else:
        raise Exception(f"Failed: {solver.error_code}")
```

### 4.5 ML-Based Solving (Advanced)

**For image classification CAPTCHAs**:

```python
import torch
from torchvision import transforms
from PIL import Image
import base64
from io import BytesIO

class ImageCaptchaSolver:
    def __init__(self, model_path):
        self.model = torch.load(model_path)
        self.model.eval()
        
        self.transform = transforms.Compose([
            transforms.Resize((64, 64)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], 
                               [0.229, 0.224, 0.225])
        ])
        
        self.classes = [
            "traffic_light", "crosswalk", "bicycle",
            "bus", "car", "motorcycle", "fire_hydrant",
            # ... more classes
        ]
    
    def predict(self, image_base64):
        # Decode image
        image_data = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_data))
        
        # Transform
        tensor = self.transform(image).unsqueeze(0)
        
        # Predict
        with torch.no_grad():
            output = self.model(tensor)
            _, predicted = torch.max(output, 1)
        
        return self.classes[predicted.item()]
```

**Challenges with ML solving**:
- Requires training data (hard to collect)
- CAPTCHAs evolve constantly
- High accuracy needed (>95%)
- Often more expensive than human solving

---

## 5. Extracting CAPTCHA Parameters

### 5.1 Finding reCAPTCHA Site Key

```python
from bs4 import BeautifulSoup

def find_recaptcha_sitekey(html):
    soup = BeautifulSoup(html, "html.parser")
    
    # Method 1: From data-sitekey attribute
    recaptcha_div = soup.select_one("[data-sitekey]")
    if recaptcha_div:
        return recaptcha_div["data-sitekey"]
    
    # Method 2: From script parameters
    import re
    match = re.search(r'grecaptcha\.render\([^,]+,\s*\{\s*[\'"]sitekey[\'"]\s*:\s*[\'"]([^"\']+)[\'"]', html)
    if match:
        return match.group(1)
    
    # Method 3: From iframe src
    iframe = soup.select_one("iframe[src*='recaptcha']")
    if iframe:
        src = iframe["src"]
        match = re.search(r'k=([^&]+)', src)
        if match:
            return match.group(1)
    
    return None

# Usage
html = requests.get(url).text
site_key = find_recaptcha_sitekey(html)
```

### 5.2 Finding hCaptcha Site Key

```python
def find_hcaptcha_sitekey(html):
    soup = BeautifulSoup(html, "html.parser")
    
    # Method 1: data-sitekey attribute
    hcaptcha_div = soup.select_one("[data-sitekey]")
    if hcaptcha_div:
        return hcaptcha_div["data-sitekey"]
    
    # Method 2: From script
    import re
    match = re.search(r'data-sitekey=["\']([^"\']+)["\']', html)
    if match:
        return match.group(1)
    
    return None
```

### 5.3 Complete CAPTCHA Integration

```python
from playwright.sync_api import sync_playwright

class CaptchaEnabledScraper:
    def __init__(self, captcha_api_key):
        self.solver = CaptchaSolver(captcha_api_key)
    
    def scrape_with_captcha(self, url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(url)
            
            # Check for CAPTCHA
            if self.has_recaptcha(page):
                self.solve_recaptcha(page, url)
            elif self.has_hcaptcha(page):
                self.solve_hcaptcha(page, url)
            
            # Continue with scraping
            return page.content()
    
    def has_recaptcha(self, page):
        return page.query_selector("[data-sitekey], iframe[src*='recaptcha']") is not None
    
    def has_hcaptcha(self, page):
        return page.query_selector("iframe[src*='hcaptcha']") is not None
    
    def solve_recaptcha(self, page, url):
        # Get site key
        site_key = page.evaluate("""
            () => {
                const el = document.querySelector('[data-sitekey]');
                return el ? el.getAttribute('data-sitekey') : null;
            }
        """)
        
        if not site_key:
            raise Exception("Could not find reCAPTCHA site key")
        
        # Solve using service
        token = self.solver.solve_recaptcha_v2(site_key, url)
        
        # Inject solution
        page.evaluate(f"""
            (token) => {{
                document.getElementById('g-recaptcha-response').value = token;
                // Also set in any hidden textarea
                const textareas = document.querySelectorAll('textarea[name="g-recaptcha-response"]');
                textareas.forEach(ta => ta.value = token);
            }}
        """, token)
        
        # Trigger callback if exists
        page.evaluate("""
            () => {
                if (typeof ___grecaptcha_cfg !== 'undefined') {
                    const clients = ___grecaptcha_cfg.clients;
                    for (const key in clients) {
                        const client = clients[key];
                        if (client.callback) {
                            client.callback(document.getElementById('g-recaptcha-response').value);
                        }
                    }
                }
            }
        """)
```

---

## 6. Avoiding CAPTCHAs

### 6.1 Behavioral Strategies

```python
import random
import time

class HumanLikeBehavior:
    """Simulate human-like behavior to avoid triggering CAPTCHAs"""
    
    @staticmethod
    def random_delay(min_sec=1, max_sec=3):
        """Random delay between actions"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    @staticmethod
    def human_like_mouse_move(page, target_selector):
        """Move mouse in human-like path to target"""
        # Get target position
        target = page.query_selector(target_selector)
        box = target.bounding_box()
        target_x = box["x"] + box["width"] / 2
        target_y = box["y"] + box["height"] / 2
        
        # Current position (random start)
        current_x = random.randint(0, 500)
        current_y = random.randint(0, 500)
        
        # Generate curved path
        steps = random.randint(10, 25)
        for i in range(steps):
            progress = i / steps
            # Add slight curve
            noise_x = random.uniform(-10, 10)
            noise_y = random.uniform(-10, 10)
            
            x = current_x + (target_x - current_x) * progress + noise_x
            y = current_y + (target_y - current_y) * progress + noise_y
            
            page.mouse.move(x, y)
            time.sleep(random.uniform(0.01, 0.05))
    
    @staticmethod
    def human_like_scroll(page):
        """Scroll like a human would"""
        # Scroll down in chunks
        for _ in range(random.randint(2, 5)):
            scroll_amount = random.randint(200, 500)
            page.mouse.wheel(0, scroll_amount)
            time.sleep(random.uniform(0.5, 1.5))
        
        # Maybe scroll back up a bit
        if random.random() > 0.7:
            page.mouse.wheel(0, -random.randint(100, 300))
```

### 6.2 Session Management

```python
class SessionManager:
    """Maintain good session reputation"""
    
    def __init__(self):
        self.session = requests.Session()
        self.request_count = 0
        self.last_request_time = 0
    
    def get(self, url, **kwargs):
        # Enforce minimum delay
        elapsed = time.time() - self.last_request_time
        if elapsed < 2:
            time.sleep(2 - elapsed + random.uniform(0, 1))
        
        # Add realistic headers
        self.session.headers.update({
            "User-Agent": self.get_rotating_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })
        
        response = self.session.get(url, **kwargs)
        
        self.request_count += 1
        self.last_request_time = time.time()
        
        # Rotate session periodically
        if self.request_count > 50:
            self.refresh_session()
        
        return response
    
    def refresh_session(self):
        """Get fresh session with new cookies"""
        self.session = requests.Session()
        self.request_count = 0
        # Visit homepage to get cookies
        self.session.get("https://example.com")
```

### 6.3 Cookie Strategy

```python
def build_cookie_reputation(page, base_url):
    """Build up cookie reputation before scraping"""
    
    # Visit homepage
    page.goto(base_url)
    time.sleep(random.uniform(2, 4))
    
    # Click around naturally
    links = page.query_selector_all("a[href^='/']")
    for link in random.sample(links, min(3, len(links))):
        link.click()
        time.sleep(random.uniform(1, 3))
        page.go_back()
        time.sleep(random.uniform(0.5, 1.5))
    
    # Accept cookies if prompted
    cookie_buttons = [
        "button:has-text('Accept')",
        "button:has-text('I agree')",
        "#cookie-accept",
        ".cookie-consent-accept"
    ]
    for selector in cookie_buttons:
        button = page.query_selector(selector)
        if button:
            button.click()
            break
    
    # Now cookies have some history
```

---

## 7. CAPTCHA Detection and Response

### 7.1 Detecting CAPTCHA Presence

```python
def detect_captcha(page):
    """Detect various CAPTCHA types on page"""
    
    captcha_indicators = {
        "recaptcha_v2": [
            "iframe[src*='recaptcha/api2']",
            "[data-sitekey]",
            ".g-recaptcha"
        ],
        "recaptcha_v3": [
            "script[src*='recaptcha/api.js?render=']",
        ],
        "hcaptcha": [
            "iframe[src*='hcaptcha.com']",
            ".h-captcha"
        ],
        "funcaptcha": [
            "iframe[src*='funcaptcha.com']",
            "#FunCaptcha"
        ],
        "text_captcha": [
            "img[src*='captcha']",
            "input[name*='captcha']"
        ]
    }
    
    detected = []
    for captcha_type, selectors in captcha_indicators.items():
        for selector in selectors:
            if page.query_selector(selector):
                detected.append(captcha_type)
                break
    
    return detected

def has_captcha_challenge(page):
    """Check if CAPTCHA challenge is currently displayed"""
    
    # reCAPTCHA challenge iframe
    challenge = page.query_selector("iframe[src*='recaptcha/api2/bframe']")
    if challenge:
        box = challenge.bounding_box()
        if box and box["height"] > 0:
            return True
    
    # hCaptcha challenge
    challenge = page.query_selector("iframe[src*='hcaptcha.com/captcha']")
    if challenge:
        box = challenge.bounding_box()
        if box and box["height"] > 100:
            return True
    
    return False
```

### 7.2 Automatic CAPTCHA Response

```python
class AdaptiveScraper:
    """Scraper that adapts to CAPTCHA challenges"""
    
    def __init__(self, captcha_solver):
        self.solver = captcha_solver
        self.captcha_count = 0
        self.base_delay = 2
    
    def scrape(self, url):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # Apply stealth
            self.apply_stealth(page)
            
            page.goto(url)
            
            # Check for CAPTCHA
            if self.handle_captcha_if_present(page, url):
                self.captcha_count += 1
                # Increase delay if seeing many CAPTCHAs
                self.base_delay = min(10, self.base_delay * 1.5)
            
            return page.content()
    
    def handle_captcha_if_present(self, page, url):
        """Handle CAPTCHA if detected"""
        detected = detect_captcha(page)
        
        if not detected:
            return False
        
        if "recaptcha_v2" in detected:
            self.solve_recaptcha_v2(page, url)
        elif "hcaptcha" in detected:
            self.solve_hcaptcha(page, url)
        # ... handle other types
        
        return True
    
    def apply_stealth(self, page):
        """Apply stealth techniques"""
        page.add_init_script("""
            // Hide webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false
            });
            
            // More stealth...
        """)
```

---

## 8. Best Practices

### 8.1 CAPTCHA Handling Strategy

```
Decision Tree:

1. Can you avoid the CAPTCHA entirely?
   ├── Yes → Use stealth, rate limiting, session management
   └── No → Continue to 2

2. Is there an API or official data source?
   ├── Yes → Use that instead
   └── No → Continue to 3

3. Is the data worth the CAPTCHA cost?
   ├── No → Consider if scraping is worth it
   └── Yes → Continue to 4

4. Choose solving method:
   ├── Low volume → Manual solving
   ├── Medium volume → Solving service (2Captcha, etc.)
   └── High volume → Custom ML + solving service backup
```

### 8.2 Cost Optimization

```python
class CostOptimizedSolver:
    """Optimize CAPTCHA solving costs"""
    
    def __init__(self, api_key):
        self.solver = CaptchaSolver(api_key)
        self.solve_count = 0
        self.cost_per_solve = 0.003  # ~$3 per 1000
    
    def solve_if_needed(self, page, url):
        """Only solve if truly necessary"""
        
        # First, try to avoid CAPTCHA
        if not has_captcha_challenge(page):
            return False
        
        # Try refreshing first (sometimes clears CAPTCHA)
        page.reload()
        time.sleep(2)
        
        if not has_captcha_challenge(page):
            return False
        
        # Try waiting (v3 might pass after behavioral analysis)
        time.sleep(5)
        if not has_captcha_challenge(page):
            return False
        
        # Must solve
        self.solve_count += 1
        print(f"Solving CAPTCHA #{self.solve_count}, cost so far: ${self.solve_count * self.cost_per_solve:.2f}")
        
        # ... solve logic
        return True
```

---

## 9. Summary

### CAPTCHA Types Quick Reference

| Type | Provider | Challenge | Difficulty |
|------|----------|-----------|------------|
| reCAPTCHA v2 | Google | Checkbox + Images | Medium |
| reCAPTCHA v3 | Google | Invisible scoring | Medium-High |
| hCaptcha | Intuition Machines | Images | Medium |
| FunCaptcha | Arkose Labs | Games | High |
| GeeTest | GeeTest | Slider/Click | Medium |
| Text CAPTCHA | Various | OCR | Low |

### Solving Options

| Method | Cost | Speed | Best For |
|--------|------|-------|----------|
| Manual | Free | Slow | One-off tasks |
| 2Captcha | $2-3/1K | 10-60s | Most use cases |
| Anti-Captcha | $2-3/1K | 10-60s | Most use cases |
| CapMonster | $1-2/1K | 5-30s | Budget option |
| Custom ML | High upfront | Fast | Very high volume |

### Key Principles

1. **Avoidance first**: Better to avoid than solve
2. **Stealth matters**: Good behavior reduces CAPTCHAs
3. **Cost awareness**: Each solve costs money
4. **Adaptivity**: Adjust strategy based on CAPTCHA frequency
5. **Ethics**: Don't abuse accessibility features

---

*Next: [03_bot_detection_fingerprinting.md](03_bot_detection_fingerprinting.md) - How sites identify bots beyond CAPTCHAs*
