# CAPTCHA Systems

> **The Human Verification Challenge**

CAPTCHAs are the most visible anti-bot measure. Understanding how they work—and their limitations—is essential for any serious scraper.

---

## What is CAPTCHA?

**C**ompletely **A**utomated **P**ublic **T**uring test to tell **C**omputers and **H**umans **A**part

The goal: Present a challenge that's easy for humans but hard for machines.

```
User/Bot arrives
      │
      ▼
┌─────────────┐
│  CAPTCHA    │
│  Challenge  │
└─────────────┘
      │
      ├── Human solves easily ──▶ Access granted
      │
      └── Bot fails ──▶ Access denied
```

---

## Evolution of CAPTCHAs

### Generation 1: Text CAPTCHAs (2000s)

```
┌─────────────────────────┐
│  ╔═╗ ╦═╗ ═══ ╦ ═╗      │
│  ╠═╣ ╠═╝     ║  ║      │
│  ╩ ╩ ╩       ╩ ═╝      │
│                        │
│  Type the text: [____] │
└─────────────────────────┘
```

- Distorted text images
- Increasingly complex as OCR improved
- Eventually too hard for humans too
- Largely obsolete now

### Generation 2: Image CAPTCHAs (2010s)

```
┌─────────────────────────────────┐
│  Select all images with:       │
│  🚦 TRAFFIC LIGHTS             │
│                                │
│  ┌───┬───┬───┐                │
│  │ 🚗│ 🚦│ 🌳│                │
│  ├───┼───┼───┤                │
│  │ 🏠│ 🚦│ 🚶│                │
│  ├───┼───┼───┤                │
│  │ 🚦│ 🚌│ 🏢│                │
│  └───┴───┴───┘                │
│           [Verify]            │
└─────────────────────────────────┘
```

- Google's reCAPTCHA v2
- Requires visual understanding
- Trains Google's self-driving car AI
- Still in wide use

### Generation 3: Invisible/Behavioral (2018+)

```
User browses page
      │
      ▼
┌─────────────────────────┐
│  Background Analysis    │
│  ├── Mouse movements    │
│  ├── Scroll patterns    │
│  ├── Click behavior     │
│  ├── Typing rhythm      │
│  └── Browser signals    │
└─────────────────────────┘
      │
      ├── Looks human ──▶ No challenge
      │
      └── Suspicious ──▶ Show CAPTCHA
```

- reCAPTCHA v3, hCaptcha Enterprise
- Scores user behavior (0.0 - 1.0)
- Most users never see a challenge
- Much harder to bypass

---

## Major CAPTCHA Systems

### Google reCAPTCHA

**Market share: ~80%**

#### reCAPTCHA v2 ("I'm not a robot")

```html
<div class="g-recaptcha" data-sitekey="SITE_KEY"></div>
```

How it works:
1. User clicks checkbox
2. Google analyzes cookies, browsing history, behavior
3. If suspicious, shows image challenge
4. Returns token for server verification

```python
# Server-side verification
response = requests.post(
    "https://www.google.com/recaptcha/api/siteverify",
    data={
        "secret": "YOUR_SECRET_KEY",
        "response": captcha_token,
        "remoteip": user_ip
    }
)
result = response.json()
# {"success": true, "challenge_ts": "...", "hostname": "..."}
```

#### reCAPTCHA v2 Invisible

Same as v2, but checkbox is hidden. Challenge appears only if needed.

```html
<button class="g-recaptcha" data-sitekey="SITE_KEY" 
        data-callback="onSubmit">Submit</button>
```

#### reCAPTCHA v3 (Score-based)

```javascript
grecaptcha.execute('SITE_KEY', {action: 'login'})
  .then(function(token) {
    // Send token to server
  });
```

Returns a score (0.0 = likely bot, 1.0 = likely human):

| Score | Interpretation | Action |
|-------|----------------|--------|
| 0.9+ | Definitely human | Allow |
| 0.7-0.9 | Probably human | Allow |
| 0.3-0.7 | Uncertain | Maybe challenge |
| 0.1-0.3 | Probably bot | Block or challenge |
| <0.1 | Definitely bot | Block |

#### reCAPTCHA Enterprise

- Advanced ML models
- More customization
- Fraud detection features
- Enterprise pricing

---

### hCaptcha

**Privacy-focused alternative to reCAPTCHA**

```html
<div class="h-captcha" data-sitekey="SITE_KEY"></div>
```

Why sites use it:
- Doesn't feed Google's data machine
- Pays website owners (reverse of reCAPTCHA)
- Similar effectiveness

Types:
- **hCaptcha Free** - Basic image challenges
- **hCaptcha Pro** - Behavioral analysis
- **hCaptcha Enterprise** - Advanced detection

---

### Other Systems

| System | Used By | Notes |
|--------|---------|-------|
| **Arkose Labs (FunCaptcha)** | Microsoft, EA, GitHub | 3D puzzles |
| **Cloudflare Turnstile** | Cloudflare customers | Non-intrusive |
| **GeeTest** | Chinese sites | Slider puzzles |
| **KeyCaptcha** | Various | Puzzle assembly |
| **MTCaptcha** | Various | GDPR-focused |

---

## CAPTCHA Challenges for Scrapers

### The Fundamental Problem

```python
import requests

response = requests.get("https://protected-site.com/data")

# Site returns CAPTCHA page instead of data
if "recaptcha" in response.text:
    # Now what?
    pass
```

### When CAPTCHAs Appear

| Trigger | Description |
|---------|-------------|
| **Always** | Every form submission |
| **Suspicious IP** | Known datacenter, VPN, proxy |
| **Rate exceeded** | Too many requests |
| **Failed behavioral** | Non-human patterns |
| **Geographic** | Unusual location |
| **Session expired** | Need re-verification |

---

## Approaches to Handle CAPTCHAs

### Approach 1: Avoid Triggering

The best CAPTCHA is the one you never see.

```python
# Strategies to avoid CAPTCHAs
strategies = {
    "residential_proxies": "Use IPs not in datacenter ranges",
    "slow_down": "Don't trigger rate limits",
    "browser_headers": "Look like a real browser",
    "cookies": "Maintain sessions like a human",
    "behavioral": "Mouse movements, delays, scroll",
    "warm_up": "Browse normally before scraping",
}
```

### Approach 2: CAPTCHA Solving Services

Third-party services that solve CAPTCHAs for you.

#### How They Work

```
Your Scraper ──▶ Solving Service ──▶ Human Workers
                                          │
                ◀── Token ────────────────┘
```

#### Major Services

| Service | Price (1000 solves) | Speed | Types |
|---------|---------------------|-------|-------|
| **2Captcha** | $2-3 | 20-60s | All types |
| **Anti-Captcha** | $2-3 | 20-60s | All types |
| **CapMonster** | $1-2 | 10-30s | Limited types |
| **DeathByCaptcha** | $2-3 | 20-60s | All types |
| **Capsolver** | $2-3 | 10-30s | All types |

#### Using 2Captcha (Example)

```python
import requests
import time

CAPTCHA_API_KEY = "your_2captcha_key"

def solve_recaptcha_v2(site_key, page_url):
    """Solve reCAPTCHA v2 using 2Captcha."""
    
    # Step 1: Submit CAPTCHA
    submit_url = "http://2captcha.com/in.php"
    response = requests.get(submit_url, params={
        "key": CAPTCHA_API_KEY,
        "method": "userrecaptcha",
        "googlekey": site_key,
        "pageurl": page_url,
        "json": 1
    })
    
    result = response.json()
    if result["status"] != 1:
        raise Exception(f"Submit failed: {result}")
    
    captcha_id = result["request"]
    
    # Step 2: Poll for result
    result_url = "http://2captcha.com/res.php"
    
    for _ in range(60):  # Max 5 minutes
        time.sleep(5)
        
        response = requests.get(result_url, params={
            "key": CAPTCHA_API_KEY,
            "action": "get",
            "id": captcha_id,
            "json": 1
        })
        
        result = response.json()
        
        if result["status"] == 1:
            return result["request"]  # The solved token
        
        if result["request"] != "CAPCHA_NOT_READY":
            raise Exception(f"Solve failed: {result}")
    
    raise Exception("Timeout waiting for solution")

# Usage
token = solve_recaptcha_v2(
    site_key="6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
    page_url="https://example.com/form"
)

# Use token in form submission
response = requests.post("https://example.com/submit", data={
    "g-recaptcha-response": token,
    "other_field": "value"
})
```

#### Solving hCaptcha

```python
def solve_hcaptcha(site_key, page_url):
    """Solve hCaptcha using 2Captcha."""
    
    response = requests.get("http://2captcha.com/in.php", params={
        "key": CAPTCHA_API_KEY,
        "method": "hcaptcha",
        "sitekey": site_key,
        "pageurl": page_url,
        "json": 1
    })
    
    # ... same polling logic as reCAPTCHA
```

### Approach 3: Browser Automation + Service

For v3 and behavioral CAPTCHAs:

```python
from playwright.sync_api import sync_playwright

def solve_with_browser(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Visible browser
        page = browser.new_page()
        
        page.goto(url)
        
        # Wait for reCAPTCHA to load
        page.wait_for_selector("iframe[src*='recaptcha']")
        
        # Extract site key from page
        site_key = page.evaluate('''
            document.querySelector('.g-recaptcha').dataset.sitekey
        ''')
        
        # Solve via service
        token = solve_recaptcha_v2(site_key, url)
        
        # Inject token
        page.evaluate(f'''
            document.getElementById('g-recaptcha-response').value = '{token}';
        ''')
        
        # Submit form
        page.click("button[type='submit']")
        
        # Continue scraping
        content = page.content()
        browser.close()
        return content
```

### Approach 4: CapMonster Cloud (Automated)

AI-based solving (no humans):

```python
def solve_recaptcha_capmonster(site_key, page_url):
    response = requests.post(
        "https://api.capmonster.cloud/createTask",
        json={
            "clientKey": "YOUR_KEY",
            "task": {
                "type": "RecaptchaV2TaskProxyless",
                "websiteURL": page_url,
                "websiteKey": site_key
            }
        }
    )
    
    task_id = response.json()["taskId"]
    
    # Poll for result
    while True:
        time.sleep(3)
        result = requests.post(
            "https://api.capmonster.cloud/getTaskResult",
            json={"clientKey": "YOUR_KEY", "taskId": task_id}
        )
        data = result.json()
        
        if data["status"] == "ready":
            return data["solution"]["gRecaptchaResponse"]
```

---

## Handling reCAPTCHA v3

v3 is score-based and never shows a challenge. Strategies:

### Strategy 1: Improve Your Score

```python
# Factors that improve v3 score:
factors = {
    "google_cookies": "Be logged into Google",
    "history": "Have browsing history on the domain",
    "behavior": "Natural mouse/keyboard patterns",
    "timing": "Don't submit forms instantly",
    "reputation": "Use residential IP",
}
```

### Strategy 2: Use Token Services

```python
def solve_recaptcha_v3(site_key, page_url, action="submit", min_score=0.7):
    response = requests.get("http://2captcha.com/in.php", params={
        "key": CAPTCHA_API_KEY,
        "method": "userrecaptcha",
        "googlekey": site_key,
        "pageurl": page_url,
        "version": "v3",
        "action": action,
        "min_score": min_score,
        "json": 1
    })
    # ... poll for result
```

### Strategy 3: Browser Fingerprint Spoofing

Use tools like `puppeteer-extra-plugin-stealth` or `playwright-stealth`.

---

## CAPTCHA Detection

### Finding CAPTCHA on a Page

```python
from bs4 import BeautifulSoup

def detect_captcha(html):
    soup = BeautifulSoup(html, "html.parser")
    
    captchas = {
        "recaptcha_v2": bool(soup.select(".g-recaptcha")),
        "recaptcha_v3": "grecaptcha.execute" in html,
        "hcaptcha": bool(soup.select(".h-captcha")),
        "cloudflare": "cf-browser-verification" in html,
        "geetest": "geetest" in html.lower(),
        "funcaptcha": "funcaptcha" in html.lower(),
    }
    
    return {k: v for k, v in captchas.items() if v}

# Usage
response = requests.get(url)
detected = detect_captcha(response.text)
print(f"CAPTCHAs found: {detected}")
```

### Extracting CAPTCHA Parameters

```python
def extract_recaptcha_params(html):
    """Extract reCAPTCHA site key and data."""
    soup = BeautifulSoup(html, "html.parser")
    
    # v2
    recaptcha_div = soup.find("div", class_="g-recaptcha")
    if recaptcha_div:
        return {
            "version": "v2",
            "site_key": recaptcha_div.get("data-sitekey"),
            "callback": recaptcha_div.get("data-callback"),
        }
    
    # v3 (in script)
    import re
    match = re.search(r"grecaptcha\.execute\(['\"]([^'\"]+)['\"]", html)
    if match:
        return {
            "version": "v3",
            "site_key": match.group(1),
        }
    
    return None
```

---

## Cost Analysis

### When CAPTCHA Solving Makes Sense

| Volume | Cost/1000 | Break-even |
|--------|-----------|------------|
| 100/day | $0.20-0.30 | Usually worth it |
| 1,000/day | $2-3 | Evaluate alternatives |
| 10,000/day | $20-30 | Consider better avoidance |
| 100,000/day | $200-300 | Definitely optimize avoidance |

### Reducing CAPTCHA Encounters

```
Strategy                    CAPTCHA Reduction
───────────────────────────────────────────────
Better headers              -20%
Residential proxies         -50%
Slower scraping             -30%
Session persistence         -25%
Human-like behavior         -40%
───────────────────────────────────────────────
Combined                    -80% or more
```

---

## Summary

| CAPTCHA Type | Difficulty | Solution |
|--------------|------------|----------|
| **Text** | Easy | OCR (mostly obsolete) |
| **reCAPTCHA v2** | Medium | Solving services |
| **reCAPTCHA v2 Invisible** | Medium | Solving services |
| **reCAPTCHA v3** | Hard | Token services + stealth |
| **hCaptcha** | Medium | Solving services |
| **Cloudflare** | Hard | Specialized tools |
| **Custom** | Varies | Case-by-case |

### Key Takeaways

1. **Avoid > Solve** - Prevention is cheaper than solving
2. **Choose the right service** - Compare prices and speed
3. **Budget for CAPTCHAs** - Factor into scraping costs
4. **Combine strategies** - Services + stealth for v3
5. **Monitor effectiveness** - Track solve rates and costs

---

*Next: [03_bot_detection_fingerprinting.md](03_bot_detection_fingerprinting.md) - How sites identify automated visitors*
