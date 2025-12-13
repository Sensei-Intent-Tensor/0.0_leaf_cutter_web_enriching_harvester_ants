# 01_ant_anatomy

> **The Building Blocks of Every Scraper**

In the Leaf Cutter framework, every scraper is an "Ant" - a specialized worker designed to harvest specific data from the web. This section defines the anatomy of these ants: their structure, patterns, outputs, and error handling.

---

## 🐜 What is an Ant?

An **Ant** is a self-contained scraping unit that:

```
┌─────────────────────────────────────────────────────────────────┐
│                         ANT ANATOMY                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   INPUT                                                         │
│   ├── URL(s) to scrape                                          │
│   ├── Configuration (headers, proxies, delays)                  │
│   └── Extraction rules (selectors, patterns)                    │
│                                                                 │
│   PROCESSING                                                    │
│   ├── Fetch content (HTTP or browser)                           │
│   ├── Parse HTML/JSON                                           │
│   ├── Extract structured data                                   │
│   └── Handle errors and retries                                 │
│                                                                 │
│   OUTPUT                                                        │
│   ├── Structured data (dict, dataclass, Pydantic model)         │
│   ├── Metadata (timestamps, source URL, status)                 │
│   └── Logs and metrics                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📚 Section Contents

| File | Description |
|------|-------------|
| [01_base_ant.py](01_base_ant.py) | The BaseAnt class - foundation for all scrapers |
| [02_ant_patterns.md](02_ant_patterns.md) | Common scraping patterns and when to use them |
| [03_output_formats.md](03_output_formats.md) | Structuring and validating scraped data |
| [04_error_handling.md](04_error_handling.md) | Robust error handling and retry strategies |
| [05_templates/](05_templates/) | Ready-to-use ant templates |

---

## 🎯 Ant Design Principles

### 1. Single Responsibility

Each ant does ONE thing well:

```python
# GOOD: Focused ant
class ProductAnt(BaseAnt):
    """Scrapes product details from a product page."""
    pass

# BAD: Multi-purpose ant
class EverythingAnt(BaseAnt):
    """Scrapes products, reviews, seller info, and recommendations."""
    pass
```

### 2. Configurable, Not Hardcoded

```python
# GOOD: Configurable
class ProductAnt(BaseAnt):
    def __init__(self, base_url: str, selectors: dict = None):
        self.base_url = base_url
        self.selectors = selectors or self.default_selectors

# BAD: Hardcoded
class ProductAnt(BaseAnt):
    base_url = "https://example.com"
    title_selector = "h1.product-title"
```

### 3. Graceful Degradation

```python
# GOOD: Handles missing data
def extract(self, html):
    return {
        'title': self.safe_extract('.title', html) or 'Unknown',
        'price': self.safe_extract('.price', html),  # None is OK
        'stock': self.safe_extract('.stock', html) or 'Unknown'
    }
```

### 4. Observable

```python
# GOOD: Logs and metrics
class ProductAnt(BaseAnt):
    def scrape(self, url):
        self.logger.info(f"Scraping: {url}")
        start = time.time()
        
        result = self._scrape(url)
        
        self.metrics.record('scrape_duration', time.time() - start)
        self.metrics.increment('pages_scraped')
        
        return result
```

---

## 🏗️ Ant Hierarchy

```
BaseAnt (abstract)
│
├── SimpleAnt
│   └── Single page, requests-based
│
├── BrowserAnt
│   └── JavaScript rendering with Playwright
│
├── PaginatedAnt
│   └── Handles multi-page results
│
├── CrawlerAnt
│   └── Follows links, discovers pages
│
└── APIAnt
    └── JSON API consumption
```

---

## 🔄 Ant Lifecycle

```
1. INITIALIZE
   └── Load config, setup session, validate inputs

2. FETCH
   └── Make HTTP request or render with browser

3. VALIDATE
   └── Check response status, detect blocks

4. PARSE
   └── Convert raw response to parseable format

5. EXTRACT
   └── Pull structured data using selectors

6. TRANSFORM
   └── Clean, normalize, validate data

7. OUTPUT
   └── Return structured result or save to storage

8. CLEANUP
   └── Close connections, report metrics
```

---

## 💡 Quick Start

### Minimal Ant

```python
from base_ant import BaseAnt

class MyAnt(BaseAnt):
    def extract(self, soup):
        return {
            'title': soup.select_one('h1').get_text(strip=True),
            'price': soup.select_one('.price').get_text(strip=True)
        }

# Usage
ant = MyAnt()
result = ant.scrape('https://example.com/product')
print(result)
```

### With Configuration

```python
ant = MyAnt(
    headers={'User-Agent': 'MyBot/1.0'},
    delay=2.0,
    retry_count=3,
    proxy='http://proxy:8080'
)
```

---

## 🔗 Related Sections

- [00_foundations/](../00_foundations/) - Core concepts and terminology
- [02_ant_farms/](../02_ant_farms/) - Collections of ants for specific sites
- [06_utils/](../06_utils/) - Shared utilities used by ants

---

*Part of the [Leaf Cutter Web Enriching Harvester Ants](../) framework*
