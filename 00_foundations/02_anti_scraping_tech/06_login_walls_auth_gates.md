# Login Walls & Authentication Gates

> **Navigating Authentication Barriers in Web Scraping**

Many valuable data sources require authentication. This document covers every authentication pattern you'll encounter and provides ethical, practical approaches to handling them.

---

## The Authentication Landscape

```
Authentication Complexity Spectrum:

Simple ──────────────────────────────────────────────▶ Complex

Basic         Session        OAuth 2.0      SSO          MFA/2FA
Form Login    Cookies        Tokens         (SAML/OIDC)  TOTP/SMS
    │            │              │              │            │
    ▼            ▼              ▼              ▼            ▼
Username     Maintain       Access +       Multiple     Human
+ Password   state          Refresh        providers    verification
                            tokens
```

---

## 1. Basic Form Authentication

### 1.1 Understanding Login Forms

```html
<!-- Typical login form structure -->
<form action="/login" method="POST">
    <!-- Visible fields -->
    <input type="text" name="username" placeholder="Username">
    <input type="password" name="password" placeholder="Password">
    
    <!-- Hidden fields (important!) -->
    <input type="hidden" name="csrf_token" value="a1b2c3d4e5f6...">
    <input type="hidden" name="_redirect" value="/dashboard">
    
    <!-- Honeypot (trap for bots) -->
    <input type="text" name="email2" style="display:none">
    
    <!-- Remember me -->
    <input type="checkbox" name="remember" value="1"> Remember me
    
    <button type="submit">Login</button>
</form>
```

### 1.2 Basic Login Implementation

```python
import requests
from bs4 import BeautifulSoup

class BasicLoginScraper:
    """Handle basic form-based authentication."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def login(self, login_url, username, password):
        """Perform login and return success status."""
        
        # Step 1: Get login page to extract tokens
        response = self.session.get(login_url)
        
        # Step 2: Extract CSRF token and other hidden fields
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form')
        
        if not form:
            raise Exception("No login form found")
        
        # Get form action URL
        action = form.get('action', login_url)
        if not action.startswith('http'):
            from urllib.parse import urljoin
            action = urljoin(login_url, action)
        
        # Extract all hidden fields
        hidden_fields = {}
        for hidden in form.find_all('input', type='hidden'):
            name = hidden.get('name')
            value = hidden.get('value', '')
            if name:
                hidden_fields[name] = value
        
        # Build login payload
        payload = {
            **hidden_fields,  # Include CSRF token and other hidden fields
            'username': username,  # Adjust field names as needed
            'password': password,
        }
        
        # Check for common field name variations
        username_field = self._find_field_name(form, ['username', 'email', 'user', 'login', 'user_email', 'user_login'])
        password_field = self._find_field_name(form, ['password', 'pass', 'passwd', 'user_password'])
        
        if username_field:
            payload[username_field] = username
        if password_field:
            payload[password_field] = password
        
        # Step 3: Submit login form
        response = self.session.post(
            action,
            data=payload,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': login_url,
                'Origin': self._get_origin(login_url),
            },
            allow_redirects=True
        )
        
        # Step 4: Verify login success
        return self._verify_login(response)
    
    def _find_field_name(self, form, possible_names):
        """Find the actual field name from possible variations."""
        for name in possible_names:
            field = form.find('input', {'name': name})
            if field:
                return name
            # Also check by ID
            field = form.find('input', {'id': name})
            if field and field.get('name'):
                return field.get('name')
        return None
    
    def _get_origin(self, url):
        """Extract origin from URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def _verify_login(self, response):
        """Verify if login was successful."""
        # Check for common success indicators
        success_indicators = [
            'dashboard',
            'welcome',
            'logout',
            'my account',
            'profile',
        ]
        
        # Check for failure indicators
        failure_indicators = [
            'invalid',
            'incorrect',
            'failed',
            'error',
            'wrong password',
            'try again',
        ]
        
        content_lower = response.text.lower()
        
        # Check URL for success
        if any(ind in response.url.lower() for ind in success_indicators):
            return True
        
        # Check content for failure
        if any(ind in content_lower for ind in failure_indicators):
            return False
        
        # Check for logout link (indicates logged in)
        soup = BeautifulSoup(response.text, 'html.parser')
        logout_link = soup.find('a', href=lambda x: x and 'logout' in x.lower())
        if logout_link:
            return True
        
        # Check cookies for session
        session_cookies = ['session', 'sessionid', 'sess', 'auth', 'token']
        for cookie_name in session_cookies:
            for cookie in self.session.cookies:
                if cookie_name in cookie.name.lower():
                    return True
        
        return False
    
    def get_authenticated_page(self, url):
        """Fetch page with authenticated session."""
        return self.session.get(url)
    
    def save_session(self, filepath):
        """Save session cookies for reuse."""
        import pickle
        with open(filepath, 'wb') as f:
            pickle.dump(self.session.cookies, f)
    
    def load_session(self, filepath):
        """Load previously saved session."""
        import pickle
        with open(filepath, 'rb') as f:
            self.session.cookies.update(pickle.load(f))

# Usage
scraper = BasicLoginScraper()
if scraper.login("https://example.com/login", "myuser", "mypass"):
    print("Login successful!")
    response = scraper.get_authenticated_page("https://example.com/protected-data")
    print(response.text)
else:
    print("Login failed!")
```

### 1.3 Handling CSRF Tokens

```python
class CSRFHandler:
    """Handle various CSRF token implementations."""
    
    @staticmethod
    def extract_csrf_from_html(html, patterns=None):
        """Extract CSRF token from HTML."""
        
        if patterns is None:
            patterns = [
                # Hidden input patterns
                {'tag': 'input', 'attrs': {'name': 'csrf_token'}},
                {'tag': 'input', 'attrs': {'name': '_csrf'}},
                {'tag': 'input', 'attrs': {'name': 'csrfmiddlewaretoken'}},
                {'tag': 'input', 'attrs': {'name': '_token'}},
                {'tag': 'input', 'attrs': {'name': 'authenticity_token'}},
                {'tag': 'input', 'attrs': {'name': '__RequestVerificationToken'}},
                
                # Meta tag patterns
                {'tag': 'meta', 'attrs': {'name': 'csrf-token'}},
                {'tag': 'meta', 'attrs': {'name': '_csrf'}},
            ]
        
        soup = BeautifulSoup(html, 'html.parser')
        
        for pattern in patterns:
            element = soup.find(pattern['tag'], pattern['attrs'])
            if element:
                # Get value from input or content from meta
                token = element.get('value') or element.get('content')
                if token:
                    return {
                        'name': list(pattern['attrs'].values())[0],
                        'value': token
                    }
        
        # Try regex for embedded tokens
        import re
        regex_patterns = [
            r'csrf[_-]?token["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'_csrf["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'"csrfToken"\s*:\s*"([^"]+)"',
        ]
        
        for pattern in regex_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return {'name': 'csrf_token', 'value': match.group(1)}
        
        return None
    
    @staticmethod
    def extract_csrf_from_cookies(cookies):
        """Some sites store CSRF token in cookies."""
        csrf_cookie_names = ['csrf', 'csrftoken', '_csrf', 'XSRF-TOKEN']
        
        for cookie in cookies:
            if any(name in cookie.name.lower() for name in csrf_cookie_names):
                return {'name': cookie.name, 'value': cookie.value}
        
        return None
```

---

## 2. Session Management

### 2.1 Understanding Sessions

```
Session Lifecycle:

1. Initial Request          2. Login                    3. Authenticated Requests
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ GET /login      │         │ POST /login     │         │ GET /dashboard  │
│                 │         │ username=...    │         │ Cookie: sess=X  │
│ Response:       │         │ password=...    │         │                 │
│ Set-Cookie:     │         │                 │         │ Response:       │
│ sess=abc123     │         │ Response:       │         │ Protected data  │
└─────────────────┘         │ Set-Cookie:     │         └─────────────────┘
                            │ sess=xyz789     │
                            │ (new session)   │
                            └─────────────────┘
```

### 2.2 Session Persistence

```python
import pickle
import json
from datetime import datetime, timedelta
from pathlib import Path

class SessionManager:
    """Manage and persist authenticated sessions."""
    
    def __init__(self, storage_dir="./sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    def save_session(self, session, site_name, metadata=None):
        """Save session with metadata."""
        session_data = {
            'cookies': [
                {
                    'name': c.name,
                    'value': c.value,
                    'domain': c.domain,
                    'path': c.path,
                    'expires': c.expires,
                    'secure': c.secure,
                }
                for c in session.cookies
            ],
            'headers': dict(session.headers),
            'metadata': metadata or {},
            'saved_at': datetime.now().isoformat(),
        }
        
        filepath = self.storage_dir / f"{site_name}_session.json"
        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return filepath
    
    def load_session(self, site_name, max_age_hours=24):
        """Load session if valid and not expired."""
        filepath = self.storage_dir / f"{site_name}_session.json"
        
        if not filepath.exists():
            return None
        
        with open(filepath, 'r') as f:
            session_data = json.load(f)
        
        # Check session age
        saved_at = datetime.fromisoformat(session_data['saved_at'])
        if datetime.now() - saved_at > timedelta(hours=max_age_hours):
            filepath.unlink()  # Delete expired session
            return None
        
        # Rebuild session
        session = requests.Session()
        
        # Restore cookies
        for cookie_data in session_data['cookies']:
            session.cookies.set(
                cookie_data['name'],
                cookie_data['value'],
                domain=cookie_data['domain'],
                path=cookie_data['path']
            )
        
        # Restore headers
        session.headers.update(session_data['headers'])
        
        return session
    
    def is_session_valid(self, session, test_url):
        """Test if session is still authenticated."""
        try:
            response = session.get(test_url, allow_redirects=False)
            
            # If redirected to login, session invalid
            if response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location', '')
                if 'login' in location.lower() or 'signin' in location.lower():
                    return False
            
            # If 401 or 403, session invalid
            if response.status_code in [401, 403]:
                return False
            
            return True
        except:
            return False

class AuthenticatedScraper:
    """Scraper with automatic session management."""
    
    def __init__(self, site_name):
        self.site_name = site_name
        self.session_manager = SessionManager()
        self.session = None
    
    def ensure_logged_in(self, login_url, credentials, test_url):
        """Ensure we have a valid authenticated session."""
        
        # Try to load existing session
        self.session = self.session_manager.load_session(self.site_name)
        
        if self.session and self.session_manager.is_session_valid(self.session, test_url):
            print("Using existing session")
            return True
        
        # Need to login
        print("Logging in...")
        self.session = requests.Session()
        
        # Perform login (implementation depends on site)
        success = self._perform_login(login_url, credentials)
        
        if success:
            self.session_manager.save_session(
                self.session,
                self.site_name,
                metadata={'username': credentials.get('username')}
            )
        
        return success
    
    def _perform_login(self, login_url, credentials):
        """Override this for site-specific login logic."""
        raise NotImplementedError
```

### 2.3 Handling Session Expiration

```python
class SessionAwareScraper:
    """Automatically handle session expiration during scraping."""
    
    def __init__(self, login_func, max_retries=3):
        self.login_func = login_func
        self.session = None
        self.max_retries = max_retries
    
    def get(self, url, **kwargs):
        """GET request with automatic re-authentication."""
        return self._request_with_retry('GET', url, **kwargs)
    
    def post(self, url, **kwargs):
        """POST request with automatic re-authentication."""
        return self._request_with_retry('POST', url, **kwargs)
    
    def _request_with_retry(self, method, url, **kwargs):
        """Make request, re-authenticate if needed."""
        
        for attempt in range(self.max_retries):
            if not self.session:
                self.session = self.login_func()
            
            response = self.session.request(method, url, **kwargs)
            
            if self._is_session_expired(response):
                print(f"Session expired, re-authenticating (attempt {attempt + 1})")
                self.session = None  # Force re-login
                continue
            
            return response
        
        raise Exception(f"Failed after {self.max_retries} authentication attempts")
    
    def _is_session_expired(self, response):
        """Detect if response indicates session expiration."""
        
        # Check status codes
        if response.status_code in [401, 403]:
            return True
        
        # Check for login redirect
        if response.status_code in [301, 302, 303, 307, 308]:
            location = response.headers.get('Location', '').lower()
            if any(x in location for x in ['login', 'signin', 'auth']):
                return True
        
        # Check response content
        expiration_phrases = [
            'session expired',
            'please log in',
            'authentication required',
            'login required',
        ]
        content_lower = response.text.lower()
        if any(phrase in content_lower for phrase in expiration_phrases):
            return True
        
        return False
```

---

## 3. OAuth 2.0 Authentication

### 3.1 OAuth 2.0 Flows

```
OAuth 2.0 Authorization Code Flow:

┌──────────┐                               ┌──────────────┐
│  Your    │                               │ Auth Server  │
│  App     │                               │ (Google,etc) │
└────┬─────┘                               └──────┬───────┘
     │                                            │
     │ 1. Redirect user to authorization          │
     │ ──────────────────────────────────────────▶│
     │    /authorize?                             │
     │      client_id=xxx&                        │
     │      redirect_uri=xxx&                     │
     │      scope=xxx&                            │
     │      state=xxx                             │
     │                                            │
     │ 2. User logs in and grants permission      │
     │                                            │
     │ 3. Redirect back with authorization code   │
     │◀────────────────────────────────────────── │
     │    /callback?code=xxx&state=xxx            │
     │                                            │
     │ 4. Exchange code for tokens                │
     │ ──────────────────────────────────────────▶│
     │    POST /token                             │
     │      code=xxx&                             │
     │      client_id=xxx&                        │
     │      client_secret=xxx                     │
     │                                            │
     │ 5. Receive access token + refresh token    │
     │◀────────────────────────────────────────── │
     │    { access_token, refresh_token }         │
     │                                            │
```

### 3.2 Handling OAuth in Scraping

```python
from urllib.parse import urlencode, parse_qs, urlparse
import secrets

class OAuthScraper:
    """Handle OAuth 2.0 authentication for scraping."""
    
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.session = requests.Session()
        
        self.access_token = None
        self.refresh_token = None
        self.token_expires = None
    
    def get_authorization_url(self, auth_endpoint, scope, state=None):
        """Generate URL for user to authorize."""
        state = state or secrets.token_urlsafe(32)
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': scope,
            'state': state,
        }
        
        return f"{auth_endpoint}?{urlencode(params)}", state
    
    def exchange_code_for_tokens(self, token_endpoint, authorization_code):
        """Exchange authorization code for access and refresh tokens."""
        
        response = self.session.post(token_endpoint, data={
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
        })
        
        if response.status_code != 200:
            raise Exception(f"Token exchange failed: {response.text}")
        
        tokens = response.json()
        self.access_token = tokens['access_token']
        self.refresh_token = tokens.get('refresh_token')
        
        expires_in = tokens.get('expires_in', 3600)
        self.token_expires = datetime.now() + timedelta(seconds=expires_in)
        
        return tokens
    
    def refresh_access_token(self, token_endpoint):
        """Use refresh token to get new access token."""
        
        if not self.refresh_token:
            raise Exception("No refresh token available")
        
        response = self.session.post(token_endpoint, data={
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        })
        
        if response.status_code != 200:
            raise Exception(f"Token refresh failed: {response.text}")
        
        tokens = response.json()
        self.access_token = tokens['access_token']
        
        if 'refresh_token' in tokens:
            self.refresh_token = tokens['refresh_token']
        
        expires_in = tokens.get('expires_in', 3600)
        self.token_expires = datetime.now() + timedelta(seconds=expires_in)
        
        return tokens
    
    def get_authenticated(self, url, **kwargs):
        """Make authenticated request, refreshing token if needed."""
        
        # Check if token needs refresh
        if self.token_expires and datetime.now() >= self.token_expires:
            print("Token expired, refreshing...")
            self.refresh_access_token(self.token_endpoint)
        
        # Add authorization header
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {self.access_token}'
        
        return self.session.get(url, headers=headers, **kwargs)
```

### 3.3 Browser-Based OAuth Flow

For OAuth that requires browser interaction:

```python
from playwright.sync_api import sync_playwright
import re

class BrowserOAuthHandler:
    """Handle OAuth flows that require browser interaction."""
    
    def __init__(self, client_id, redirect_uri):
        self.client_id = client_id
        self.redirect_uri = redirect_uri
    
    def authorize_with_browser(self, auth_url, username, password):
        """Complete OAuth flow using browser automation."""
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            # Navigate to authorization URL
            page.goto(auth_url)
            
            # Wait for login form
            page.wait_for_selector('input[type="email"], input[type="text"]')
            
            # Fill credentials (adjust selectors for specific provider)
            page.fill('input[type="email"], input[name="username"]', username)
            
            # Handle "Next" button for multi-step logins
            next_button = page.query_selector('button:has-text("Next")')
            if next_button:
                next_button.click()
                page.wait_for_selector('input[type="password"]')
            
            page.fill('input[type="password"]', password)
            
            # Submit
            page.click('button[type="submit"], input[type="submit"]')
            
            # Wait for consent/permission page
            try:
                page.wait_for_selector('button:has-text("Allow"), button:has-text("Authorize")', timeout=5000)
                page.click('button:has-text("Allow"), button:has-text("Authorize")')
            except:
                pass  # No consent page
            
            # Wait for redirect with authorization code
            page.wait_for_url(f"{self.redirect_uri}*", timeout=30000)
            
            # Extract authorization code from URL
            final_url = page.url
            parsed = urlparse(final_url)
            params = parse_qs(parsed.query)
            
            authorization_code = params.get('code', [None])[0]
            
            browser.close()
            
            return authorization_code
```

---

## 4. API Key Authentication

### 4.1 API Key Types

```
API Key Placement Options:

1. Query Parameter:
   GET /api/data?api_key=xxx123

2. Header:
   GET /api/data
   X-API-Key: xxx123

3. Bearer Token:
   GET /api/data
   Authorization: Bearer xxx123

4. Basic Auth (key as username):
   GET /api/data
   Authorization: Basic base64(api_key:)
```

### 4.2 API Key Management

```python
import os
from dataclasses import dataclass
from typing import Optional
import yaml

@dataclass
class APICredentials:
    """Store API credentials securely."""
    key: str
    secret: Optional[str] = None
    endpoint: Optional[str] = None
    rate_limit: Optional[int] = None

class APIKeyManager:
    """Manage multiple API keys with rotation."""
    
    def __init__(self, config_path=None):
        self.keys = {}
        if config_path:
            self.load_from_file(config_path)
    
    def load_from_file(self, path):
        """Load keys from config file."""
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        
        for service, creds in config.get('api_keys', {}).items():
            self.keys[service] = APICredentials(**creds)
    
    def load_from_env(self, service, env_var):
        """Load key from environment variable."""
        key = os.environ.get(env_var)
        if key:
            self.keys[service] = APICredentials(key=key)
    
    def get_key(self, service):
        """Get API key for service."""
        creds = self.keys.get(service)
        if not creds:
            raise ValueError(f"No API key for service: {service}")
        return creds
    
    def create_session(self, service, auth_type='header', header_name='X-API-Key'):
        """Create authenticated session for service."""
        creds = self.get_key(service)
        session = requests.Session()
        
        if auth_type == 'header':
            session.headers[header_name] = creds.key
        elif auth_type == 'bearer':
            session.headers['Authorization'] = f'Bearer {creds.key}'
        elif auth_type == 'basic':
            from requests.auth import HTTPBasicAuth
            session.auth = HTTPBasicAuth(creds.key, creds.secret or '')
        
        return session

# Example config file (api_keys.yaml):
# api_keys:
#   service_a:
#     key: "xxx123"
#     rate_limit: 100
#   service_b:
#     key: "yyy456"
#     secret: "secret789"
```

---

## 5. Multi-Factor Authentication (MFA/2FA)

### 5.1 Types of 2FA

```
2FA Methods:

1. TOTP (Time-based One-Time Password)
   ├── Google Authenticator
   ├── Authy
   └── Microsoft Authenticator
   
2. SMS/Phone
   ├── Text message codes
   └── Voice calls
   
3. Email
   └── Code sent to email

4. Hardware Keys
   ├── YubiKey
   └── FIDO2/WebAuthn

5. Push Notifications
   └── Approve on mobile app
```

### 5.2 Handling TOTP

```python
import pyotp

class TOTPHandler:
    """Handle TOTP-based 2FA."""
    
    def __init__(self, secret):
        """
        Initialize with TOTP secret.
        
        Secret is usually provided during 2FA setup as:
        - Base32 string (e.g., "JBSWY3DPEHPK3PXP")
        - QR code containing otpauth:// URL
        """
        self.totp = pyotp.TOTP(secret)
    
    def get_current_code(self):
        """Get current 6-digit TOTP code."""
        return self.totp.now()
    
    def verify_code(self, code):
        """Verify a TOTP code."""
        return self.totp.verify(code)

class TwoFactorLogin:
    """Complete login flow with 2FA."""
    
    def __init__(self, totp_secret=None):
        self.session = requests.Session()
        self.totp_handler = TOTPHandler(totp_secret) if totp_secret else None
    
    def login_with_2fa(self, login_url, username, password, totp_submit_url=None):
        """
        Complete login with 2FA.
        
        Flow:
        1. Submit username/password
        2. Get 2FA prompt
        3. Submit TOTP code
        """
        
        # Step 1: Initial login
        response = self.session.get(login_url)
        csrf_token = self._extract_csrf(response.text)
        
        response = self.session.post(login_url, data={
            'username': username,
            'password': password,
            'csrf_token': csrf_token,
        })
        
        # Step 2: Check if 2FA is required
        if self._requires_2fa(response):
            if not self.totp_handler:
                raise Exception("2FA required but no TOTP secret provided")
            
            # Get current TOTP code
            code = self.totp_handler.get_current_code()
            
            # Submit 2FA code
            totp_url = totp_submit_url or self._find_2fa_submit_url(response)
            csrf_token = self._extract_csrf(response.text)
            
            response = self.session.post(totp_url, data={
                'totp_code': code,
                'csrf_token': csrf_token,
            })
        
        return self._verify_login(response)
    
    def _requires_2fa(self, response):
        """Check if response indicates 2FA is needed."""
        indicators = [
            'two-factor',
            '2fa',
            'verification code',
            'authenticator',
            'one-time password',
        ]
        content_lower = response.text.lower()
        return any(ind in content_lower for ind in indicators)
    
    def _extract_csrf(self, html):
        """Extract CSRF token from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        csrf = soup.find('input', {'name': 'csrf_token'})
        return csrf['value'] if csrf else None
```

### 5.3 Browser-Based 2FA

For 2FA that can't be automated (SMS, push, hardware):

```python
from playwright.sync_api import sync_playwright

class InteractiveTwoFactorLogin:
    """Handle 2FA that requires human interaction."""
    
    def login_with_interactive_2fa(self, url, username, password):
        """
        Login flow that pauses for manual 2FA entry.
        """
        
        with sync_playwright() as p:
            # Use visible browser
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            # Navigate to login
            page.goto(url)
            
            # Fill credentials
            page.fill('input[name="username"]', username)
            page.fill('input[name="password"]', password)
            page.click('button[type="submit"]')
            
            # Wait for 2FA page
            page.wait_for_selector('[class*="2fa"], [class*="two-factor"], input[name*="code"]')
            
            # Prompt user
            print("\n" + "="*50)
            print("2FA REQUIRED")
            print("Please complete 2FA in the browser window.")
            print("="*50)
            
            # Wait for user to complete 2FA
            # (wait for redirect to dashboard or success page)
            page.wait_for_url("**/dashboard**", timeout=120000)
            
            # Extract cookies for future use
            cookies = page.context.cookies()
            
            browser.close()
            
            return cookies
```

---

## 6. Single Sign-On (SSO)

### 6.1 Understanding SSO

```
SSO Flow (SAML Example):

User          Service Provider (SP)      Identity Provider (IdP)
 │                    │                           │
 │  1. Access SP      │                           │
 │ ──────────────────▶│                           │
 │                    │                           │
 │                    │  2. SAML Request          │
 │                    │ ─────────────────────────▶│
 │                    │                           │
 │  3. Redirect to IdP login                      │
 │◀───────────────────────────────────────────────│
 │                    │                           │
 │  4. User authenticates with IdP                │
 │ ──────────────────────────────────────────────▶│
 │                    │                           │
 │  5. SAML Response (assertion)                  │
 │◀───────────────────────────────────────────────│
 │                    │                           │
 │  6. Submit assertion to SP                     │
 │ ──────────────────▶│                           │
 │                    │                           │
 │  7. Access granted │                           │
 │◀────────────────── │                           │
```

### 6.2 Handling SSO

```python
class SSOHandler:
    """Handle SSO authentication flows."""
    
    def __init__(self):
        self.session = requests.Session()
    
    def authenticate_sso(self, initial_url, idp_username, idp_password):
        """
        Navigate through SSO flow.
        
        This handles the redirects between SP and IdP.
        """
        
        # Step 1: Access protected resource
        response = self.session.get(initial_url, allow_redirects=False)
        
        # Step 2: Follow redirects to IdP
        while response.status_code in [301, 302, 303, 307, 308]:
            redirect_url = response.headers['Location']
            response = self.session.get(redirect_url, allow_redirects=False)
        
        # Step 3: We should now be at IdP login page
        if not self._is_login_page(response):
            raise Exception("Did not reach IdP login page")
        
        # Step 4: Extract IdP login form details
        idp_login_url, form_data = self._parse_idp_form(response)
        form_data['username'] = idp_username
        form_data['password'] = idp_password
        
        # Step 5: Submit IdP credentials
        response = self.session.post(idp_login_url, data=form_data, allow_redirects=False)
        
        # Step 6: Follow SAML response redirect back to SP
        while response.status_code in [301, 302, 303, 307, 308]:
            redirect_url = response.headers['Location']
            
            # Check for SAML response in redirect
            if 'SAMLResponse' in redirect_url or response.status_code == 303:
                # Handle SAML POST binding
                response = self._handle_saml_response(response)
            else:
                response = self.session.get(redirect_url, allow_redirects=False)
        
        return response
    
    def _handle_saml_response(self, response):
        """Handle SAML response that requires POST."""
        
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form')
        
        if form:
            action = form.get('action')
            
            # Extract SAML response from hidden field
            saml_response = form.find('input', {'name': 'SAMLResponse'})
            relay_state = form.find('input', {'name': 'RelayState'})
            
            data = {}
            if saml_response:
                data['SAMLResponse'] = saml_response['value']
            if relay_state:
                data['RelayState'] = relay_state['value']
            
            return self.session.post(action, data=data, allow_redirects=True)
        
        return response
```

### 6.3 Browser-Based SSO

```python
class BrowserSSOHandler:
    """Handle complex SSO flows using browser automation."""
    
    def authenticate_with_browser(self, url, username, password, provider='generic'):
        """
        Complete SSO authentication using browser.
        
        Handles: Okta, Azure AD, Google Workspace, OneLogin, etc.
        """
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            # Navigate to protected resource
            page.goto(url)
            
            # Wait for IdP login page
            page.wait_for_load_state('networkidle')
            
            # Detect IdP and use appropriate flow
            current_url = page.url.lower()
            
            if 'okta' in current_url:
                self._handle_okta(page, username, password)
            elif 'microsoftonline' in current_url or 'login.microsoft' in current_url:
                self._handle_azure_ad(page, username, password)
            elif 'accounts.google' in current_url:
                self._handle_google(page, username, password)
            else:
                self._handle_generic(page, username, password)
            
            # Wait for redirect back to original site
            page.wait_for_url(f"**{urlparse(url).netloc}**", timeout=60000)
            
            # Get authenticated cookies
            cookies = context.cookies()
            
            browser.close()
            
            return cookies
    
    def _handle_okta(self, page, username, password):
        """Handle Okta SSO."""
        page.fill('input[name="identifier"], input[name="username"]', username)
        page.click('input[type="submit"], button[type="submit"]')
        page.wait_for_selector('input[name="credentials.passcode"], input[type="password"]')
        page.fill('input[name="credentials.passcode"], input[type="password"]', password)
        page.click('input[type="submit"], button[type="submit"]')
    
    def _handle_azure_ad(self, page, username, password):
        """Handle Azure AD SSO."""
        page.fill('input[name="loginfmt"]', username)
        page.click('input[type="submit"]')
        page.wait_for_selector('input[name="passwd"]')
        page.fill('input[name="passwd"]', password)
        page.click('input[type="submit"]')
        
        # Handle "Stay signed in?" prompt
        try:
            page.wait_for_selector('input[value="No"]', timeout=3000)
            page.click('input[value="No"]')
        except:
            pass
    
    def _handle_google(self, page, username, password):
        """Handle Google Workspace SSO."""
        page.fill('input[type="email"]', username)
        page.click('#identifierNext')
        page.wait_for_selector('input[type="password"]')
        page.fill('input[type="password"]', password)
        page.click('#passwordNext')
    
    def _handle_generic(self, page, username, password):
        """Handle generic login forms."""
        # Find and fill username
        username_selectors = [
            'input[name="username"]',
            'input[name="email"]',
            'input[type="email"]',
            'input[name="user"]',
            'input[id="username"]',
        ]
        for selector in username_selectors:
            if page.query_selector(selector):
                page.fill(selector, username)
                break
        
        # Find and fill password
        page.fill('input[type="password"]', password)
        
        # Submit
        page.click('button[type="submit"], input[type="submit"]')
```

---

## 7. Paywalls & Content Gates

### 7.1 Types of Paywalls

```
Paywall Types:

1. Hard Paywall
   └── No content visible without subscription
   
2. Soft/Metered Paywall
   └── X free articles per month
   
3. Registration Wall
   └── Free but requires account
   
4. Newsletter Gate
   └── Enter email to access

5. Freemium
   └── Basic free, premium paid
```

### 7.2 Detecting Paywall Type

```python
def detect_paywall_type(response):
    """Identify paywall type from response."""
    
    html = response.text.lower()
    
    indicators = {
        'hard_paywall': [
            'subscribe to continue',
            'subscription required',
            'premium content',
            'members only',
        ],
        'metered_paywall': [
            'free articles remaining',
            'articles this month',
            'monthly limit',
            'reached your limit',
        ],
        'registration_wall': [
            'create an account',
            'sign up to read',
            'register for free',
            'login to continue',
        ],
        'newsletter_gate': [
            'enter your email',
            'subscribe to newsletter',
            'join our mailing list',
        ],
    }
    
    for paywall_type, phrases in indicators.items():
        if any(phrase in html for phrase in phrases):
            return paywall_type
    
    return 'none'
```

### 7.3 Metered Paywall Strategies

```python
class MeteredPaywallHandler:
    """Handle metered (soft) paywalls."""
    
    def __init__(self):
        self.strategies = [
            self._clear_cookies,
            self._use_incognito,
            self._try_archive,
            self._try_google_cache,
        ]
    
    def access_article(self, url):
        """Try multiple strategies to access metered content."""
        
        for strategy in self.strategies:
            try:
                result = strategy(url)
                if result:
                    return result
            except Exception as e:
                print(f"Strategy failed: {e}")
                continue
        
        return None
    
    def _clear_cookies(self, url):
        """Access with fresh session (resets meter)."""
        session = requests.Session()
        response = session.get(url, headers={
            'User-Agent': 'Mozilla/5.0...',
        })
        return response if self._has_content(response) else None
    
    def _use_incognito(self, url):
        """Use browser in incognito mode."""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()  # Fresh context = no cookies
            page = context.new_page()
            page.goto(url)
            content = page.content()
            browser.close()
            return content if len(content) > 1000 else None
    
    def _try_archive(self, url):
        """Try web.archive.org for cached version."""
        archive_url = f"https://web.archive.org/web/{url}"
        response = requests.get(archive_url)
        return response if response.status_code == 200 else None
    
    def _try_google_cache(self, url):
        """Try Google's cached version."""
        cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{url}"
        response = requests.get(cache_url, headers={
            'User-Agent': 'Mozilla/5.0...'
        })
        return response if response.status_code == 200 else None
    
    def _has_content(self, response):
        """Check if response contains actual article content."""
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for article body
        article = soup.find(['article', 'div[class*="article"]', 'div[class*="content"]'])
        
        if article:
            text = article.get_text()
            # Real articles are usually > 500 characters
            return len(text) > 500
        
        return False
```

---

## 8. Best Practices

### 8.1 Credential Security

```python
import os
from cryptography.fernet import Fernet

class SecureCredentialStore:
    """Securely store and retrieve credentials."""
    
    def __init__(self, key=None):
        self.key = key or os.environ.get('CREDENTIAL_KEY')
        if not self.key:
            raise ValueError("Encryption key required")
        self.cipher = Fernet(self.key.encode() if isinstance(self.key, str) else self.key)
    
    @classmethod
    def generate_key(cls):
        """Generate new encryption key."""
        return Fernet.generate_key().decode()
    
    def encrypt(self, plaintext):
        """Encrypt credential."""
        return self.cipher.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext):
        """Decrypt credential."""
        return self.cipher.decrypt(ciphertext.encode()).decode()
    
    def store_credentials(self, filepath, credentials):
        """Store encrypted credentials to file."""
        encrypted = {
            k: self.encrypt(v) for k, v in credentials.items()
        }
        with open(filepath, 'w') as f:
            json.dump(encrypted, f)
    
    def load_credentials(self, filepath):
        """Load and decrypt credentials from file."""
        with open(filepath, 'r') as f:
            encrypted = json.load(f)
        return {
            k: self.decrypt(v) for k, v in encrypted.items()
        }
```

### 8.2 Rate Limiting Authenticated Requests

```python
class RateLimitedAuthSession:
    """Authenticated session with rate limiting."""
    
    def __init__(self, session, requests_per_minute=30):
        self.session = session
        self.rate_limit = requests_per_minute
        self.request_times = []
    
    def get(self, url, **kwargs):
        self._wait_for_rate_limit()
        return self.session.get(url, **kwargs)
    
    def post(self, url, **kwargs):
        self._wait_for_rate_limit()
        return self.session.post(url, **kwargs)
    
    def _wait_for_rate_limit(self):
        """Wait if necessary to respect rate limit."""
        now = time.time()
        minute_ago = now - 60
        
        # Remove old request times
        self.request_times = [t for t in self.request_times if t > minute_ago]
        
        # If at limit, wait
        if len(self.request_times) >= self.rate_limit:
            sleep_time = self.request_times[0] - minute_ago + 0.1
            time.sleep(sleep_time)
        
        self.request_times.append(time.time())
```

---

## 9. Summary

### Authentication Methods Quick Reference

| Method | Complexity | Automation Difficulty |
|--------|------------|----------------------|
| Basic Form | Low | Easy |
| Session Cookies | Low | Easy |
| CSRF Tokens | Medium | Medium |
| OAuth 2.0 | High | Medium-Hard |
| API Keys | Low | Easy |
| TOTP 2FA | Medium | Easy (with secret) |
| SMS 2FA | High | Hard (needs human) |
| SSO (SAML) | High | Hard |
| Hardware 2FA | Very High | Impossible to automate |

### Key Principles

1. **Persist sessions** - Don't login more than necessary
2. **Handle expiration** - Auto-detect and re-authenticate
3. **Secure credentials** - Never hardcode passwords
4. **Respect rate limits** - Especially for authenticated APIs
5. **Use browser automation** - For complex auth flows
6. **Have fallback strategies** - Auth can fail for many reasons

### Ethical Considerations

```
Before Authenticating to Scrape:
┌─────────────────────────────────────────────────────────┐
│ □ Do I have permission to use these credentials?       │
│ □ Am I violating the Terms of Service?                 │
│ □ Could this harm the legitimate user?                 │
│ □ Am I respecting rate limits?                         │
│ □ Is there an official API I should use instead?       │
└─────────────────────────────────────────────────────────┘
```

---

*Next: [07_dynamic_content_obfuscation.md](07_dynamic_content_obfuscation.md) - Handling obfuscated and dynamic content*
