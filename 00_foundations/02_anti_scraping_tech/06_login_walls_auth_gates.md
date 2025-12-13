# Login Walls & Auth Gates

> **When Content Hides Behind Authentication**

Many valuable datasets are protected by login requirements. This document covers how to handle authenticated scraping responsibly.

---

## Types of Authentication Barriers

### 1. Hard Login Walls

Content completely inaccessible without account:

```
┌─────────────────────────────────┐
│  Please log in to continue     │
│                                │
│  Email: [__________________]   │
│  Password: [________________]  │
│                                │
│  [  Login  ]  [  Sign Up  ]   │
└─────────────────────────────────┘
```

Examples: Banking, enterprise SaaS, private communities

### 2. Soft Paywalls

Limited free access, full access requires payment:

```
You've read 3 of 5 free articles this month.
Subscribe for unlimited access.

[Continue with limited access] [Subscribe $9.99/mo]
```

Examples: News sites (NYT, WSJ), research databases

### 3. Registration Walls

Free account required but no payment:

```
Create a free account to view this content.
[Sign up with Google] [Sign up with Email]
```

Examples: LinkedIn, some forums, professional networks

### 4. Metered Access

Access granted up to a limit:

```python
# Tracking mechanisms
tracking = {
    "cookie": "articles_read=5",
    "ip_based": "requests_from_ip: 100",
    "fingerprint": "device_views: 10",
    "account": "monthly_views: 50",
}
```

---

## Authentication Methods

### Session-Based Auth

```
┌─────────────┐        ┌─────────────┐
│   Client    │        │   Server    │
└──────┬──────┘        └──────┬──────┘
       │                      │
       │  POST /login         │
       │  {user, pass}        │
       │─────────────────────▶│
       │                      │
       │  Set-Cookie:         │
       │  session=abc123      │
       │◀─────────────────────│
       │                      │
       │  GET /protected      │
       │  Cookie: session=abc │
       │─────────────────────▶│
       │                      │
       │  200 OK (content)    │
       │◀─────────────────────│
```

### Token-Based Auth (JWT)

```
┌─────────────┐        ┌─────────────┐
│   Client    │        │   Server    │
└──────┬──────┘        └──────┬──────┘
       │                      │
       │  POST /auth/login    │
       │  {user, pass}        │
       │─────────────────────▶│
       │                      │
       │  {"token": "eyJ..."}│
       │◀─────────────────────│
       │                      │
       │  GET /protected      │
       │  Authorization:      │
       │  Bearer eyJ...       │
       │─────────────────────▶│
       │                      │
       │  200 OK (content)    │
       │◀─────────────────────│
```

### OAuth 2.0

```
┌──────┐     ┌──────┐     ┌───────────┐
│ User │     │ App  │     │ Provider  │
└──┬───┘     └──┬───┘     └─────┬─────┘
   │            │               │
   │  Login     │               │
   │───────────▶│               │
   │            │  Redirect     │
   │◀───────────│───────────────│
   │            │               │
   │  Authorize at Provider     │
   │───────────────────────────▶│
   │            │               │
   │  Callback with code        │
   │◀───────────────────────────│
   │            │               │
   │            │  Exchange code│
   │            │──────────────▶│
   │            │               │
   │            │  Access token │
   │            │◀──────────────│
```

---

## Scraping with Authentication

### Basic Session Login

```python
import requests
from bs4 import BeautifulSoup

class AuthenticatedScraper:
    def __init__(self, login_url, username, password):
        self.session = requests.Session()
        self.login_url = login_url
        self.username = username
        self.password = password
        self.logged_in = False
    
    def login(self):
        """Perform login and store session cookies."""
        
        # Step 1: Get login page (for CSRF token)
        login_page = self.session.get(self.login_url)
        soup = BeautifulSoup(login_page.text, 'html.parser')
        
        # Step 2: Extract CSRF token
        csrf_token = self._extract_csrf(soup)
        
        # Step 3: Submit login form
        login_data = {
            'username': self.username,
            'password': self.password,
            'csrf_token': csrf_token,
        }
        
        response = self.session.post(
            self.login_url,
            data=login_data,
            headers={
                'Referer': self.login_url,
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        )
        
        # Step 4: Verify login success
        self.logged_in = self._verify_login(response)
        return self.logged_in
    
    def _extract_csrf(self, soup):
        """Extract CSRF token from page."""
        # Try common patterns
        csrf_input = soup.find('input', {'name': ['csrf_token', '_token', 
                                                   'authenticity_token',
                                                   'csrfmiddlewaretoken']})
        if csrf_input:
            return csrf_input.get('value')
        
        csrf_meta = soup.find('meta', {'name': 'csrf-token'})
        if csrf_meta:
            return csrf_meta.get('content')
        
        return None
    
    def _verify_login(self, response):
        """Check if login was successful."""
        # Check for success indicators
        if 'logout' in response.text.lower():
            return True
        if 'dashboard' in response.url:
            return True
        if response.status_code == 200 and 'login' not in response.url:
            return True
        return False
    
    def get(self, url):
        """Make authenticated GET request."""
        if not self.logged_in:
            self.login()
        return self.session.get(url)

# Usage
scraper = AuthenticatedScraper(
    login_url="https://example.com/login",
    username="myuser",
    password="mypass"
)

if scraper.login():
    response = scraper.get("https://example.com/protected/data")
    print(response.text)
```

### JWT/API Token Auth

```python
class TokenAuthScraper:
    def __init__(self, api_base, username, password):
        self.api_base = api_base
        self.username = username
        self.password = password
        self.token = None
        self.token_expiry = 0
    
    def authenticate(self):
        """Get authentication token."""
        response = requests.post(
            f"{self.api_base}/auth/login",
            json={
                'username': self.username,
                'password': self.password,
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data['access_token']
            self.token_expiry = time.time() + data.get('expires_in', 3600)
            return True
        return False
    
    def ensure_token(self):
        """Ensure we have a valid token."""
        if not self.token or time.time() >= self.token_expiry - 60:
            self.authenticate()
    
    def get(self, endpoint):
        """Make authenticated API request."""
        self.ensure_token()
        
        return requests.get(
            f"{self.api_base}{endpoint}",
            headers={
                'Authorization': f'Bearer {self.token}',
                'Accept': 'application/json',
            }
        )
```

### Browser-Based Login (Complex Sites)

```python
from playwright.sync_api import sync_playwright
import requests

def login_with_browser(login_url, username, password):
    """Handle complex login flows with browser automation."""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Navigate to login
        page.goto(login_url)
        
        # Fill credentials
        page.fill('input[name="username"], input[type="email"]', username)
        page.fill('input[name="password"], input[type="password"]', password)
        
        # Click login button
        page.click('button[type="submit"], input[type="submit"]')
        
        # Wait for navigation
        page.wait_for_url(lambda url: 'login' not in url, timeout=30000)
        
        # Extract cookies for requests library
        cookies = context.cookies()
        
        browser.close()
        
        # Convert to requests format
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(
                cookie['name'],
                cookie['value'],
                domain=cookie.get('domain'),
                path=cookie.get('path', '/')
            )
        
        return session

# Usage
session = login_with_browser(
    "https://complex-site.com/login",
    "myuser",
    "mypass"
)

# Now use session for fast requests
response = session.get("https://complex-site.com/data")
```

---

## Handling Common Challenges

### Challenge 1: CAPTCHA on Login

```python
def login_with_captcha(login_url, username, password, captcha_service):
    session = requests.Session()
    
    # Get login page
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.text, 'html.parser')
    
    # Extract CAPTCHA parameters
    site_key = soup.find('div', class_='g-recaptcha')['data-sitekey']
    
    # Solve CAPTCHA via service
    captcha_token = captcha_service.solve_recaptcha(site_key, login_url)
    
    # Submit with CAPTCHA solution
    response = session.post(login_url, data={
        'username': username,
        'password': password,
        'g-recaptcha-response': captcha_token,
    })
    
    return session
```

### Challenge 2: Multi-Factor Authentication

```python
def login_with_mfa(login_url, username, password, mfa_handler):
    session = requests.Session()
    
    # Step 1: Initial login
    response = session.post(login_url, data={
        'username': username,
        'password': password,
    })
    
    # Step 2: Check if MFA required
    if 'mfa' in response.url or 'verify' in response.text.lower():
        # Get MFA code (from authenticator app, email, SMS)
        mfa_code = mfa_handler.get_code()
        
        # Submit MFA
        response = session.post(
            response.url,  # MFA verification URL
            data={'code': mfa_code}
        )
    
    return session

# MFA handlers
class TOTPHandler:
    """Handle TOTP (Google Authenticator) codes."""
    def __init__(self, secret):
        self.secret = secret
    
    def get_code(self):
        import pyotp
        totp = pyotp.TOTP(self.secret)
        return totp.now()

class EmailMFAHandler:
    """Handle email-based MFA."""
    def __init__(self, email_checker):
        self.email_checker = email_checker
    
    def get_code(self):
        # Wait for email with code
        time.sleep(10)
        return self.email_checker.get_latest_code()
```

### Challenge 3: Rate-Limited Login Attempts

```python
class RateLimitedLogin:
    def __init__(self, max_attempts=3, cooldown=300):
        self.max_attempts = max_attempts
        self.cooldown = cooldown
        self.attempts = 0
        self.last_attempt = 0
    
    def login(self, session, url, credentials):
        # Check cooldown
        if self.attempts >= self.max_attempts:
            wait_time = self.cooldown - (time.time() - self.last_attempt)
            if wait_time > 0:
                print(f"Rate limited. Waiting {wait_time:.0f}s...")
                time.sleep(wait_time)
                self.attempts = 0
        
        self.attempts += 1
        self.last_attempt = time.time()
        
        response = session.post(url, data=credentials)
        
        if 'too many attempts' in response.text.lower():
            self.attempts = self.max_attempts
            return self.login(session, url, credentials)  # Retry after cooldown
        
        return response
```

### Challenge 4: OAuth Login

```python
def oauth_login(client_id, client_secret, redirect_uri):
    """Handle OAuth 2.0 flow."""
    
    # Step 1: Get authorization URL
    auth_url = (
        f"https://provider.com/oauth/authorize?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=read"
    )
    
    # Step 2: User authorizes (browser automation or manual)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(auth_url)
        
        # Wait for redirect with code
        page.wait_for_url(f"{redirect_uri}*")
        callback_url = page.url
        browser.close()
    
    # Step 3: Extract authorization code
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(callback_url)
    code = parse_qs(parsed.query)['code'][0]
    
    # Step 4: Exchange code for token
    response = requests.post(
        "https://provider.com/oauth/token",
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
        }
    )
    
    return response.json()['access_token']
```

---

## Bypassing Soft Paywalls

### Method 1: Cookie Manipulation

```python
def reset_article_counter(session, domain):
    """Reset metered paywall counter."""
    
    # Common counter cookies
    counter_cookies = [
        'article_count', 'articles_read', 'views',
        'meter', 'metering', 'paywall_views',
    ]
    
    for cookie in counter_cookies:
        session.cookies.set(cookie, '0', domain=domain)
```

### Method 2: Incognito/Fresh Session

```python
def fresh_session_per_article(urls):
    """Use fresh session for each article."""
    
    results = []
    for url in urls:
        # New session = new meter
        session = requests.Session()
        session.headers.update(BROWSER_HEADERS)
        
        response = session.get(url)
        results.append(response.text)
    
    return results
```

### Method 3: Referrer Manipulation

Some paywalls allow access from search engines:

```python
def bypass_with_referrer(url):
    """Try accessing via search engine referrer."""
    
    headers = BROWSER_HEADERS.copy()
    headers['Referer'] = 'https://www.google.com/'
    
    response = requests.get(url, headers=headers)
    return response
```

### Method 4: Archive Services

```python
def get_from_archive(url):
    """Try to get content from web archives."""
    
    archives = [
        f"https://web.archive.org/web/{url}",
        f"https://archive.is/newest/{url}",
        f"https://webcache.googleusercontent.com/search?q=cache:{url}",
    ]
    
    for archive_url in archives:
        try:
            response = requests.get(archive_url, timeout=10)
            if response.status_code == 200:
                return response.text
        except:
            continue
    
    return None
```

---

## Session Management Best Practices

### Persist Sessions

```python
import pickle
import os

class PersistentSession:
    def __init__(self, session_file, login_func):
        self.session_file = session_file
        self.login_func = login_func
        self.session = self._load_or_create()
    
    def _load_or_create(self):
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'rb') as f:
                    return pickle.load(f)
            except:
                pass
        return requests.Session()
    
    def save(self):
        with open(self.session_file, 'wb') as f:
            pickle.dump(self.session, f)
    
    def ensure_logged_in(self):
        # Test if session is valid
        test_response = self.session.get("https://site.com/profile")
        
        if 'login' in test_response.url:
            self.session = self.login_func()
            self.save()
    
    def get(self, url):
        self.ensure_logged_in()
        response = self.session.get(url)
        self.save()  # Save any new cookies
        return response
```

### Handle Session Expiration

```python
class SessionManager:
    def __init__(self, credentials, session_lifetime=3600):
        self.credentials = credentials
        self.session_lifetime = session_lifetime
        self.session = None
        self.session_created = 0
    
    def get_session(self):
        now = time.time()
        
        # Check if session expired
        if not self.session or now - self.session_created > self.session_lifetime:
            self.session = self._create_new_session()
            self.session_created = now
        
        return self.session
    
    def _create_new_session(self):
        session = requests.Session()
        # Perform login
        login(session, self.credentials)
        return session
```

---

## Ethical Considerations

### When NOT to Bypass Auth

- ❌ Content you don't have rights to access
- ❌ Violating Terms of Service for commercial gain
- ❌ Accessing others' private data
- ❌ Circumventing payment for paid content

### Acceptable Scenarios

- ✅ Accessing your own data
- ✅ Research with proper authorization
- ✅ Public data behind registration
- ✅ Archival purposes (check ToS)

---

## Summary

| Auth Type | Scraping Approach |
|-----------|-------------------|
| **Session cookies** | requests.Session() + login |
| **JWT tokens** | Store and refresh tokens |
| **OAuth** | Browser automation for flow |
| **MFA** | TOTP library or manual |
| **Soft paywall** | Cookie reset, fresh sessions |
| **Complex flows** | Full browser automation |

### Key Takeaways

1. **Use requests.Session()** - Maintains cookies automatically
2. **Handle CSRF tokens** - Extract before form submission
3. **Verify login success** - Don't assume it worked
4. **Persist sessions** - Don't login repeatedly
5. **Handle expiration** - Re-authenticate when needed
6. **Be ethical** - Respect access restrictions

---

*Next: [07_dynamic_content_obfuscation.md](07_dynamic_content_obfuscation.md) - When sites deliberately hide data*
