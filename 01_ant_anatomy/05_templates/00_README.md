# Ant Templates

> **Ready-to-Use Scraper Templates**

This directory contains template scrapers that you can copy and customize for your specific needs.

---

## Available Templates

| Template | Description | Use Case |
|----------|-------------|----------|
| [simple_ant.py](simple_ant.py) | Basic single-page scraper | Product pages, articles |
| [paginated_ant.py](paginated_ant.py) | Multi-page with pagination | Search results, listings |
| [browser_ant.py](browser_ant.py) | JavaScript-rendered pages | SPAs, dynamic content |
| [api_ant.py](api_ant.py) | JSON API consumer | REST APIs, data feeds |

---

## Quick Start

### 1. Copy a Template

```bash
cp 01_ant_anatomy/05_templates/simple_ant.py my_project/my_ant.py
```

### 2. Customize

```python
# my_ant.py
from simple_ant import SimpleAnt

class MyProductAnt(SimpleAnt):
    name = "my_product_ant"
    
    selectors = {
        'title': 'h1.product-title',
        'price': '.price-current',
        'description': '.product-description',
    }
```

### 3. Run

```python
ant = MyProductAnt()
result = ant.scrape('https://example.com/product/123')
print(result.data)
```

---

## Template Selection Guide

```
What do you need to scrape?
│
├── Static HTML page
│   └── Use: simple_ant.py
│
├── Multiple pages (pagination)
│   └── Use: paginated_ant.py
│
├── JavaScript-rendered content
│   └── Use: browser_ant.py
│
├── JSON API endpoint
│   └── Use: api_ant.py
│
└── Complex site (multiple patterns)
    └── Combine multiple templates
```

---

*Part of [01_ant_anatomy](../) - Core scraper building blocks*
