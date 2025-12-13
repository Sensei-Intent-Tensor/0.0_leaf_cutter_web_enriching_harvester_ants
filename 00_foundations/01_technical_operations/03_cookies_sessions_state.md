# Cookies, Sessions & State

> **How Websites Remember You (And How to Maintain That Memory)**

HTTP is stateless—each request is independent. Cookies and sessions solve this by maintaining state across requests. For scrapers, understanding this is essential for authenticated scraping and maintaining context.

---

## Why State Matters

```
Without State:
Request 1: Login ✓
Request 2: "Who are you?" (Forgot you logged in)
Request 3: "Who are you?" (Still doesn't know)

With State (Cookies):
Request 1: Login ✓ → Server sends cookie
Request 2: Include cookie → "Welcome back!"
Request 3: Include cookie → "Still logged in!"
```

---

## 1. Cookies Fundamentals

### What Is a Cookie?

A cookie is a small piece of data stored by the client (browser/scraper) and sent with every subsequent request to the same domain.

```
Server Response:
Set-Cookie: session_id=abc123; Path=/; HttpOnly; Secure

Subsequent Requests:
Cookie: session_id=abc123
```

### Cookie Anatomy

```
Set-Cookie: name=value; Domain=.example.com; Path=/; Expires=Wed, 15 Jan 2025 12:00:00 GMT; Secure; HttpOnly; SameSite=Lax
           │     │      │                     │      │                                      │       │        │
           │     │      │                     │      │                                      │       │        └─ CSRF protection
           │     │      │                     │      │                                      │       └─ No JavaScript access
           │     │      │                     │      │                                      └─ HTTPS only
           │     │      │                     │      └─ When it expires
           │     │      │                     └─ Which paths receive it
           │     │      └─ Which domains receive it
           │     └─ The cookie value
           └─ The cookie name
```

### Cookie Attributes

| Attribute | Purpose | Scraping Impact |
|-----------|---------|-----------------|
| `Domain` | Which domains receive the cookie | Must match target domain |
| `Path` | Which paths receive the cookie | Usually `/` (all paths) |
| `Expires/Max-Age` | When cookie expires | Need to refresh if expired |
| `Secure` | HTTPS only | Use HTTPS |
| `HttpOnly` | No JavaScript access | Doesn't affect scrapers |
| `SameSite` | CSRF protection | Mostly doesn't affect scrapers |

---

## 2. Session Management

### How Sessions Work

```
┌─────────────┐                           ┌─────────────┐
│   CLIENT    │                           │   SERVER    │
│             │                           │             │
│  Login ─────┼──────────────────────────▶│             │
│             │                           │  Create     │
│             │                           │  Session    │
│             │◀──────────────────────────┼─ Set-Cookie │
│  Store      │   session_id=abc123       │  session_id │
│  Cookie     │                           │             │
│             │                           │             │
│  Request ───┼──────────────────────────▶│             │
│  + Cookie   │   Cookie: session_id=     │  Look up    │
│             │   abc123                  │  Session    │
│             │◀──────────────────────────┼─ "Welcome!" │
└─────────────┘                           └─────────────┘
```

### Session vs. Persistent Cookies

| Type | Expires | Use Case |
|------|---------|----------|
| **Session Cookie** | When browser closes | Login sessions |
| **Persistent Cookie** | Specific date/time | "Remember me" |

```python
# Session cookie (no Expires)
Set-Cookie: session_id=abc123

# Persistent cookie (has Expires)
Set-Cookie: remember_me=xyz789; Expires=Wed, 15 Jan 2025 12:00:00 GMT
```

---

## 3. Cookie Handling in Python

### Using requests.Session

```python
import requests

# Create a session - automatically handles cookies
session = requests.Session()

# First request - server may set cookies
response = session.get("https://example.com")
print(session.cookies)  # Shows received cookies

# Subsequent requests automatically include cookies
response = session.get("https://example.com/protected")
```

### Manual Cookie Management

```python
# Inspect cookies
for cookie in session.cookies:
    print(f"{cookie.name}: {cookie.value}")
    print(f"  Domain: {cookie.domain}")
    print(f"  Path: {cookie.path}")
    print(f"  Expires: {cookie.expires}")

# Add cookies manually
session.cookies.set("custom_cookie", "value", domain="example.com")

# Send cookies with a single request
response = requests.get(url, cookies={"session": "abc123"})

# Clear cookies
session.cookies.clear()
```

### Cookie Persistence

```python
import pickle

# Save cookies to file
with open("cookies.pkl", "wb") as f:
    pickle.dump(session.cookies, f)

# Load cookies later
with open("cookies.pkl", "rb") as f:
    session.cookies.update(pickle.load(f))
```

---

## 4. Authentication Flows

### Basic Login Flow

```python
import requests
from bs4 import BeautifulSoup

session = requests.Session()

# Step 1: Get login page (may set initial cookies, get CSRF token)
login_page = session.get("https://example.com/login")
soup = BeautifulSoup(login_page.text, "html.parser")

# Step 2: Extract CSRF token (if present)
csrf_token = soup.select_one("input[name='csrf_token']")
csrf_value = csrf_token["value"] if csrf_token else None

# Step 3: Submit login form
login_data = {
    "username": "myuser",
    "password": "mypass",
}
if csrf_value:
    login_data["csrf_token"] = csrf_value

response = session.post(
    "https://example.com/login",
    data=login_data,
    headers={"Referer": "https://example.com/login"}
)

# Step 4: Verify login succeeded
if "dashboard" in response.url or "Welcome" in response.text:
    print("Login successful!")
    # Session cookies now contain authentication
else:
    print("Login failed!")

# Step 5: Access protected content
protected = session.get("https://example.com/protected-page")
```

### OAuth / Token-Based Auth

```python
# Some sites use tokens instead of cookies
session = requests.Session()

# Login returns a token
login_response = session.post("https://api.example.com/login", json={
    "username": "user",
    "password": "pass"
})
token = login_response.json()["access_token"]

# Use token in subsequent requests
session.headers.update({
    "Authorization": f"Bearer {token}"
})

# Now all requests include the token
data = session.get("https://api.example.com/data").json()
```

### Two-Factor Authentication

```python
# Step 1: Initial login
response = session.post("https://example.com/login", data={
    "username": "user",
    "password": "pass"
})

# Step 2: Check if 2FA required
if "verification" in response.url:
    # Need to handle 2FA
    code = input("Enter 2FA code: ")  # Or from authenticator API
    response = session.post("https://example.com/verify", data={
        "code": code
    })

# Step 3: Continue with authenticated session
```

---

## 5. State Challenges

### Challenge: CSRF Tokens

Many forms require a CSRF token that changes per session/page.

```python
def get_csrf_token(session, url):
    """Extract CSRF token from a page."""
    response = session.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Try common CSRF field names
    for name in ["csrf_token", "_token", "csrfmiddlewaretoken", "authenticity_token"]:
        token = soup.select_one(f"input[name='{name}']")
        if token:
            return token["value"]
    
    # Try meta tag
    meta = soup.select_one("meta[name='csrf-token']")
    if meta:
        return meta["content"]
    
    return None

# Usage
csrf = get_csrf_token(session, "https://example.com/form")
session.post("https://example.com/submit", data={
    "csrf_token": csrf,
    "field1": "value1"
})
```

### Challenge: Session Expiration

Sessions expire. Handle gracefully:

```python
class AuthenticatedScraper:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.login()
    
    def login(self):
        # Perform login
        self.session.post("https://example.com/login", data={
            "username": self.username,
            "password": self.password
        })
    
    def fetch(self, url):
        response = self.session.get(url)
        
        # Check if session expired
        if response.status_code == 401 or "login" in response.url:
            print("Session expired, re-logging in...")
            self.login()
            response = self.session.get(url)
        
        return response
```

### Challenge: Multiple Cookies

Some sites use multiple cookies for different purposes:

```python
# After login, inspect all cookies
for cookie in session.cookies:
    print(f"{cookie.name}: {cookie.value[:20]}...")

# Typical cookie setup:
# - session_id: Main session identifier
# - csrf_token: CSRF protection
# - preferences: User preferences
# - tracking_id: Analytics
```

---

## 6. Cookies in Headless Browsers

### Playwright Cookie Management

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    
    # Navigate and let browser handle cookies naturally
    page.goto("https://example.com/login")
    page.fill("#username", "user")
    page.fill("#password", "pass")
    page.click("#submit")
    
    # Get all cookies
    cookies = context.cookies()
    for cookie in cookies:
        print(f"{cookie['name']}: {cookie['value']}")
    
    # Save cookies for later
    import json
    with open("cookies.json", "w") as f:
        json.dump(cookies, f)
    
    # Load cookies in new session
    context2 = browser.new_context()
    with open("cookies.json") as f:
        context2.add_cookies(json.load(f))
```

### Transfer Cookies Between Playwright and Requests

```python
from playwright.sync_api import sync_playwright
import requests

# Get cookies from Playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com/login")
    # ... perform login ...
    
    playwright_cookies = page.context.cookies()

# Transfer to requests session
session = requests.Session()
for cookie in playwright_cookies:
    session.cookies.set(
        cookie["name"],
        cookie["value"],
        domain=cookie.get("domain", ""),
        path=cookie.get("path", "/")
    )

# Now use requests for faster scraping
response = session.get("https://example.com/data")
```

---

## 7. Debugging Cookie Issues

### Inspect What's Being Sent

```python
response = session.get(url)

# What cookies were sent?
print("Request cookies:", response.request.headers.get("Cookie"))

# What cookies were received?
print("Response Set-Cookie:", response.headers.get("Set-Cookie"))

# Current session cookies
print("Session cookies:", dict(session.cookies))
```

### Common Issues

| Problem | Symptom | Solution |
|---------|---------|----------|
| Missing cookies | Always redirected to login | Check if cookies are being stored |
| Wrong domain | Cookies not sent | Verify cookie domain matches request domain |
| Expired cookies | Intermittent auth failures | Refresh session periodically |
| Missing CSRF | Form submission fails | Extract fresh token before each POST |
| Secure cookie over HTTP | Cookie not sent | Use HTTPS |
| Path mismatch | Cookie not sent to some URLs | Check cookie path attribute |

### Enable Debug Logging

```python
import logging
import http.client

# See all HTTP traffic including cookies
http.client.HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

# Now make request - will show all headers
session.get("https://example.com")
```

---

## 8. Best Practices

### Do's

```python
# ✅ Use sessions for related requests
session = requests.Session()

# ✅ Persist cookies for long-running scrapers
save_cookies(session.cookies)

# ✅ Handle session expiration gracefully
if is_logged_out(response):
    relogin()

# ✅ Extract CSRF tokens fresh before each form submission
csrf = get_csrf_from_page(session, form_url)
```

### Don'ts

```python
# ❌ Don't create new sessions for each request
for url in urls:
    requests.get(url)  # Loses cookies each time

# ❌ Don't hardcode session cookies that expire
cookies = {"session": "old_hardcoded_value"}  # Will expire

# ❌ Don't ignore Set-Cookie headers
response = requests.get(url)  # Not using session, cookies lost

# ❌ Don't share sessions across different accounts
session.login("user1")
session.login("user2")  # Overwrites user1's session
```

---

## Summary

| Concept | Purpose | Scraper Handling |
|---------|---------|------------------|
| **Cookie** | Store state client-side | Use `requests.Session()` |
| **Session** | Maintain logged-in state | Persist and refresh as needed |
| **CSRF Token** | Prevent forged requests | Extract from page before POST |
| **Set-Cookie** | Server sends new cookies | Handled automatically by Session |
| **Cookie Domain** | Control which sites receive cookie | Must match target domain |

### Quick Reference

```python
# Basic session usage
session = requests.Session()
session.get(url)  # Cookies handled automatically

# Check cookies
print(session.cookies.get_dict())

# Add cookie manually
session.cookies.set("name", "value", domain=".example.com")

# Save/load cookies
pickle.dump(session.cookies, open("cookies.pkl", "wb"))
session.cookies.update(pickle.load(open("cookies.pkl", "rb")))
```

---

*Next: [04_headers_user_agents.md](04_headers_user_agents.md) - Crafting headers that don't get you blocked*
