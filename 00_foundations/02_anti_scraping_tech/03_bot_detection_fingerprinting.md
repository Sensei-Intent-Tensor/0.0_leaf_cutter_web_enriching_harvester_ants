# Bot Detection & Fingerprinting

> **How Sites Know You're Not Human**

Modern bot detection goes far beyond checking User-Agent strings. This document covers the sophisticated techniques sites use to identify automated visitors.

---

## The Detection Challenge

### The Arms Race

```
Era 1 (Early 2000s): Check User-Agent
├── Block: "python-requests", "curl", "wget"
└── Bypass: Set browser User-Agent

Era 2 (Late 2000s): Check Headers
├── Block: Missing Accept-Language, wrong order
└── Bypass: Copy all browser headers

Era 3 (2010s): JavaScript Checks
├── Block: No JS execution, wrong properties
└── Bypass: Use headless browsers

Era 4 (Now): Behavioral + Fingerprinting
├── Block: Statistical anomalies, fingerprint mismatches
└── Bypass: Much harder...
```

---

## 1. Request-Based Detection

### Header Analysis

Sites check request headers for:

```python
# Suspicious patterns
red_flags = {
    # Missing headers
    "no_accept_language": True,
    "no_accept_encoding": True,
    
    # Bot signatures
    "user_agent_contains_bot": "python-requests/2.28.0",
    
    # Wrong order (browsers have specific order)
    "header_order": ["Host", "User-Agent", "Accept", ...],
    
    # Inconsistencies
    "chrome_ua_but_no_sec_ch_ua": True,
}
```

### IP Reputation

| IP Type | Detection Risk | Reason |
|---------|----------------|--------|
| **Residential** | Low | Real ISP, shared with humans |
| **Mobile** | Very Low | Carrier NAT, many users per IP |
| **Datacenter** | High | AWS, GCP, Azure IP ranges known |
| **VPN** | High | Known VPN exit nodes |
| **Tor** | Very High | Exit nodes are public |
| **Proxy lists** | Very High | Scraped proxies are known |

### Detection Services Check:

```python
# IP databases sites use
ip_databases = [
    "ipinfo.io",          # IP metadata
    "maxmind.com",        # GeoIP + fraud scoring
    "ipqualityscore.com", # Bot/fraud detection
    "scamalytics.com",    # Proxy/VPN detection
]
```

### TLS Fingerprinting

Every TLS client has a unique fingerprint based on:
- Supported cipher suites
- Extensions offered
- Order of parameters

**JA3 Fingerprint:**

```python
# JA3 hash identifies your TLS client
# Real Chrome: ea44ba3d10a89f0c1ab8ba65d54f7523
# Python requests: 96b6a54e7c6c9d2fb6acde5c5f5e5d00  # Different!

# Solution: Use libraries that mimic browser TLS
# - curl_cffi (Python)
# - got-scraping (Node.js)
# - tls-client (Go)
```

**HTTP/2 Fingerprinting:**

```python
# HTTP/2 settings also create fingerprints
# - SETTINGS frame values
# - Priority tree structure
# - Window size
```

---

## 2. Browser Fingerprinting

### What is a Browser Fingerprint?

A unique identifier created from browser characteristics:

```javascript
// Simplified fingerprint collection
const fingerprint = {
    // Screen
    screenWidth: screen.width,
    screenHeight: screen.height,
    colorDepth: screen.colorDepth,
    devicePixelRatio: window.devicePixelRatio,
    
    // Browser
    userAgent: navigator.userAgent,
    language: navigator.language,
    languages: navigator.languages,
    platform: navigator.platform,
    cookieEnabled: navigator.cookieEnabled,
    doNotTrack: navigator.doNotTrack,
    
    // Hardware
    hardwareConcurrency: navigator.hardwareConcurrency,
    deviceMemory: navigator.deviceMemory,
    maxTouchPoints: navigator.maxTouchPoints,
    
    // Plugins & MIME types
    plugins: Array.from(navigator.plugins).map(p => p.name),
    mimeTypes: Array.from(navigator.mimeTypes).map(m => m.type),
    
    // WebGL
    webglVendor: getWebGLVendor(),
    webglRenderer: getWebGLRenderer(),
    
    // Canvas
    canvasFingerprint: getCanvasFingerprint(),
    
    // Audio
    audioFingerprint: getAudioFingerprint(),
    
    // Fonts
    fonts: getAvailableFonts(),
    
    // Timezone
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    timezoneOffset: new Date().getTimezoneOffset(),
};
```

### Canvas Fingerprinting

Drawing operations produce unique outputs based on GPU/driver:

```javascript
function getCanvasFingerprint() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // Draw text with specific font
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillStyle = '#f60';
    ctx.fillRect(125, 1, 62, 20);
    ctx.fillStyle = '#069';
    ctx.fillText('Hello, world!', 2, 15);
    
    // Get data URL (unique per system)
    return canvas.toDataURL();
}
```

**Problem for bots:** Headless browsers produce different canvas output.

### WebGL Fingerprinting

```javascript
function getWebGLInfo() {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl');
    
    return {
        vendor: gl.getParameter(gl.VENDOR),
        renderer: gl.getParameter(gl.RENDERER),
        // UNMASKED values reveal true GPU
        unmaskedVendor: gl.getParameter(
            gl.getExtension('WEBGL_debug_renderer_info').UNMASKED_VENDOR_WEBGL
        ),
        unmaskedRenderer: gl.getParameter(
            gl.getExtension('WEBGL_debug_renderer_info').UNMASKED_RENDERER_WEBGL
        ),
    };
}

// Real browser: "ANGLE (Intel HD Graphics 630)"
// Headless Chrome: "Google SwiftShader"  // RED FLAG!
```

### Audio Fingerprinting

Audio processing is unique per system:

```javascript
function getAudioFingerprint() {
    const context = new OfflineAudioContext(1, 44100, 44100);
    const oscillator = context.createOscillator();
    const compressor = context.createDynamicsCompressor();
    
    oscillator.connect(compressor);
    compressor.connect(context.destination);
    oscillator.start(0);
    
    return new Promise(resolve => {
        context.startRendering().then(buffer => {
            resolve(buffer.getChannelData(0).slice(4500, 5000));
        });
    });
}
```

### Font Fingerprinting

Different systems have different fonts:

```javascript
function detectFonts() {
    const testFonts = [
        'Arial', 'Verdana', 'Times New Roman',
        'Courier New', 'Georgia', 'Comic Sans MS',
        // System-specific fonts
        'Helvetica Neue', 'Segoe UI', 'Ubuntu'
    ];
    
    const baseFonts = ['monospace', 'sans-serif', 'serif'];
    const testString = 'mmmmmmmmmmlli';
    
    // Measure width with each font
    // Different installed fonts = different widths
}
```

---

## 3. Headless Browser Detection

### Common Detection Methods

```javascript
// Check for headless indicators
const headlessIndicators = {
    // Chrome headless
    'webdriver': navigator.webdriver,  // true in automation
    'languages_empty': navigator.languages.length === 0,
    'plugins_empty': navigator.plugins.length === 0,
    
    // Puppeteer/Playwright specific
    'chrome_runtime': !window.chrome || !window.chrome.runtime,
    
    // PhantomJS
    'phantom': window._phantom || window.callPhantom,
    
    // Nightmare
    'nightmare': window.__nightmare,
    
    // Selenium
    'selenium': window.document.__selenium_unwrapped ||
                window.document.__webdriver_evaluate ||
                window.document.__driver_evaluate,
    
    // CDP (Chrome DevTools Protocol)
    'cdp': !!(window.cdc_adoQpoasnfa76pfcZLmcfl_Array ||
              window.cdc_adoQpoasnfa76pfcZLmcfl_Promise),
};
```

### The `navigator.webdriver` Problem

```javascript
// In automated browsers:
navigator.webdriver  // true

// In regular browsers:
navigator.webdriver  // undefined or false
```

**Mitigation in Playwright:**

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()
    
    # Remove webdriver flag
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)
    
    page = context.new_page()
```

### Permission Detection

```javascript
// Real browsers prompt for permissions
// Headless browsers often auto-allow or auto-deny

navigator.permissions.query({name: 'notifications'})
    .then(result => {
        if (result.state === 'prompt') {
            // Likely real browser
        } else {
            // Potentially automated
        }
    });
```

---

## 4. Behavioral Detection

### Mouse Movement Analysis

```javascript
// Sites track:
const mouseMetrics = {
    // Movement patterns
    movements: [],          // [(x, y, timestamp), ...]
    velocities: [],         // Speed between points
    accelerations: [],      // Rate of speed change
    angles: [],             // Direction changes
    
    // Statistics
    totalDistance: 0,
    averageSpeed: 0,
    straightLineRatio: 0,   // Bots often move in straight lines
    
    // Patterns
    hasNaturalCurves: false,
    hasHesitation: false,
    hasMicroMovements: false,
};
```

**Bot Detection Signals:**

| Pattern | Human | Bot |
|---------|-------|-----|
| **Movement path** | Curved, organic | Straight lines |
| **Speed** | Variable | Constant |
| **Micro-movements** | Present | Absent |
| **Hesitation** | Before clicks | None |
| **Off-target movements** | Common | Rare |

### Keyboard Patterns

```javascript
const keyboardMetrics = {
    keyDownTimes: {},       // When each key pressed
    keyUpTimes: {},         // When each key released
    interKeyDelays: [],     // Time between keypresses
    holdDurations: [],      // How long keys held
    
    // Patterns
    typingSpeed: 0,         // WPM
    errorRate: 0,           // Backspaces
    rhythmVariation: 0,     // Consistency
};
```

**Detection:**
- Bots type too consistently
- Bots don't make typos
- Bots type at inhuman speeds

### Scroll Behavior

```javascript
const scrollMetrics = {
    scrollEvents: [],       // [(position, timestamp), ...]
    scrollSpeeds: [],
    readingPauses: [],      // Time spent at positions
    
    // Patterns
    hasNaturalPauses: false,
    scrollsTooFast: false,
    scrollsToBottom: false, // Without reading
};
```

### Click Patterns

```javascript
const clickMetrics = {
    clicks: [],             // [(x, y, timestamp, element), ...]
    
    // Analysis
    clickAccuracy: 0,       // Distance from element center
    doubleClickSpeed: 0,
    clickTiming: [],
    
    // Suspicious patterns
    perfectCenterClicks: 0, // Bots click dead center
    instantClicks: 0,       // No human delay
};
```

---

## 5. Consistency Checks

### Cross-Checking Data Points

```javascript
const consistencyChecks = {
    // User-Agent vs JavaScript
    'ua_platform_match': navigator.userAgent.includes(navigator.platform),
    
    // Screen vs Window
    'screen_window_ratio': (screen.width >= window.innerWidth),
    
    // Timezone vs IP location
    'timezone_ip_match': checkTimezoneMatchesIP(),
    
    // Language vs Accept-Language
    'language_match': checkLanguageHeaders(),
    
    // Touch capability vs device
    'touch_device_match': checkTouchConsistency(),
};
```

### Common Inconsistencies

| Claim | Reality | Detection |
|-------|---------|-----------|
| Windows UA | Linux navigator.platform | ❌ |
| Mobile UA | No touch events | ❌ |
| Chrome UA | Missing Chrome APIs | ❌ |
| US timezone | Russia IP | ❌ |
| Retina display | devicePixelRatio = 1 | ❌ |

---

## 6. Stealth Techniques

### Playwright Stealth

```python
# playwright-stealth library
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Apply stealth patches
    stealth_sync(page)
    
    page.goto("https://bot-detection-test.com")
```

### Puppeteer Stealth

```javascript
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

puppeteer.use(StealthPlugin());

const browser = await puppeteer.launch({headless: true});
const page = await browser.newPage();
```

### What Stealth Patches

```javascript
// Common patches applied by stealth plugins:

// 1. navigator.webdriver
Object.defineProperty(navigator, 'webdriver', {get: () => false});

// 2. Chrome runtime
window.chrome = {runtime: {}};

// 3. Permissions
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({state: Notification.permission}) :
        originalQuery(parameters)
);

// 4. Plugins
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5]
});

// 5. Languages
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en']
});

// 6. WebGL vendor
// Patch getParameter to return realistic values
```

### Real Browser Profile

```python
# Using undetected-chromedriver
import undetected_chromedriver as uc

driver = uc.Chrome(headless=True)
driver.get("https://example.com")

# Uses real Chrome binary, patches detection
```

---

## 7. Testing Your Stealth

### Detection Test Sites

| Site | What It Tests |
|------|---------------|
| **bot.sannysoft.com** | Comprehensive bot detection |
| **browserleaks.com** | Fingerprint exposure |
| **amiunique.org** | Fingerprint uniqueness |
| **pixelscan.net** | Headless detection |
| **abrahamjuliot.github.io/creepjs** | Advanced fingerprinting |

### Automated Testing

```python
def test_bot_detection(page):
    """Test if browser passes bot detection."""
    
    page.goto("https://bot.sannysoft.com/")
    page.wait_for_timeout(5000)  # Let tests run
    
    # Check results
    results = page.evaluate('''
        Array.from(document.querySelectorAll('tr')).map(row => ({
            test: row.cells[0]?.innerText,
            result: row.cells[1]?.innerText,
            status: row.cells[1]?.className.includes('passed') ? 'pass' : 'fail'
        }))
    ''')
    
    failures = [r for r in results if r['status'] == 'fail']
    
    if failures:
        print("Failed tests:")
        for f in failures:
            print(f"  - {f['test']}: {f['result']}")
    else:
        print("All tests passed!")
    
    return len(failures) == 0
```

---

## 8. Advanced Evasion

### Rotating Fingerprints

```python
import random

def get_random_fingerprint():
    """Generate varied but consistent fingerprint."""
    
    screens = [
        (1920, 1080), (1366, 768), (1440, 900),
        (1536, 864), (2560, 1440), (1280, 720)
    ]
    
    screen = random.choice(screens)
    
    return {
        "screen_width": screen[0],
        "screen_height": screen[1],
        "color_depth": random.choice([24, 32]),
        "pixel_ratio": random.choice([1, 1.25, 1.5, 2]),
        "timezone": random.choice([
            "America/New_York", "America/Los_Angeles",
            "Europe/London", "Europe/Berlin"
        ]),
        "language": random.choice(["en-US", "en-GB"]),
    }
```

### Browser Context Isolation

```python
# Each task gets fresh context
for task in tasks:
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent=get_random_ua(),
        locale='en-US',
        timezone_id='America/New_York',
    )
    
    page = context.new_page()
    # ... scrape ...
    context.close()  # Fresh fingerprint next time
```

---

## Summary

| Detection Type | Difficulty to Evade | Solution |
|----------------|---------------------|----------|
| **User-Agent** | Easy | Copy browser UA |
| **Headers** | Easy | Copy all headers |
| **IP Reputation** | Medium | Residential proxies |
| **TLS Fingerprint** | Medium | Use curl_cffi |
| **navigator.webdriver** | Medium | Stealth plugins |
| **Canvas/WebGL** | Hard | Real browser |
| **Behavioral** | Very Hard | Human-like automation |

### Key Takeaways

1. **Use stealth plugins** - They handle common detections
2. **Test on detection sites** - Know what you're exposing
3. **Match your story** - UA, headers, timezone, IP must align
4. **Behavioral matters** - Add delays, mouse movements
5. **Rotate identities** - Don't reuse fingerprints

---

*Next: [04_honeypots_traps.md](04_honeypots_traps.md) - Hidden traps that catch bots*
