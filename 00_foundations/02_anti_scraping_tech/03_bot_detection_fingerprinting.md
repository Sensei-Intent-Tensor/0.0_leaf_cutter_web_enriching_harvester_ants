# Bot Detection & Browser Fingerprinting

> **How Websites Identify Bots Without CAPTCHAs**

Modern anti-bot systems go far beyond CAPTCHAs. They build unique "fingerprints" of browsers and analyze behavior to distinguish humans from bots. This document reveals how fingerprinting works and how to counter it.

---

## The Fingerprinting Concept

```
Every Browser Leaves a Unique Fingerprint:

Real Browser:                         Headless Chrome:
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│ User-Agent: Chrome/120          │   │ User-Agent: Chrome/120          │
│ Screen: 1920x1080               │   │ Screen: 800x600 ← Unusual       │
│ Plugins: PDF, Flash             │   │ Plugins: [] ← Empty!            │
│ Fonts: 247 fonts                │   │ Fonts: 12 fonts ← Too few       │
│ WebGL: NVIDIA GTX 1080          │   │ WebGL: SwiftShader ← Headless!  │
│ Canvas: Unique hash             │   │ Canvas: Known headless hash     │
│ navigator.webdriver: false      │   │ navigator.webdriver: true ← Bot!│
└─────────────────────────────────┘   └─────────────────────────────────┘
         │                                      │
         ▼                                      ▼
    Looks human                            Detected as bot
```

---

## 1. Browser Fingerprinting Techniques

### 1.1 Canvas Fingerprinting

**How it works**: Draw hidden content to a canvas, hash the result. Different hardware/software produces different pixel data.

```javascript
// How sites fingerprint your canvas
function getCanvasFingerprint() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // Draw text with specific settings
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillStyle = '#f60';
    ctx.fillRect(125, 1, 62, 20);
    ctx.fillStyle = '#069';
    ctx.fillText('Cwm fjordbank glyphs vext quiz', 2, 15);
    
    // Add more drawing operations
    ctx.strokeStyle = 'rgba(102, 204, 0, 0.7)';
    ctx.beginPath();
    ctx.arc(50, 50, 50, 0, Math.PI * 2, true);
    ctx.stroke();
    
    // Hash the result
    return canvas.toDataURL().hashCode();
}

// Different machines produce different hashes due to:
// - GPU rendering differences
// - Font rendering differences
// - Anti-aliasing variations
// - Color profile differences
```

**Detection pattern**:
```
Real browsers: Unique canvas hashes (millions of variations)
Headless browsers: Often identical hashes (known fingerprints)
VMs: Different from physical machines
```

### 1.2 WebGL Fingerprinting

**How it works**: Query WebGL renderer information and render 3D content.

```javascript
function getWebGLFingerprint() {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || 
               canvas.getContext('experimental-webgl');
    
    if (!gl) return null;
    
    // Get renderer info
    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
    
    return {
        vendor: gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL),
        renderer: gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL),
        // Example: "NVIDIA Corporation", "NVIDIA GeForce GTX 1080"
    };
}
```

**Detection signals**:
| Value | Interpretation |
|-------|----------------|
| `NVIDIA GeForce GTX 1080` | Real desktop GPU |
| `Intel HD Graphics 620` | Real integrated GPU |
| `Google SwiftShader` | **Headless Chrome!** |
| `llvmpipe` | **Virtual machine** |
| `Mesa DRI Intel` | Linux real GPU |
| `ANGLE` | Chrome on Windows (normal) |

### 1.3 Audio Fingerprinting

**How it works**: Generate audio signals using AudioContext, analyze the output.

```javascript
function getAudioFingerprint() {
    const audioContext = new (window.AudioContext || 
                              window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const analyser = audioContext.createAnalyser();
    const gain = audioContext.createGain();
    const scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);
    
    oscillator.type = 'triangle';
    oscillator.frequency.setValueAtTime(10000, audioContext.currentTime);
    gain.gain.setValueAtTime(0, audioContext.currentTime);
    
    oscillator.connect(analyser);
    analyser.connect(scriptProcessor);
    scriptProcessor.connect(gain);
    gain.connect(audioContext.destination);
    
    oscillator.start(0);
    
    // Capture and hash the audio data
    // Different hardware produces different subtle variations
}
```

**Why it works**: Audio processing varies by:
- Sound card
- Audio drivers
- Operating system
- CPU architecture

### 1.4 Font Fingerprinting

**How it works**: Detect which fonts are installed by measuring text rendering.

```javascript
function detectFonts() {
    const baseFonts = ['monospace', 'sans-serif', 'serif'];
    const testFonts = [
        'Arial', 'Verdana', 'Times New Roman', 'Courier New',
        'Georgia', 'Comic Sans MS', 'Impact', 'Trebuchet MS',
        // ... hundreds more
    ];
    
    const testString = 'mmmmmmmmmmlli';
    const testSize = '72px';
    
    const span = document.createElement('span');
    span.style.fontSize = testSize;
    span.innerHTML = testString;
    document.body.appendChild(span);
    
    const detected = [];
    
    for (const font of testFonts) {
        for (const baseFont of baseFonts) {
            span.style.fontFamily = `'${font}', ${baseFont}`;
            // If width/height differs from base font, font is installed
            // This is a simplification - real implementations are more complex
        }
    }
    
    document.body.removeChild(span);
    return detected;
}
```

**Detection pattern**:
```
Windows 10: ~200 fonts typical
macOS: ~150 fonts typical
Linux: ~50 fonts typical
Headless: Very few fonts (10-20)
Docker/Container: Minimal fonts
```

### 1.5 Screen and Window Fingerprinting

```javascript
function getScreenFingerprint() {
    return {
        // Screen properties
        screenWidth: screen.width,
        screenHeight: screen.height,
        availWidth: screen.availWidth,
        availHeight: screen.availHeight,
        colorDepth: screen.colorDepth,
        pixelRatio: window.devicePixelRatio,
        
        // Window properties
        innerWidth: window.innerWidth,
        innerHeight: window.innerHeight,
        outerWidth: window.outerWidth,
        outerHeight: window.outerHeight,
        
        // Position (often 0,0 for headless)
        screenX: window.screenX,
        screenY: window.screenY,
    };
}
```

**Suspicious patterns**:
| Signal | Real Browser | Bot/Headless |
|--------|--------------|--------------|
| Screen size | Common sizes (1920x1080) | Unusual (800x600) |
| Window size | Smaller than screen | Same as screen |
| Position | Non-zero | 0,0 |
| Color depth | 24 or 32 | 24 |
| Pixel ratio | 1, 1.5, 2 | 1 |

### 1.6 Navigator and Plugin Detection

```javascript
function getNavigatorFingerprint() {
    return {
        // Basic info
        userAgent: navigator.userAgent,
        language: navigator.language,
        languages: navigator.languages,
        platform: navigator.platform,
        
        // Hardware
        hardwareConcurrency: navigator.hardwareConcurrency,
        deviceMemory: navigator.deviceMemory,
        maxTouchPoints: navigator.maxTouchPoints,
        
        // Plugins (often empty in headless)
        plugins: Array.from(navigator.plugins).map(p => p.name),
        mimeTypes: Array.from(navigator.mimeTypes).map(m => m.type),
        
        // Automation detection
        webdriver: navigator.webdriver,  // TRUE = automated!
        
        // Feature detection
        cookieEnabled: navigator.cookieEnabled,
        doNotTrack: navigator.doNotTrack,
    };
}
```

**Critical detection points**:
```javascript
// These are dead giveaways:
navigator.webdriver        // true = automation
navigator.plugins.length   // 0 = suspicious
navigator.languages        // undefined = suspicious
window.chrome              // undefined in headless (without stealth)
window.chrome.runtime      // undefined = suspicious
```

---

## 2. Behavioral Analysis

### 2.1 Mouse Movement Analysis

```javascript
class MouseAnalyzer {
    constructor() {
        this.movements = [];
        this.clicks = [];
        
        document.addEventListener('mousemove', e => {
            this.movements.push({
                x: e.clientX,
                y: e.clientY,
                time: Date.now()
            });
        });
        
        document.addEventListener('click', e => {
            this.clicks.push({
                x: e.clientX,
                y: e.clientY,
                time: Date.now()
            });
        });
    }
    
    analyzePatterns() {
        if (this.movements.length < 10) return 'insufficient_data';
        
        // Calculate velocities
        const velocities = [];
        for (let i = 1; i < this.movements.length; i++) {
            const dx = this.movements[i].x - this.movements[i-1].x;
            const dy = this.movements[i].y - this.movements[i-1].y;
            const dt = this.movements[i].time - this.movements[i-1].time;
            const velocity = Math.sqrt(dx*dx + dy*dy) / dt;
            velocities.push(velocity);
        }
        
        // Human characteristics:
        // - Variable velocity (acceleration/deceleration)
        // - Curved paths (not straight lines)
        // - Overshooting targets
        // - Micro-adjustments near targets
        
        const avgVelocity = velocities.reduce((a,b) => a+b) / velocities.length;
        const velocityVariance = this.calculateVariance(velocities);
        
        // Bots often have:
        // - Constant velocity
        // - Perfectly straight paths
        // - Exact target clicking
        // - No micro-movements
        
        if (velocityVariance < 0.1) return 'likely_bot';
        return 'likely_human';
    }
}
```

**Human mouse patterns**:
```
Human Movement:           Bot Movement:
    ●                         ●
   ╱│                         │
  ╱ │ (curved path)           │ (straight line)
 ╱  │                         │
●   ▼                         ▼
start → overshoot → target    start → target
```

### 2.2 Keyboard Analysis

```javascript
class KeyboardAnalyzer {
    constructor() {
        this.keyEvents = [];
        
        document.addEventListener('keydown', e => {
            this.keyEvents.push({
                key: e.key,
                type: 'down',
                time: Date.now()
            });
        });
        
        document.addEventListener('keyup', e => {
            this.keyEvents.push({
                key: e.key,
                type: 'up',
                time: Date.now()
            });
        });
    }
    
    analyzeTyping() {
        // Calculate dwell time (key held down)
        // Calculate flight time (between keys)
        
        const dwellTimes = [];
        const flightTimes = [];
        
        // Human typing characteristics:
        // - Variable dwell times (70-150ms typical)
        // - Variable flight times
        // - Rhythm patterns
        // - Common typos and corrections
        
        // Bot characteristics:
        // - Identical dwell times
        // - Perfect, constant speed
        // - No typos
        // - Unnaturally fast
    }
}
```

**Typing patterns comparison**:
```
Human typing "hello":
h[100ms]e[85ms]l[120ms]l[90ms]o[110ms]  ← Variable timing

Bot typing "hello":
h[10ms]e[10ms]l[10ms]l[10ms]o[10ms]  ← Identical timing
```

### 2.3 Scroll Behavior Analysis

```javascript
class ScrollAnalyzer {
    constructor() {
        this.scrollEvents = [];
        
        window.addEventListener('scroll', () => {
            this.scrollEvents.push({
                position: window.scrollY,
                time: Date.now()
            });
        });
    }
    
    analyzeScrolling() {
        // Human scroll characteristics:
        // - Variable scroll amounts
        // - Pauses (reading content)
        // - Occasional scroll up (re-reading)
        // - Inertial scrolling on touch devices
        // - Scroll speed varies with content
        
        // Bot characteristics:
        // - Constant scroll increments
        // - No pauses
        // - Always down, never up
        // - Perfectly timed intervals
    }
}
```

### 2.4 Timing Analysis

```javascript
class TimingAnalyzer {
    analyzeRequestTiming(requests) {
        const intervals = [];
        for (let i = 1; i < requests.length; i++) {
            intervals.push(requests[i].time - requests[i-1].time);
        }
        
        // Human patterns:
        // - Random intervals (thinking, reading)
        // - Longer gaps between pages
        // - Short bursts of activity
        // - Session patterns (morning, evening)
        
        // Bot patterns:
        // - Fixed intervals (exactly 1000ms)
        // - Constant rate over hours
        // - No daily patterns
        // - Immediate sequential requests
        
        const variance = this.calculateVariance(intervals);
        const mean = intervals.reduce((a,b) => a+b) / intervals.length;
        
        // Coefficient of variation
        const cv = Math.sqrt(variance) / mean;
        
        // Humans: CV > 0.5 typically
        // Bots: CV < 0.1 often
        
        return cv;
    }
}
```

---

## 3. JavaScript Environment Checks

### 3.1 Automation Detection Properties

```javascript
function detectAutomation() {
    const indicators = {
        // Webdriver flag (dead giveaway)
        webdriver: navigator.webdriver,
        
        // Selenium-specific
        seleniumIdeRecording: window._selenium,
        webdriverEvaluate: window.webdriver,
        driverEvaluate: window.driver_evaluate,
        seleniumEvaluate: window.selenium_evaluate,
        
        // Puppeteer/Playwright-specific
        puppeteer: window.__puppeteer_evaluation_script__,
        playwrightBinding: window.__playwright,
        
        // PhantomJS
        phantom: window.callPhantom || window._phantom,
        
        // Nightmare
        nightmare: window.__nightmare,
        
        // Generic automation
        domAutomation: window.domAutomation,
        domAutomationController: window.domAutomationController,
        
        // Chrome DevTools Protocol
        cdc: document.getElementsByTagName('html')[0]
                     .getAttribute('cdc_adoQpoasnfa76pfcZLmcfl'),
    };
    
    for (const [key, value] of Object.entries(indicators)) {
        if (value) return { detected: true, indicator: key };
    }
    
    return { detected: false };
}
```

### 3.2 Chrome-Specific Checks

```javascript
function chromeChecks() {
    // Real Chrome has these
    const hasChrome = !!window.chrome;
    const hasChromeRuntime = !!(window.chrome && window.chrome.runtime);
    const hasPermissions = !!(window.chrome && window.chrome.permissions);
    
    // Check for missing/modified properties
    const checks = {
        chromeExists: hasChrome,
        runtimeExists: hasChromeRuntime,
        
        // Real Chrome has these app properties
        appInstalled: window.chrome?.app?.isInstalled,
        appGetDetails: typeof window.chrome?.app?.getDetails === 'function',
        
        // Check prototype chain
        correctPrototype: Object.getPrototypeOf(navigator) === Navigator.prototype,
    };
    
    return checks;
}
```

### 3.3 Permission API Analysis

```javascript
async function analyzePermissions() {
    const permissions = [
        'geolocation',
        'notifications', 
        'push',
        'midi',
        'camera',
        'microphone',
        'background-fetch',
        'background-sync',
        'persistent-storage',
        'ambient-light-sensor',
        'accelerometer',
        'gyroscope',
        'magnetometer',
        'clipboard-read',
        'clipboard-write',
    ];
    
    const results = {};
    
    for (const permission of permissions) {
        try {
            const status = await navigator.permissions.query({ name: permission });
            results[permission] = status.state;
        } catch (e) {
            results[permission] = 'error';
        }
    }
    
    // Headless often has different permission patterns
    // Real browsers have user-set permissions
    
    return results;
}
```

---

## 4. Stealth Techniques

### 4.1 Playwright Stealth

```python
from playwright.sync_api import sync_playwright

def create_stealth_page(browser):
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        locale='en-US',
        timezone_id='America/New_York',
        geolocation={'latitude': 40.7128, 'longitude': -74.0060},
        permissions=['geolocation'],
    )
    
    page = context.new_page()
    
    # Inject stealth scripts
    page.add_init_script("""
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });
        
        // Fix plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                {
                    0: {type: "application/x-google-chrome-pdf"},
                    description: "Portable Document Format",
                    filename: "internal-pdf-viewer",
                    length: 1,
                    name: "Chrome PDF Plugin"
                },
                {
                    0: {type: "application/pdf"},
                    description: "",
                    filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                    length: 1,
                    name: "Chrome PDF Viewer"
                },
            ],
        });
        
        // Fix languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        
        // Fix platform
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32',
        });
        
        // Fix hardware concurrency
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8,
        });
        
        // Fix device memory
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8,
        });
        
        // Add chrome object
        window.chrome = {
            runtime: {},
            app: {
                isInstalled: false,
                getDetails: () => null,
            },
        };
        
        // Fix permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
    """)
    
    return page

# Usage
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = create_stealth_page(browser)
    page.goto("https://bot.sannysoft.com")  # Test fingerprint
```

### 4.2 Using playwright-stealth Library

```python
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Apply stealth
    stealth_sync(page)
    
    page.goto("https://example.com")
```

### 4.3 Puppeteer Extra Stealth

```javascript
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

// Apply stealth plugin
puppeteer.use(StealthPlugin());

(async () => {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    
    await page.goto('https://example.com');
    
    // Check if we pass bot detection
    await page.goto('https://bot.sannysoft.com');
    await page.screenshot({ path: 'fingerprint.png' });
    
    await browser.close();
})();
```

### 4.4 Advanced Stealth Configurations

```python
def advanced_stealth_context(browser):
    """Create maximally stealthy browser context"""
    
    context = browser.new_context(
        # Realistic viewport
        viewport={'width': 1920, 'height': 1080},
        
        # Realistic user agent
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        
        # Locale and timezone consistency
        locale='en-US',
        timezone_id='America/New_York',
        
        # Geolocation (consistent with timezone)
        geolocation={'latitude': 40.7128, 'longitude': -74.0060},
        permissions=['geolocation'],
        
        # Color scheme (matches OS)
        color_scheme='light',
        
        # Device scale factor
        device_scale_factor=1,
        
        # Disable some telemetry
        ignore_https_errors=False,
        
        # Extra HTTP headers
        extra_http_headers={
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        },
    )
    
    return context
```

---

## 5. Canvas Fingerprint Spoofing

### 5.1 Noise Injection

```javascript
// Add noise to canvas operations
const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
HTMLCanvasElement.prototype.toDataURL = function(type) {
    if (type === 'image/png') {
        const canvas = this;
        const ctx = canvas.getContext('2d');
        
        // Get image data
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;
        
        // Add subtle noise
        for (let i = 0; i < data.length; i += 4) {
            // Modify each pixel slightly
            data[i] = data[i] ^ (Math.random() > 0.5 ? 1 : 0);     // R
            data[i+1] = data[i+1] ^ (Math.random() > 0.5 ? 1 : 0); // G
            data[i+2] = data[i+2] ^ (Math.random() > 0.5 ? 1 : 0); // B
        }
        
        // Put back modified data
        ctx.putImageData(imageData, 0, 0);
    }
    
    return originalToDataURL.apply(this, arguments);
};
```

### 5.2 Consistent Spoofing

```python
def canvas_spoof_script():
    """Generate consistent canvas fingerprint spoof"""
    return """
        (function() {
            // Generate consistent seed based on user agent
            const seed = navigator.userAgent.split('').reduce((a, c) => 
                a + c.charCodeAt(0), 0);
            
            // Seeded random for consistency
            function seededRandom() {
                const x = Math.sin(seed++) * 10000;
                return x - Math.floor(x);
            }
            
            const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
            CanvasRenderingContext2D.prototype.getImageData = function(x, y, w, h) {
                const imageData = originalGetImageData.apply(this, arguments);
                
                // Add consistent noise
                for (let i = 0; i < imageData.data.length; i += 4) {
                    if (seededRandom() < 0.01) {
                        imageData.data[i] ^= 1;
                    }
                }
                
                return imageData;
            };
        })();
    """
```

---

## 6. WebGL Fingerprint Spoofing

```javascript
// Spoof WebGL vendor/renderer
const getParameterProxyHandler = {
    apply: function(target, thisArg, args) {
        const param = args[0];
        const gl = thisArg;
        
        // UNMASKED_VENDOR_WEBGL
        if (param === 37445) {
            return 'Intel Inc.';
        }
        
        // UNMASKED_RENDERER_WEBGL  
        if (param === 37446) {
            return 'Intel Iris OpenGL Engine';
        }
        
        return Reflect.apply(target, thisArg, args);
    }
};

// Apply to both WebGL and WebGL2
const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = new Proxy(
    originalGetParameter, 
    getParameterProxyHandler
);

if (WebGL2RenderingContext) {
    const originalGetParameter2 = WebGL2RenderingContext.prototype.getParameter;
    WebGL2RenderingContext.prototype.getParameter = new Proxy(
        originalGetParameter2,
        getParameterProxyHandler
    );
}
```

---

## 7. Testing Your Stealth

### 7.1 Fingerprint Testing Sites

| Site | What It Tests |
|------|---------------|
| `bot.sannysoft.com` | Comprehensive bot detection |
| `browserleaks.com` | All fingerprint types |
| `amiunique.org` | Fingerprint uniqueness |
| `coveryourtracks.eff.org` | EFF tracking test |
| `pixelscan.net` | Advanced bot detection |
| `creepjs.com` | JavaScript fingerprinting |

### 7.2 Automated Testing

```python
from playwright.sync_api import sync_playwright
import json

def test_stealth(page):
    """Test stealth against various detectors"""
    
    results = {}
    
    # Test 1: SannySoft
    page.goto("https://bot.sannysoft.com")
    page.wait_for_load_state("networkidle")
    
    # Get test results from page
    results['sannysoft'] = page.evaluate("""
        () => {
            const rows = document.querySelectorAll('table tr');
            const results = {};
            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                if (cells.length >= 2) {
                    results[cells[0].textContent] = cells[1].textContent;
                }
            });
            return results;
        }
    """)
    
    # Test 2: Navigator properties
    results['navigator'] = page.evaluate("""
        () => ({
            webdriver: navigator.webdriver,
            plugins: navigator.plugins.length,
            languages: navigator.languages,
            platform: navigator.platform,
            hardwareConcurrency: navigator.hardwareConcurrency,
        })
    """)
    
    # Test 3: Chrome object
    results['chrome'] = page.evaluate("""
        () => ({
            exists: !!window.chrome,
            runtime: !!window.chrome?.runtime,
            app: !!window.chrome?.app,
        })
    """)
    
    return results

# Run test
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    stealth_sync(page)  # Apply stealth
    
    results = test_stealth(page)
    print(json.dumps(results, indent=2))
```

### 7.3 Continuous Monitoring

```python
class StealthMonitor:
    """Monitor stealth effectiveness over time"""
    
    def __init__(self):
        self.test_results = []
    
    def run_test_suite(self, page):
        result = {
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
        # Webdriver check
        result['tests']['webdriver'] = page.evaluate(
            "navigator.webdriver"
        ) == False
        
        # Plugins check
        result['tests']['plugins'] = page.evaluate(
            "navigator.plugins.length"
        ) > 0
        
        # Chrome check
        result['tests']['chrome'] = page.evaluate(
            "!!window.chrome && !!window.chrome.runtime"
        )
        
        # Canvas check (should vary)
        canvas_hash = page.evaluate("""
            () => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                ctx.textBaseline = 'top';
                ctx.font = '14px Arial';
                ctx.fillText('test', 0, 0);
                return canvas.toDataURL();
            }
        """)
        result['tests']['canvas_hash'] = canvas_hash[:50]
        
        self.test_results.append(result)
        return result
    
    def get_pass_rate(self):
        if not self.test_results:
            return 0
        
        total_tests = 0
        passed_tests = 0
        
        for result in self.test_results:
            for test_name, passed in result['tests'].items():
                if test_name != 'canvas_hash':
                    total_tests += 1
                    if passed:
                        passed_tests += 1
        
        return passed_tests / total_tests if total_tests > 0 else 0
```

---

## 8. Behavioral Countermeasures

### 8.1 Human-Like Mouse Movement

```python
import random
import math

class HumanMouse:
    @staticmethod
    def bezier_curve(start, end, control1, control2, steps=50):
        """Generate Bezier curve points"""
        points = []
        for t in range(steps + 1):
            t = t / steps
            x = (1-t)**3 * start[0] + 3*(1-t)**2*t * control1[0] + \
                3*(1-t)*t**2 * control2[0] + t**3 * end[0]
            y = (1-t)**3 * start[1] + 3*(1-t)**2*t * control1[1] + \
                3*(1-t)*t**2 * control2[1] + t**3 * end[1]
            points.append((x, y))
        return points
    
    @staticmethod
    def generate_path(start, end):
        """Generate human-like mouse path"""
        distance = math.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2)
        
        # Add overshoot
        overshoot = 20 * random.random()
        direction = math.atan2(end[1]-start[1], end[0]-start[0])
        overshoot_point = (
            end[0] + overshoot * math.cos(direction),
            end[1] + overshoot * math.sin(direction)
        )
        
        # Generate curved path
        control1 = (
            start[0] + (end[0]-start[0])/3 + random.randint(-50, 50),
            start[1] + (end[1]-start[1])/3 + random.randint(-50, 50)
        )
        control2 = (
            start[0] + 2*(end[0]-start[0])/3 + random.randint(-50, 50),
            start[1] + 2*(end[1]-start[1])/3 + random.randint(-50, 50)
        )
        
        # Main path
        path = HumanMouse.bezier_curve(start, overshoot_point, control1, control2)
        
        # Correction path (if overshoot)
        if overshoot > 5:
            correction = HumanMouse.bezier_curve(
                overshoot_point, end,
                (overshoot_point[0], overshoot_point[1]),
                (end[0], end[1]),
                steps=10
            )
            path.extend(correction)
        
        return path
    
    @staticmethod
    async def move_to(page, x, y):
        """Move mouse with human-like motion"""
        # Get current position
        current = await page.evaluate("() => ({x: window.mouseX || 0, y: window.mouseY || 0})")
        start = (current['x'], current['y'])
        end = (x, y)
        
        # Generate path
        path = HumanMouse.generate_path(start, end)
        
        # Move along path with variable speed
        for i, point in enumerate(path):
            # Variable delay (faster in middle, slower at ends)
            progress = i / len(path)
            delay = 5 + 15 * math.sin(progress * math.pi)  # ms
            
            await page.mouse.move(point[0], point[1])
            await page.wait_for_timeout(delay)
```

### 8.2 Human-Like Typing

```python
class HumanTyping:
    # Average typing speeds (ms between keys)
    BASE_DELAY = 100
    VARIANCE = 50
    
    # Digraph timings (common letter pairs are faster)
    DIGRAPH_SPEEDS = {
        'th': 0.7, 'he': 0.7, 'in': 0.7, 'er': 0.7, 'an': 0.7,
        'on': 0.8, 'at': 0.8, 'en': 0.8, 'nd': 0.8, 'ti': 0.8,
    }
    
    @staticmethod
    def get_delay(prev_char, curr_char):
        """Calculate delay based on character pair"""
        base = HumanTyping.BASE_DELAY
        
        # Check for digraph
        digraph = (prev_char + curr_char).lower()
        if digraph in HumanTyping.DIGRAPH_SPEEDS:
            base *= HumanTyping.DIGRAPH_SPEEDS[digraph]
        
        # Same finger (slower on same hand)
        # Add random variance
        variance = random.gauss(0, HumanTyping.VARIANCE)
        
        return max(30, base + variance)
    
    @staticmethod
    async def type_text(page, selector, text):
        """Type text with human-like timing"""
        await page.click(selector)
        
        prev_char = ''
        for char in text:
            delay = HumanTyping.get_delay(prev_char, char)
            await page.keyboard.type(char)
            await page.wait_for_timeout(delay)
            prev_char = char
            
            # Occasional longer pause (thinking)
            if random.random() < 0.05:
                await page.wait_for_timeout(random.randint(200, 500))
```

---

## 9. Summary

### Fingerprinting Vectors

| Vector | What It Reveals | Spoofable? |
|--------|----------------|------------|
| Canvas | GPU/rendering | Yes (noise) |
| WebGL | GPU hardware | Yes (override) |
| Audio | Audio hardware | Partially |
| Fonts | Installed fonts | Difficult |
| Screen | Display setup | Yes |
| Navigator | Browser properties | Yes |
| Plugins | Installed plugins | Yes |
| Behavior | Human patterns | Requires effort |

### Detection Priorities

```
Most Common Detection Methods (in order):
1. navigator.webdriver === true     ← Easy to fix
2. Missing plugins/languages        ← Easy to fix
3. Missing chrome.runtime           ← Easy to fix
4. Canvas fingerprint mismatch      ← Medium effort
5. WebGL renderer (SwiftShader)     ← Medium effort
6. Behavioral analysis              ← Hard to fix
7. ML-based detection               ← Very hard to fix
```

### Essential Stealth Steps

```python
# Minimum stealth checklist:
1. ☐ Set navigator.webdriver = false
2. ☐ Add realistic plugins array
3. ☐ Add languages array
4. ☐ Create window.chrome object
5. ☐ Spoof WebGL renderer
6. ☐ Add canvas noise
7. ☐ Use realistic viewport
8. ☐ Match user-agent to actual browser version
9. ☐ Add human-like delays
10. ☐ Implement mouse movement
```

### Key Principles

1. **Consistency is crucial**: All fingerprint vectors must tell the same story
2. **Real browsers are the reference**: Match actual browser behavior
3. **Behavior matters most**: Advanced systems analyze patterns, not just static properties
4. **Test regularly**: Detection methods evolve
5. **Layer your stealth**: Multiple techniques are better than one

---

*Next: [04_honeypots_traps.md](04_honeypots_traps.md) - Hidden detection mechanisms*
