# Cookies, Sessions & State

> **Maintaining Identity Across Requests**

HTTP is stateless—each request is independent. Cookies and sessions allow websites to remember who you are. Understanding these is critical for scraping authenticated content or navigating multi-step flows.

---

## The Stateless Problem

```
Request 1: GET /login    → Server: "Who are you?"
Request 2: POST /login   → Server: "OK, logged in... but I'll forget"
Request 3: GET /dashboard → Server: "Who are you?" (forgot already!)
```

Without state management, every request starts fresh.

---

## 1. Cookies

### What Are Cookies?

Small pieces of data that:
1. Server sends to client via `Set-Cookie` header
2. Client stores locally
3. Client sends back via `Cookie` header on subsequent requests

```
First Request:
Client ──────────────────────────────────▶ Server
        GET /login

Response:
Client ◀────────────────────────────────── Server
        Set-Cookie: session_id=abc123

Subsequent Requests:
Client ──────────────────────────────────▶ Server
        GET /dashboard
        Cookie: session_id=abc123
                    ↑
        Server knows who you are!
```

### Cookie Anatomy

```
Set-Cookie: session_id=abc123; Path=/; Domain=.example.com; Expires=Thu, 01 Jan 2025 00:00:00 GMT; Secure; HttpOnly; SameSite=Lax
```

| Attribute | Purpose | Example |
|-----------|---------|---------|
| **Name=Value** | The cookie data | `session_id=abc123` |
| **Path** | URL paths where cookie is sent | `/` (all paths) |
| **Domain** | Domains where cookie is sent | `.example.com` (includes subdomains) |
| **Expires** | When cookie expires | `Thu, 01 Jan 2025 00:00:00 GMT` |
| **Max-Age** | Seconds until expiry | `86400` (1 day) |
| **Secure** | HTTPS only | (flag, no value) |
| **HttpOnly** | JavaScript can't access | (flag, no value) |
| **SameSite** | CSRF protection | `Strict`, `Lax`, `None` |

### Cookie Types

| Type | Lifetime | Use |
|------|----------|-----|
| **Session Cookie** | Until browser closes | Temporary login |
| **Persistent Cookie** | Has Expires/Max-Age | "Remember me" |
| **First-Party** | Same domain as page | Normal site cookies |
| **Third-Party** | Different domain | Tracking, ads |

---

## 2. Managing Cookies in Python

### Using requests.Session

The `Session` object automatically handles cookies:

```python
import requests

# Create session - persists cookies across requests
session = requests.Session()

# First request - server sets cookies
response = session.get("https://example.com/")
# Set-Cookie headers are automatically stored

# Subsequent requests - cookies sent automatically
response = session.get("https://example.com/dashboard")
# Cookie header included automatically

# View current cookies
print(session.cookies.get_dict())
# {'session_id': 'abc123', 'user_pref': 'dark'}
```

### Manual Cookie Management

```python
# Set cookies manually
session.cookies.set("custom_cookie", "value123")
session.cookies.set("another", "value", domain="example.com", path="/")

# Get specific cookie
session_id = session.cookies.get("session_id")

# Delete cookie
del session.cookies["unwanted_cookie"]

# Clear all cookies
session.cookies.clear()
```

### Passing Cookies Directly

```python
# Without session - pass cookies dict
response = requests.get(url, cookies={
    "session_id": "abc123",
    "user_id": "456"
})

# From browser - copy cookie string
cookie_string = "session_id=abc123; user_id=456; theme=dark"
cookies = dict(item.split("=") for item in cookie_string.split("; "))
response = requests.get(url, cookies=cookies)
```

### Exporting/Importing Cookies

```python
import pickle

# Save cookies to file
with open("cookies.pkl", "wb") as f:
    pickle.dump(session.cookies, f)

# Load cookies from file
with open("cookies.pkl", "rb") as f:
    session.cookies.update(pickle.load(f))
```

### Cookie Jar Operations

```python
from requests.cookies import RequestsCookieJar

# Create cookie jar
jar = RequestsCookieJar()
jar.set("session", "abc123", domain="example.com", path="/")

# Use with session
session.cookies = jar

# Iterate cookies
for cookie in session.cookies:
    print(f"{cookie.name}: {cookie.value}")
    print(f"  Domain: {cookie.domain}")
    print(f"  Path: {cookie.path}")
    print(f"  Expires: {cookie.expires}")
```

---

## 3. Sessions

### What Is a Session?

A session is server-side storage linked to a client via session ID (usually in a cookie).

```
┌─────────────┐              ┌─────────────────────────────┐
│   Client    │              │          Server             │
│             │              │                             │
│ Cookie:     │              │  Session Storage:           │
│ session_id= │─────────────▶│  abc123: {                  │
│ abc123      │              │    user_id: 42,             │
│             │              │    cart: [...],             │
│             │              │    logged_in: true          │
│             │              │  }                          │
└─────────────┘              └─────────────────────────────┘
```

### Session vs Cookies

| Aspect | Cookies | Sessions |
|--------|---------|----------|
| **Storage** | Client (browser) | Server |
| **Size Limit** | ~4KB per cookie | Unlimited |
| **Security** | Visible to client | Hidden on server |
| **Data** | Limited, strings | Any data structure |
| **Identifier** | Cookie itself | Session ID in cookie |

---

## 4. Login Flows

### Basic Login Pattern

```python
import requests
from bs4 import BeautifulSoup

session = requests.Session()

# Step 1: Get login page (may set initial cookies, get CSRF token)
login_page = session.get("https://example.com/login")
soup = BeautifulSoup(login_page.text, "html.parser")

# Step 2: Extract CSRF token (if present)
csrf_token = soup.find("input", {"name": "csrf_token"})["value"]

# Step 3: Submit login form
login_response = session.post(
    "https://example.com/login",
    data={
        "username": "myuser",
        "password": "mypassword",
        "csrf_token": csrf_token
    },
    headers={
        "Referer": "https://example.com/login"
    }
)

# Step 4: Verify login succeeded
if "dashboard" in login_response.url or "Welcome" in login_response.text:
    print("Login successful!")
else:
    print("Login failed!")

# Step 5: Access protected pages (session maintains auth)
dashboard = session.get("https://example.com/dashboard")
```

### Login Flow Variations

#### JSON API Login

```python
session = requests.Session()

# Login via JSON API
response = session.post(
    "https://example.com/api/auth/login",
    json={
        "email": "user@example.com",
        "password": "password123"
    },
    headers={"Content-Type": "application/json"}
)

# Token might be in response body (not cookie)
data = response.json()
access_token = data.get("access_token")

# Use token in subsequent requests
session.headers.update({
    "Authorization": f"Bearer {access_token}"
})
```

#### OAuth/Token-Based

```python
# Step 1: Get authorization URL
auth_url = f"https://example.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}"

# Step 2: User authorizes (manual step or browser automation)
# Receive callback with authorization code

# Step 3: Exchange code for token
token_response = requests.post(
    "https://example.com/oauth/token",
    data={
        "grant_type": "authorization_code",
        "code": auth_code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri
    }
)

access_token = token_response.json()["access_token"]
```

#### Two-Factor Authentication

```python
session = requests.Session()

# Step 1: Normal login
session.post(login_url, data={"username": "user", "password": "pass"})

# Step 2: Server requests 2FA
# May redirect to /2fa or return specific response

# Step 3: Submit 2FA code (from authenticator app, SMS, email)
session.post(
    "https://example.com/2fa/verify",
    data={"code": "123456"}  # User provides this
)

# Now fully authenticated
```

---

## 5. State Management Patterns

### Pattern 1: Session Per Scrape

```python
def scrape_site():
    session = requests.Session()
    
    # Login
    login(session)
    
    # Scrape with authenticated session
    for url in urls:
        response = session.get(url)
        process(response)
    
    # Session discarded after function
```

### Pattern 2: Persistent Session

```python
import pickle
import os

SESSION_FILE = "session.pkl"

def get_session():
    session = requests.Session()
    
    # Load existing session if available
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "rb") as f:
            session.cookies.update(pickle.load(f))
    
    return session

def save_session(session):
    with open(SESSION_FILE, "wb") as f:
        pickle.dump(session.cookies, f)

# Usage
session = get_session()
if not is_logged_in(session):
    login(session)
    save_session(session)

# Scrape
data = scrape(session)
save_session(session)  # Save updated cookies
```

### Pattern 3: Session Validation

```python
def is_session_valid(session):
    """Check if session is still authenticated."""
    response = session.get("https://example.com/api/me")
    
    # Various ways to check
    if response.status_code == 401:
        return False
    if "login" in response.url:
        return False
    if "error" in response.json():
        return False
    
    return True

def ensure_logged_in(session, credentials):
    """Ensure session is authenticated, login if needed."""
    if not is_session_valid(session):
        login(session, credentials)
    return session
```

### Pattern 4: Session Pool

```python
import random
from threading import Lock

class SessionPool:
    def __init__(self, credentials_list):
        self.sessions = []
        self.lock = Lock()
        
        # Create authenticated session for each account
        for creds in credentials_list:
            session = requests.Session()
            login(session, creds)
            self.sessions.append(session)
    
    def get_session(self):
        """Get a random session from pool."""
        with self.lock:
            return random.choice(self.sessions)

# Usage
pool = SessionPool([
    {"username": "user1", "password": "pass1"},
    {"username": "user2", "password": "pass2"},
])

response = pool.get_session().get(url)
```

---

## 6. Common Challenges

### Challenge: CSRF Tokens

```python
def get_csrf_token(session, url):
    """Extract CSRF token from page."""
    response = session.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Try common patterns
    csrf = None
    
    # Hidden input field
    csrf_input = soup.find("input", {"name": ["csrf_token", "_token", "authenticity_token", "csrfmiddlewaretoken"]})
    if csrf_input:
        csrf = csrf_input.get("value")
    
    # Meta tag
    csrf_meta = soup.find("meta", {"name": ["csrf-token", "_csrf"]})
    if csrf_meta:
        csrf = csrf_meta.get("content")
    
    # In JavaScript (regex fallback)
    if not csrf:
        import re
        match = re.search(r'csrf[_-]?token["\']?\s*[:=]\s*["\']([^"\']+)["\']', response.text, re.I)
        if match:
            csrf = match.group(1)
    
    return csrf
```

### Challenge: Session Expiration

```python
class ResilientSession:
    def __init__(self, credentials):
        self.credentials = credentials
        self.session = requests.Session()
        self.login()
    
    def login(self):
        # Perform login
        pass
    
    def get(self, url, **kwargs):
        response = self.session.get(url, **kwargs)
        
        # Check if session expired
        if self._is_session_expired(response):
            self.login()
            response = self.session.get(url, **kwargs)
        
        return response
    
    def _is_session_expired(self, response):
        return response.status_code == 401 or "login" in response.url
```

### Challenge: Cookies Across Subdomains

```python
# Cookie set for .example.com works on:
# - example.com
# - www.example.com
# - api.example.com

# May need to handle separately
session.cookies.set("token", "abc", domain=".example.com")
```

---

## 7. Browser Cookie Extraction

### From Browser DevTools

1. Open DevTools → Application → Cookies
2. Copy cookie values
3. Use in scraper

### Using browser_cookie3

```python
import browser_cookie3

# Get cookies from Chrome
chrome_cookies = browser_cookie3.chrome(domain_name=".example.com")

# Get cookies from Firefox
firefox_cookies = browser_cookie3.firefox(domain_name=".example.com")

# Use with requests
session = requests.Session()
session.cookies = chrome_cookies
response = session.get("https://example.com/protected")
```

### From Playwright/Puppeteer

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    
    # Navigate and login
    page.goto("https://example.com/login")
    page.fill("#username", "user")
    page.fill("#password", "pass")
    page.click("#submit")
    
    # Extract cookies
    cookies = context.cookies()
    
    # Convert to requests format
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(
            cookie["name"],
            cookie["value"],
            domain=cookie["domain"],
            path=cookie["path"]
        )
    
    browser.close()

# Now use session for fast requests
response = session.get("https://example.com/data")
```

---

## 8. Debugging Sessions

### Inspect Session State

```python
# View all cookies
print(session.cookies.get_dict())

# View cookie details
for cookie in session.cookies:
    print(f"Name: {cookie.name}")
    print(f"Value: {cookie.value}")
    print(f"Domain: {cookie.domain}")
    print(f"Path: {cookie.path}")
    print(f"Secure: {cookie.secure}")
    print(f"Expires: {cookie.expires}")
    print("---")
```

### Compare with Browser

```python
# Get what browser sends
browser_cookies = "session_id=abc; user_id=123"  # From DevTools

# Get what session has
session_cookies = "; ".join(f"{k}={v}" for k, v in session.cookies.get_dict().items())

print(f"Browser: {browser_cookies}")
print(f"Session: {session_cookies}")
```

---

## Summary

| Concept | Purpose | Key Points |
|---------|---------|------------|
| **Cookies** | Store state on client | Sent via headers, various attributes |
| **Sessions** | Server-side state | Linked to client via session cookie |
| **requests.Session** | Persist state in Python | Handles cookies automatically |
| **Login Flow** | Authenticate scraper | Get page → Extract CSRF → POST creds |
| **Token Auth** | Alternative to cookies | Store token, send in header |

### Best Practices

1. **Always use `requests.Session()`** for multi-request scraping
2. **Extract CSRF tokens** before form submissions
3. **Check login success** before proceeding
4. **Handle session expiration** gracefully
5. **Persist sessions** for long-running scrapers
6. **Use browser extraction** for complex auth flows

---

*Next: [04_headers_user_agents.md](04_headers_user_agents.md) - Crafting convincing request headers*
