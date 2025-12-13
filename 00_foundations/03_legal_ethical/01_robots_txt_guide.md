# robots.txt Guide

> **The Gentleman's Agreement of Web Scraping**

The robots.txt file is how websites communicate with bots about what they allow and don't allow. While not legally binding, respecting it is a cornerstone of ethical scraping.

---

## What is robots.txt?

A plain text file at the root of a website that provides guidelines for bots:

```
https://example.com/robots.txt
```

It's part of the **Robots Exclusion Protocol** (REP), a standard since 1994.

---

## Basic Syntax

### Structure

```
User-agent: [bot name or wildcard]
[directive]: [path]
```

### Example

```
# Allow all bots everywhere
User-agent: *
Allow: /

# Block specific directory
Disallow: /private/

# Sitemap location
Sitemap: https://example.com/sitemap.xml
```

---

## Directives

### User-agent

Specifies which bots the rules apply to:

```
# All bots
User-agent: *

# Specific bot
User-agent: Googlebot

# Multiple bots (separate blocks)
User-agent: Googlebot
User-agent: Bingbot
Disallow: /private/
```

### Disallow

Paths the bot should NOT visit:

```
# Block specific path
Disallow: /admin/

# Block all paths (block everything)
Disallow: /

# Block specific file
Disallow: /secret-page.html

# Block path pattern
Disallow: /user/*/settings
```

### Allow

Explicitly allow paths (overrides Disallow):

```
# Block all of /private/ except public.html
User-agent: *
Disallow: /private/
Allow: /private/public.html
```

### Crawl-delay

Seconds to wait between requests:

```
User-agent: *
Crawl-delay: 10
```

**Note:** Googlebot ignores this; use Google Search Console instead.

### Sitemap

Location of XML sitemap:

```
Sitemap: https://example.com/sitemap.xml
Sitemap: https://example.com/sitemap-products.xml
```

---

## Common Patterns

### Block Everything

```
User-agent: *
Disallow: /
```

### Allow Everything

```
User-agent: *
Allow: /
```

Or simply an empty robots.txt.

### Block Specific Bots

```
User-agent: BadBot
Disallow: /

User-agent: *
Allow: /
```

### Protect Sensitive Areas

```
User-agent: *
Disallow: /admin/
Disallow: /api/
Disallow: /private/
Disallow: /user/
Disallow: /checkout/
Disallow: /cart/
Disallow: /*?sessionid=
```

### Allow Only Certain Bots

```
User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: *
Disallow: /
```

---

## Reading robots.txt in Python

### Basic Parsing

```python
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

def check_allowed(url, user_agent='*'):
    """Check if URL is allowed for scraping."""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    
    rp = RobotFileParser()
    rp.set_url(robots_url)
    
    try:
        rp.read()
    except Exception as e:
        # If robots.txt doesn't exist or can't be read, assume allowed
        print(f"Could not read robots.txt: {e}")
        return True
    
    return rp.can_fetch(user_agent, url)

# Usage
url = "https://example.com/products/123"
if check_allowed(url, user_agent='MyBot'):
    # OK to scrape
    response = requests.get(url)
else:
    print("Blocked by robots.txt")
```

### Getting Crawl Delay

```python
def get_crawl_delay(base_url, user_agent='*'):
    """Get crawl delay from robots.txt."""
    rp = RobotFileParser()
    rp.set_url(f"{base_url}/robots.txt")
    rp.read()
    
    delay = rp.crawl_delay(user_agent)
    return delay if delay else 0

# Usage
delay = get_crawl_delay("https://example.com")
print(f"Should wait {delay} seconds between requests")
```

### Getting Sitemaps

```python
def get_sitemaps(base_url):
    """Extract sitemap URLs from robots.txt."""
    import requests
    
    robots_url = f"{base_url}/robots.txt"
    response = requests.get(robots_url)
    
    sitemaps = []
    for line in response.text.split('\n'):
        if line.lower().startswith('sitemap:'):
            sitemap_url = line.split(':', 1)[1].strip()
            sitemaps.append(sitemap_url)
    
    return sitemaps

# Usage
sitemaps = get_sitemaps("https://example.com")
for sitemap in sitemaps:
    print(f"Found sitemap: {sitemap}")
```

### Complete Robot Checker Class

```python
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import time

class RobotsChecker:
    """Checks and caches robots.txt rules."""
    
    def __init__(self, user_agent='MyBot/1.0'):
        self.user_agent = user_agent
        self.parsers = {}  # Cache by domain
    
    def _get_parser(self, url):
        """Get or create parser for domain."""
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        
        if domain not in self.parsers:
            rp = RobotFileParser()
            rp.set_url(f"{domain}/robots.txt")
            try:
                rp.read()
            except:
                rp = None
            self.parsers[domain] = rp
        
        return self.parsers[domain]
    
    def can_fetch(self, url):
        """Check if URL can be fetched."""
        parser = self._get_parser(url)
        if parser is None:
            return True  # No robots.txt = assume allowed
        return parser.can_fetch(self.user_agent, url)
    
    def get_delay(self, url):
        """Get crawl delay for URL's domain."""
        parser = self._get_parser(url)
        if parser is None:
            return 0
        delay = parser.crawl_delay(self.user_agent)
        return delay if delay else 0

# Usage
checker = RobotsChecker(user_agent='MyBot/1.0')

for url in urls:
    if checker.can_fetch(url):
        delay = checker.get_delay(url)
        time.sleep(delay)
        # Scrape...
    else:
        print(f"Skipping (blocked): {url}")
```

---

## Real-World Examples

### Google

```
User-agent: *
Disallow: /search
Disallow: /sdch
Disallow: /groups
Disallow: /index.html?
Disallow: /?
Allow: /search/about
Allow: /search/static
Allow: /search/howsearchworks
Sitemap: https://www.google.com/sitemap.xml
```

### LinkedIn

```
User-agent: *
Disallow: /

# Blocks everyone - very strict
```

### Amazon

```
User-agent: *
Disallow: /exec/obidos/account-access-login
Disallow: /exec/obidos/change-style
Disallow: /exec/obidos/flex-hierarchical-browse
Disallow: /gp/cart
Disallow: /gp/flex
# ... extensive list
```

### Wikipedia

```
User-agent: *
Disallow: /wiki/Special:
Disallow: /wiki/User:
Disallow: /wiki/Talk:
Allow: /wiki/Special:Export
# Very permissive for content, blocks administrative pages
```

---

## robots.txt Limitations

### What It IS

- Guidelines for well-behaved bots
- Industry standard/convention
- Signal of site owner's preferences
- Potential legal evidence (if you violate it)

### What It Is NOT

- Technical enforcement (doesn't actually block)
- Legally binding contract
- Complete list of allowed/blocked pages
- Security mechanism

### Can Be Ignored By

- Malicious bots
- Security scanners
- Archival services (sometimes)
- Legal researchers (sometimes)

---

## Legal Implications

### In Court Cases

robots.txt has been referenced in legal cases:

| Case | Outcome |
|------|---------|
| **hiQ vs LinkedIn** | Violating robots.txt alone not enough for CFAA violation |
| **Craigslist vs 3Taps** | Ignoring robots.txt + cease-and-desist = violation |
| **Facebook vs Power Ventures** | Multiple factors including robots.txt |

### Best Practice

Even if not legally binding, respecting robots.txt:
- Shows good faith
- Reduces legal risk
- Follows industry norms
- Is the ethical choice

---

## Edge Cases

### No robots.txt

```python
# If file doesn't exist, assume everything is allowed
# HTTP 404 for robots.txt = no restrictions
```

### Malformed robots.txt

```python
# Parser should handle gracefully
# When in doubt, be conservative
```

### Conflicting Rules

```
User-agent: *
Disallow: /folder/
Allow: /folder/page.html
```

More specific rules take precedence.

### Wildcards (Extended Syntax)

```
# Block all PDFs
Disallow: /*.pdf$

# Block query strings
Disallow: /*?*

# Block path patterns
Disallow: /product/*/reviews
```

**Note:** Wildcards are not part of original spec but widely supported.

---

## Integrating Into Scrapers

### Simple Integration

```python
import requests
from urllib.robotparser import RobotFileParser

class RespectfulScraper:
    def __init__(self, user_agent):
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers['User-Agent'] = user_agent
        self.robots_cache = {}
    
    def fetch(self, url):
        if not self._check_robots(url):
            raise PermissionError(f"Blocked by robots.txt: {url}")
        
        delay = self._get_delay(url)
        if delay:
            time.sleep(delay)
        
        return self.session.get(url)
    
    def _check_robots(self, url):
        # ... implementation
        pass
```

### Scrapy Integration

```python
# settings.py
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 1
```

Scrapy automatically handles robots.txt when `ROBOTSTXT_OBEY = True`.

---

## Summary

| Directive | Meaning | Example |
|-----------|---------|---------|
| `User-agent` | Which bot | `User-agent: Googlebot` |
| `Disallow` | Don't visit | `Disallow: /private/` |
| `Allow` | OK to visit | `Allow: /public/` |
| `Crawl-delay` | Wait time (sec) | `Crawl-delay: 10` |
| `Sitemap` | Sitemap location | `Sitemap: /sitemap.xml` |

### Key Takeaways

1. **Always check robots.txt** before scraping
2. **Respect Disallow** directives
3. **Honor Crawl-delay** if specified
4. **Cache parser** per domain
5. **Be conservative** when rules are unclear
6. **Document compliance** for legal protection

---

*Next: [02_terms_of_service.md](02_terms_of_service.md) - Understanding website Terms of Service*
