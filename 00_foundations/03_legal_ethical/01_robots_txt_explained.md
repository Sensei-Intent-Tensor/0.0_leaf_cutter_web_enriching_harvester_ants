# robots.txt Explained

> **The Gentleman's Agreement of Web Scraping**

robots.txt is a file that tells web robots which parts of a site they should and shouldn't access. Understanding it is the first step in ethical scraping.

---

## What is robots.txt?

A plain text file at the root of a website that provides crawling directives:

```
https://example.com/robots.txt
```

### Purpose

1. **Communication** - Website owner's crawling preferences
2. **Resource protection** - Prevent overload of sensitive areas
3. **Privacy** - Keep certain content out of search engines
4. **Guidance** - Show bots the right paths

### Important Note

robots.txt is **advisory, not enforceable**. Bots can technically ignore it, but:
- Respecting it is industry best practice
- Ignoring it may have legal implications
- Major services (Google, Bing) always respect it

---

## robots.txt Syntax

### Basic Structure

```
User-agent: *
Disallow: /admin/
Disallow: /private/
Allow: /public/
Crawl-delay: 10
Sitemap: https://example.com/sitemap.xml
```

### Directives

| Directive | Purpose | Example |
|-----------|---------|---------|
| `User-agent` | Which bot the rules apply to | `User-agent: Googlebot` |
| `Disallow` | Paths not to crawl | `Disallow: /admin/` |
| `Allow` | Override disallow | `Allow: /admin/public/` |
| `Crawl-delay` | Seconds between requests | `Crawl-delay: 10` |
| `Sitemap` | Location of sitemap | `Sitemap: /sitemap.xml` |

### User-agent Patterns

```
# Apply to all bots
User-agent: *

# Specific bots
User-agent: Googlebot
User-agent: Bingbot
User-agent: YandexBot

# Your custom bot
User-agent: MyScraperBot/1.0
```

### Path Patterns

```
# Exact path
Disallow: /admin/

# All paths starting with
Disallow: /private

# All .pdf files
Disallow: /*.pdf$

# Query strings
Disallow: /*?*

# Specific file types
Disallow: /*.doc$
Disallow: /*.xls$
```

---

## Reading robots.txt

### Example 1: Simple Site

```
User-agent: *
Disallow: /admin/
Disallow: /cgi-bin/
Disallow: /tmp/
Sitemap: https://example.com/sitemap.xml
```

**Meaning:**
- All bots (`*`) should avoid `/admin/`, `/cgi-bin/`, `/tmp/`
- Everything else is fair game
- Sitemap available for discovery

### Example 2: Different Rules per Bot

```
User-agent: Googlebot
Disallow: /search/
Crawl-delay: 1

User-agent: Bingbot
Disallow: /search/
Crawl-delay: 5

User-agent: *
Disallow: /admin/
Disallow: /search/
Crawl-delay: 10
```

**Meaning:**
- Google can crawl faster (1 second delay)
- Bing waits 5 seconds
- Everyone else waits 10 seconds
- All avoid `/search/` and others avoid `/admin/`

### Example 3: Complex E-commerce

```
User-agent: *
Disallow: /cart/
Disallow: /checkout/
Disallow: /account/
Disallow: /wishlist/
Disallow: /search?*
Disallow: /*?sort=*
Disallow: /*?filter=*
Allow: /products/
Allow: /categories/

User-agent: Googlebot-Image
Allow: /images/products/
Disallow: /images/internal/
```

**Meaning:**
- Don't crawl user-specific pages (cart, account)
- Don't crawl search/filter URLs (duplicate content)
- Products and categories are welcome
- Google Image bot has special image rules

### Example 4: Total Block

```
User-agent: *
Disallow: /
```

**Meaning:**
- Block ALL bots from entire site

### Example 5: Allow All

```
User-agent: *
Disallow:
```

**Meaning:**
- No restrictions (disallow nothing)

---

## Parsing robots.txt in Python

### Using urllib.robotparser

```python
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

def check_robots(url, user_agent="*"):
    """Check if URL is allowed by robots.txt."""
    
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    
    rp = RobotFileParser()
    rp.set_url(robots_url)
    
    try:
        rp.read()
    except Exception as e:
        print(f"Could not read robots.txt: {e}")
        return True  # If can't read, assume allowed
    
    return rp.can_fetch(user_agent, url)

# Usage
url = "https://example.com/products/123"
if check_robots(url, "MyBot/1.0"):
    print("Allowed to crawl")
else:
    print("Blocked by robots.txt")
```

### Getting Crawl Delay

```python
def get_crawl_delay(domain, user_agent="*"):
    """Get crawl delay from robots.txt."""
    
    robots_url = f"https://{domain}/robots.txt"
    
    rp = RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    
    delay = rp.crawl_delay(user_agent)
    return delay if delay else 0

# Usage
delay = get_crawl_delay("example.com", "MyBot/1.0")
print(f"Should wait {delay} seconds between requests")
```

### Getting Sitemaps

```python
def get_sitemaps(domain):
    """Extract sitemap URLs from robots.txt."""
    
    import requests
    
    robots_url = f"https://{domain}/robots.txt"
    response = requests.get(robots_url)
    
    sitemaps = []
    for line in response.text.split('\n'):
        if line.lower().startswith('sitemap:'):
            sitemap_url = line.split(':', 1)[1].strip()
            sitemaps.append(sitemap_url)
    
    return sitemaps

# Usage
sitemaps = get_sitemaps("example.com")
for sitemap in sitemaps:
    print(f"Sitemap: {sitemap}")
```

### Complete Robots Checker Class

```python
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import requests
import time

class RobotsChecker:
    def __init__(self, user_agent="MyBot/1.0"):
        self.user_agent = user_agent
        self.parsers = {}  # Cache per domain
        self.cache_ttl = 3600  # 1 hour
        self.cache_times = {}
    
    def _get_parser(self, domain):
        """Get or create parser for domain."""
        
        now = time.time()
        
        # Check cache
        if domain in self.parsers:
            if now - self.cache_times[domain] < self.cache_ttl:
                return self.parsers[domain]
        
        # Create new parser
        rp = RobotFileParser()
        rp.set_url(f"https://{domain}/robots.txt")
        
        try:
            rp.read()
        except:
            rp = None
        
        self.parsers[domain] = rp
        self.cache_times[domain] = now
        
        return rp
    
    def can_fetch(self, url):
        """Check if URL can be fetched."""
        
        domain = urlparse(url).netloc
        parser = self._get_parser(domain)
        
        if parser is None:
            return True  # No robots.txt = allowed
        
        return parser.can_fetch(self.user_agent, url)
    
    def get_crawl_delay(self, url):
        """Get crawl delay for URL's domain."""
        
        domain = urlparse(url).netloc
        parser = self._get_parser(domain)
        
        if parser is None:
            return 0
        
        delay = parser.crawl_delay(self.user_agent)
        return delay if delay else 0
    
    def get_sitemaps(self, url):
        """Get sitemaps for URL's domain."""
        
        domain = urlparse(url).netloc
        parser = self._get_parser(domain)
        
        if parser is None:
            return []
        
        return parser.site_maps() or []

# Usage
checker = RobotsChecker("MyBot/1.0")

urls = [
    "https://example.com/products/123",
    "https://example.com/admin/users",
    "https://other-site.com/data",
]

for url in urls:
    allowed = checker.can_fetch(url)
    delay = checker.get_crawl_delay(url)
    print(f"{url}: {'✓' if allowed else '✗'} (delay: {delay}s)")
```

---

## Best Practices

### For Your Scraper

```python
class RespectfulScraper:
    def __init__(self, user_agent):
        self.user_agent = user_agent
        self.robots = RobotsChecker(user_agent)
        self.session = requests.Session()
        self.session.headers['User-Agent'] = user_agent
    
    def scrape(self, url):
        # Check robots.txt first
        if not self.robots.can_fetch(url):
            print(f"Blocked by robots.txt: {url}")
            return None
        
        # Respect crawl delay
        delay = self.robots.get_crawl_delay(url)
        if delay:
            time.sleep(delay)
        
        # Make request
        response = self.session.get(url)
        return response

# Identify yourself
scraper = RespectfulScraper("MyBot/1.0 (+https://mysite.com/bot)")
```

### Identify Your Bot

Include contact information in User-Agent:

```
User-Agent: MyBot/1.0 (+https://mysite.com/bot-info)
User-Agent: MyBot/1.0 (contact@mysite.com)
```

This allows site owners to:
- Know who's crawling
- Contact you if there's a problem
- Potentially whitelist you

---

## What robots.txt Means Legally

### It's Evidence of Intent

While robots.txt isn't a legal contract, it can be relevant in legal cases:

- **hiQ v. LinkedIn**: Court noted LinkedIn's robots.txt didn't block hiQ
- **Field v. Google**: robots.txt used to argue implied license

### Not a Security Measure

robots.txt:
- ❌ Does NOT prevent access
- ❌ Does NOT hide content
- ❌ Is NOT access control
- ✅ IS a communication of preferences

### Should You Always Obey?

| Situation | Recommendation |
|-----------|----------------|
| Personal project | Respect it |
| Commercial use | Definitely respect it |
| Research | Usually respect, may have exceptions |
| Archived content | May proceed cautiously |
| Public interest | Consult a lawyer |

---

## Common robots.txt Patterns

### News Sites

```
User-agent: *
Disallow: /search
Disallow: /login
Crawl-delay: 1
Sitemap: https://news-site.com/sitemap-index.xml
```

### E-commerce

```
User-agent: *
Disallow: /cart
Disallow: /checkout
Disallow: /account
Disallow: /*?sort=
Disallow: /*?filter=
Allow: /products/
```

### Social Media

```
User-agent: *
Disallow: /messages
Disallow: /settings
Disallow: /api/
Allow: /public/
Crawl-delay: 5
```

### API Documentation

```
User-agent: *
Disallow: /internal/
Allow: /docs/
Allow: /api-reference/
Sitemap: https://api-docs.com/sitemap.xml
```

---

## Summary

| Aspect | Details |
|--------|---------|
| **Location** | `/robots.txt` at site root |
| **Format** | Plain text, specific syntax |
| **Enforcement** | Advisory only, not technical |
| **Best Practice** | Always check and respect |
| **Legal Status** | Evidence of intent, not contract |

### Key Takeaways

1. **Check robots.txt first** - Before scraping any site
2. **Respect Crawl-delay** - Be a good netizen
3. **Identify yourself** - Use descriptive User-Agent
4. **Cache the rules** - Don't re-fetch constantly
5. **No robots.txt ≠ permission** - Use common sense

---

*Next: [02_terms_of_service.md](02_terms_of_service.md) - Understanding ToS implications*
