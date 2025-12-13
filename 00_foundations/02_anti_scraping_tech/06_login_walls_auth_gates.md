# Login Walls & Auth Gates

> **Getting Past the "Please Sign In" Barrier**

Many valuable data sources require authentication. This document covers strategies for handling login walls, session management, and maintaining authenticated access.

---

## Types of Authentication Barriers

### 1. Hard Login Walls

Content completely inaccessible without authentication:

```
┌─────────────────────────────────┐
│         LOGIN REQUIRED          │
│                                 │
│  Email: [________________]      │
│  Pass:  [________________]      │
│                                 │
│  [Sign In]  [Create Account]    │
│                                 │
└─────────────────────────────────┘

No content visible until authenticated.
```

**Examples:** LinkedIn, Facebook, Banking sites

### 2. Soft Paywalls / Metered Access

Limited free access before login required:

```
Article 1: ✓ Readable
Article 2: ✓ Readable  
Article 3: ✓ Readable
Article 4: 🔒 "Subscribe to continue reading"
```

**Examples:** NYTimes, Medium, news sites

### 3. Progressive Disclosure

More data revealed after authentication:

```
Without login:
├── Product name ✓
├── Basic description ✓
└── Price: "Sign in to see pricing"

With login:
├── Product name ✓
├── Full description ✓
├── Price: $99.99 ✓
└── Inventory: 45 in stock ✓
```

**Examples:** B2B sites, wholesale platforms

### 4. API Authentication

APIs requiring keys or tokens:

```python
# Without auth
requests.get("https://api.site.com/data")
# 401 Unauthorized

# With auth
requests.get(
    "https://api.site.com/data",
    headers={"Authorization": "Bearer TOKEN"}
)
# 200 OK
```

---

## Authentication Methods

### Method 1: Form-Based Login

Standard username/password form submission.

```python
import requests
from bs4 import BeautifulSoup

def form_login(login_url, username, password):
    session = requests.Session()
    
    # Step 1: Get login page
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.text, 'html.parser')
    
    # Step 2: Find form and extract hidden fields
    form = soup.find('form', {'id': 'login-form'}) or soup.find('form')
    
    form_data = {}
    for input_tag in form.find_all('input'):
        name = input_tag.get('name')
        value = input_tag.get('value', '')
        if name:
            form_data[name] = value
    
    # Step 3: Add credentials
    # Find the right field names (varies by site)
    username_field = None
    password_field = None
    
    for name in form_data.keys():
        if any(x in name.lower() for x in ['user', 'email', 'login']):
            username_field = name
        if any(x in name.lower() for x in ['pass', 'pwd']):
            password_field = name
    
    form_data[username_field] = username
    form_data[password_field] = password
    
    # Step 4: Find form action URL
    action = form.get('action', login_url)
    if action.startswith('/'):
        from urllib.parse import urljoin
        action = urljoin(login_url, action)
    
    # Step 5: Submit
    response = session.post(
        action,
        data=form_data,
        headers={
            'Referer': login_url,
            'Origin': login_url.rsplit('/', 1)[0]
        }
    )
    
    # Step 6: Verify success
    if is_login_successful(response, session):
        return session
    else:
        raise Exception("Login failed")

def is_login_successful(response, session):
    """Check if login worked."""
    # Check URL (often redirects to dashboard)
    if 'login' not in response.url.lower():
        return True
    
    # Check for error messages
    if 'invalid' in response.text.lower():
        return False
    if 'incorrect' in response.text.lower():
        return False
    
    # Check for session cookie
    if any('session' in c.name.lower() for c in session.cookies):
        return True
    
    return False
```

### Method 2: JSON API Login

Modern SPAs often use JSON API endpoints:

```python
def api_login(api_url, email, password):
    session = requests.Session()
    
    response = session.post(
        f"{api_url}/auth/login",
        json={
            "email": email,
            "password": password
        },
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        
        # Token might be in response body
        if 'access_token' in data:
            session.headers['Authorization'] = f"Bearer {data['access_token']}"
        
        # Or might be set as cookie automatically
        return session
    
    raise Exception(f"Login failed: {response.text}")
```

### Method 3: OAuth Flow

For sites using OAuth (Google, Facebook, etc.):

```python
# OAuth is complex - often easier to use browser automation
from playwright.sync_api import sync_playwright

def oauth_login(site_url, oauth_provider='google'):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Must see OAuth popup
        context = browser.new_context()
        page = context.new_page()
        
        # Go to site login
        page.goto(site_url)
        
        # Click OAuth button
        page.click(f'button:has-text("Sign in with {oauth_provider}")')
        
        # Handle OAuth popup
        with page.expect_popup() as popup_info:
            popup = popup_info.value
            
            # Fill Google/Facebook credentials
            popup.fill('input[type="email"]', 'your@email.com')
            popup.click('button:has-text("Next")')
            popup.fill('input[type="password"]', 'password')
            popup.click('button:has-text("Sign in")')
            
            # Popup closes, main page is now logged in
        
        # Wait for login to complete
        page.wait_for_url("**/dashboard**")
        
        # Extract cookies
        cookies = context.cookies()
        browser.close()
        return cookies
```

### Method 4: Browser Automation Login

For complex login flows (CAPTCHA, 2FA, JavaScript):

```python
from playwright.sync_api import sync_playwright

def browser_login(login_url, username, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto(login_url)
        
        # Fill form
        page.fill('input[name="username"], input[type="email"]', username)
        page.fill('input[name="password"], input[type="password"]', password)
        
        # Click submit
        page.click('button[type="submit"], input[type="submit"]')
        
        # Wait for navigation
        page.wait_for_load_state('networkidle')
        
        # Check if login successful
        if 'login' in page.url.lower():
            # Still on login page - failed
            error = page.query_selector('.error-message')
            raise Exception(f"Login failed: {error.inner_text() if error else 'Unknown'}")
        
        # Extract session for requests
        cookies = context.cookies()
        browser.close()
        
        return cookies_to_session(cookies)

def cookies_to_session(cookies):
    """Convert Playwright cookies to requests session."""
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(
            cookie['name'],
            cookie['value'],
            domain=cookie.get('domain'),
            path=cookie.get('path', '/')
        )
    return session
```

---

## Handling CSRF Tokens

### What is CSRF?

Cross-Site Request Forgery tokens prevent unauthorized form submissions:

```html
<form method="POST" action="/login">
    <input type="hidden" name="csrf_token" value="abc123xyz789">
    <input type="text" name="username">
    <input type="password" name="password">
    <button type="submit">Login</button>
</form>
```

### Extracting CSRF Tokens

```python
def get_csrf_token(session, url):
    """Extract CSRF token from page."""
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Common locations
    
    # 1. Hidden input field
    csrf_input = soup.find('input', {'name': ['csrf_token', '_token', 
                                               'csrfmiddlewaretoken', 
                                               'authenticity_token',
                                               '_csrf']})
    if csrf_input:
        return csrf_input.get('value')
    
    # 2. Meta tag
    csrf_meta = soup.find('meta', {'name': ['csrf-token', '_csrf', 'csrf']})
    if csrf_meta:
        return csrf_meta.get('content')
    
    # 3. In JavaScript (regex)
    import re
    patterns = [
        r'csrf[_-]?token["\']?\s*[:=]\s*["\']([^"\']+)["\']',
        r'_csrf["\']?\s*[:=]\s*["\']([^"\']+)["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, response.text, re.I)
        if match:
            return match.group(1)
    
    # 4. In cookies
    for cookie in session.cookies:
        if 'csrf' in cookie.name.lower():
            return cookie.value
    
    return None
```

---

## Handling Two-Factor Authentication

### Manual 2FA Intervention

```python
def login_with_2fa(login_url, username, password, get_2fa_code):
    """
    get_2fa_code: function that returns 2FA code (could prompt user)
    """
    session = requests.Session()
    
    # Step 1: Normal login
    csrf = get_csrf_token(session, login_url)
    response = session.post(login_url, data={
        'username': username,
        'password': password,
        'csrf_token': csrf
    })
    
    # Step 2: Check if 2FA required
    if '2fa' in response.url or 'verify' in response.url:
        # Get 2FA code from user or authenticator
        code = get_2fa_code()  # e.g., input("Enter 2FA code: ")
        
        # Submit 2FA
        csrf = get_csrf_token(session, response.url)
        response = session.post(response.url, data={
            'code': code,
            'csrf_token': csrf
        })
    
    return session

# Usage with manual input
session = login_with_2fa(
    "https://site.com/login",
    "username",
    "password",
    lambda: input("Enter 2FA code: ")
)
```

### Automated TOTP

```python
import pyotp

def login_with_totp(login_url, username, password, totp_secret):
    """Automated 2FA using TOTP secret."""
    
    session = requests.Session()
    
    # Normal login
    response = session.post(login_url, data={
        'username': username,
        'password': password
    })
    
    if '2fa' in response.url:
        # Generate TOTP code
        totp = pyotp.TOTP(totp_secret)
        code = totp.now()
        
        # Submit
        response = session.post(response.url, data={'code': code})
    
    return session
```

---

## Session Persistence

### Saving Sessions

```python
import pickle
import os
from datetime import datetime, timedelta

SESSION_FILE = 'session.pkl'

def save_session(session, metadata=None):
    """Save session to file."""
    data = {
        'cookies': session.cookies,
        'headers': dict(session.headers),
        'saved_at': datetime.now(),
        'metadata': metadata
    }
    with open(SESSION_FILE, 'wb') as f:
        pickle.dump(data, f)

def load_session(max_age_hours=24):
    """Load session from file if not expired."""
    if not os.path.exists(SESSION_FILE):
        return None
    
    with open(SESSION_FILE, 'rb') as f:
        data = pickle.load(f)
    
    # Check expiration
    if datetime.now() - data['saved_at'] > timedelta(hours=max_age_hours):
        return None
    
    session = requests.Session()
    session.cookies = data['cookies']
    session.headers.update(data['headers'])
    
    return session
```

### Session Validation

```python
def validate_session(session, test_url):
    """Check if session is still authenticated."""
    response = session.get(test_url)
    
    # Check various indicators
    if response.status_code == 401:
        return False
    if 'login' in response.url.lower():
        return False
    if 'sign in' in response.text.lower()[:1000]:
        return False
    
    return True

def get_or_create_session(credentials, test_url):
    """Get existing session or create new one."""
    
    # Try loading saved session
    session = load_session()
    
    if session and validate_session(session, test_url):
        print("Using saved session")
        return session
    
    # Create new session
    print("Creating new session")
    session = perform_login(**credentials)
    save_session(session)
    
    return session
```

---

## Handling Metered Paywalls

### Cookie Reset

```python
def reset_article_count():
    """Clear cookies that track article count."""
    session = requests.Session()
    # Start fresh - no cookies
    return session
```

### Incognito-Style Requests

```python
def anonymous_request(url):
    """Make request without persistent identity."""
    session = requests.Session()
    
    # Rotate IP if possible
    proxy = get_random_proxy()
    
    response = session.get(
        url,
        proxies={'http': proxy, 'https': proxy},
        headers=get_browser_headers()
    )
    
    return response
```

### Google Cache/Archive

```python
def get_cached_version(url):
    """Try to get content from caches."""
    
    # Google Cache
    google_cache = f"https://webcache.googleusercontent.com/search?q=cache:{url}"
    
    # Wayback Machine
    wayback_api = f"https://archive.org/wayback/available?url={url}"
    wayback_response = requests.get(wayback_api).json()
    
    if wayback_response.get('archived_snapshots', {}).get('closest'):
        wayback_url = wayback_response['archived_snapshots']['closest']['url']
        return requests.get(wayback_url)
    
    return None
```

---

## Account Management

### Multiple Accounts

```python
class AccountPool:
    def __init__(self, credentials_list):
        self.accounts = credentials_list
        self.sessions = {}
        self.usage = {c['username']: 0 for c in credentials_list}
    
    def get_session(self):
        """Get least-used account session."""
        # Find account with lowest usage
        username = min(self.usage, key=self.usage.get)
        
        # Create session if needed
        if username not in self.sessions:
            creds = next(c for c in self.accounts if c['username'] == username)
            self.sessions[username] = perform_login(**creds)
        
        self.usage[username] += 1
        return self.sessions[username]
    
    def mark_blocked(self, session):
        """Mark account as blocked, remove from pool."""
        for username, sess in self.sessions.items():
            if sess == session:
                del self.sessions[username]
                self.usage[username] = float('inf')
                break
```

---

## Summary

| Auth Type | Complexity | Best Approach |
|-----------|------------|---------------|
| **Form login** | Low | requests + BeautifulSoup |
| **JSON API** | Low | requests |
| **OAuth** | High | Browser automation |
| **2FA (manual)** | Medium | Human in loop |
| **2FA (TOTP)** | Medium | pyotp library |
| **CAPTCHA on login** | High | Solving service + browser |

### Key Takeaways

1. **Extract hidden fields** - CSRF tokens, form data
2. **Follow redirects** - Login often involves multiple steps
3. **Verify success** - Don't assume login worked
4. **Persist sessions** - Avoid repeated logins
5. **Validate before use** - Sessions expire
6. **Handle 2FA gracefully** - Automate TOTP when possible

---

*Next: [07_dynamic_content_obfuscation.md](07_dynamic_content_obfuscation.md) - Anti-scraping code techniques*
