# Parsing Libraries Guide

> **Extracting Data from HTML, XML, and JSON**

Once you've fetched a page, you need to extract data from it. This document covers the tools for parsing different data formats.

---

## Parsing Decision Tree

```
What format is your data?
│
├── HTML/XML
│   ├── Need speed? → lxml
│   ├── Messy HTML? → BeautifulSoup (html.parser or lxml)
│   ├── Need both CSS & XPath? → parsel
│   └── Using Scrapy? → parsel (built-in)
│
├── JSON
│   ├── Standard JSON → json (stdlib)
│   ├── Streaming large files → ijson
│   └── JSON with comments → json5
│
└── Other
    ├── CSV → csv or pandas
    ├── PDF → pdfplumber
    └── Excel → openpyxl or pandas
```

---

## 1. BeautifulSoup

### Overview

The most popular HTML/XML parser. Forgiving, intuitive, great for beginners.

```python
from bs4 import BeautifulSoup

html = """
<html>
<body>
    <div class="product" id="p1">
        <h2>Widget</h2>
        <span class="price">$99.99</span>
        <a href="/product/1">Details</a>
    </div>
    <div class="product" id="p2">
        <h2>Gadget</h2>
        <span class="price">$149.99</span>
        <a href="/product/2">Details</a>
    </div>
</body>
</html>
"""

soup = BeautifulSoup(html, 'html.parser')  # or 'lxml' for speed
```

### Finding Elements

```python
# By tag
h2 = soup.find('h2')  # First h2
all_h2 = soup.find_all('h2')  # All h2s

# By class
products = soup.find_all('div', class_='product')
products = soup.find_all(class_='product')  # Any tag with class

# By ID
product = soup.find(id='p1')

# By attribute
links = soup.find_all('a', href=True)  # All links with href
specific = soup.find_all('a', {'href': '/product/1'})

# Multiple conditions
result = soup.find_all('div', class_='product', id='p1')

# By text content
element = soup.find(string='Widget')
element = soup.find(string=lambda t: 'Widget' in t if t else False)
```

### CSS Selectors

```python
# Select one
product = soup.select_one('div.product')

# Select all
products = soup.select('div.product')
prices = soup.select('.product .price')

# Complex selectors
soup.select('div.product > h2')           # Direct child
soup.select('div.product h2')             # Descendant
soup.select('div.product + div')          # Adjacent sibling
soup.select('div[id]')                    # Has attribute
soup.select('div[class="product"]')       # Exact attribute
soup.select('div[class*="prod"]')         # Contains
soup.select('div[class^="prod"]')         # Starts with
soup.select('div:nth-child(2)')           # Position
```

### Extracting Data

```python
element = soup.find('div', class_='product')

# Text content
text = element.get_text()                  # All text, including children
text = element.get_text(strip=True)        # Stripped whitespace
text = element.get_text(separator=' ')     # Custom separator

# Specific text
title = element.find('h2').string          # Direct text only
title = element.find('h2').get_text()      # All text

# Attributes
link = element.find('a')
href = link['href']                        # Raises KeyError if missing
href = link.get('href')                    # Returns None if missing
href = link.get('href', '')                # Default value

# All attributes
attrs = link.attrs  # {'href': '/product/1'}
```

### Navigating the Tree

```python
element = soup.find('h2')

# Parent
parent = element.parent
parents = list(element.parents)  # All ancestors

# Siblings
next_sib = element.next_sibling
prev_sib = element.previous_sibling
all_next = list(element.next_siblings)

# Children
children = element.children          # Iterator
children = list(element.children)    # List
descendants = element.descendants    # All nested

# Next/previous elements (skips whitespace)
next_elem = element.find_next()
prev_elem = element.find_previous()
next_h2 = element.find_next('h2')
```

### Parser Comparison

| Parser | Speed | Lenient | Install |
|--------|-------|---------|---------|
| `html.parser` | Medium | Yes | Built-in |
| `lxml` | Fast | Yes | `pip install lxml` |
| `lxml-xml` | Fast | No | `pip install lxml` |
| `html5lib` | Slow | Very | `pip install html5lib` |

```python
# html.parser - built-in, good default
soup = BeautifulSoup(html, 'html.parser')

# lxml - fastest, install separately
soup = BeautifulSoup(html, 'lxml')

# html5lib - parses like browser, slowest
soup = BeautifulSoup(html, 'html5lib')
```

---

## 2. lxml

### Overview

Fastest parser. Supports XPath. Best for high-volume parsing.

```python
from lxml import html, etree

# Parse HTML
tree = html.fromstring(html_content)

# Parse XML
tree = etree.fromstring(xml_content)

# From file
tree = html.parse('page.html')
```

### XPath Queries

```python
# Basic selection
titles = tree.xpath('//h2/text()')
prices = tree.xpath('//span[@class="price"]/text()')

# With conditions
expensive = tree.xpath('//div[@class="product"][.//span > 100]')

# Attributes
links = tree.xpath('//a/@href')
ids = tree.xpath('//div[@class="product"]/@id')

# Functions
count = tree.xpath('count(//div[@class="product"])')
first = tree.xpath('(//div[@class="product"])[1]')

# Contains
partial = tree.xpath('//div[contains(@class, "prod")]')

# Text matching
widget = tree.xpath('//div[h2[text()="Widget"]]')
```

### XPath Cheatsheet

| Expression | Meaning |
|------------|---------|
| `//div` | All div elements |
| `/html/body/div` | Absolute path |
| `//div[@class]` | Divs with class attribute |
| `//div[@class="product"]` | Exact class match |
| `//div[contains(@class, "prod")]` | Class contains |
| `//div/h2` | h2 children of div |
| `//div//h2` | h2 descendants of div |
| `//div/text()` | Direct text content |
| `//div//text()` | All text content |
| `//div/@id` | id attribute |
| `//div[1]` | First div |
| `//div[last()]` | Last div |
| `//div[position() < 3]` | First two divs |
| `//div[@id="x"]/following-sibling::div` | Following siblings |

### CSS Selectors with lxml

```python
from lxml.cssselect import CSSSelector

# Create selector
sel = CSSSelector('div.product')
products = sel(tree)

# Or use cssselect directly
tree.cssselect('div.product')
tree.cssselect('.price')
```

---

## 3. parsel

### Overview

Combines BeautifulSoup ease with lxml power. Used by Scrapy.

```python
from parsel import Selector

sel = Selector(text=html)
```

### CSS and XPath Together

```python
# CSS selectors
titles = sel.css('h2::text').getall()
first_title = sel.css('h2::text').get()

# XPath
prices = sel.xpath('//span[@class="price"]/text()').getall()
first_price = sel.xpath('//span[@class="price"]/text()').get()

# Chaining
products = sel.css('div.product')
for product in products:
    title = product.css('h2::text').get()
    price = product.xpath('.//span[@class="price"]/text()').get()
    link = product.css('a::attr(href)').get()
```

### Special Selectors

```python
# Text content (CSS)
sel.css('h2::text').get()           # Direct text
sel.css('div *::text').getall()     # All descendant text

# Attributes (CSS)
sel.css('a::attr(href)').get()
sel.css('div::attr(class)').get()

# With re (regex extraction)
sel.css('span.price::text').re(r'\$(\d+\.\d+)')
sel.css('span.price::text').re_first(r'\$(\d+\.\d+)')
```

---

## 4. JSON Parsing

### Standard Library

```python
import json

# Parse string
data = json.loads('{"name": "Widget", "price": 99.99}')

# Parse file
with open('data.json') as f:
    data = json.load(f)

# Access data
name = data['name']
price = data.get('price', 0)  # With default

# Nested data
products = data['products']
for product in products:
    print(product['name'])
```

### Handling Common Issues

```python
# JSON in HTML
import re
html = '<script>var data = {"products": [...]};</script>'
match = re.search(r'var data = ({.*?});', html)
if match:
    data = json.loads(match.group(1))

# JSON with trailing commas (invalid JSON)
import json5  # pip install json5
data = json5.loads('{"name": "Widget",}')  # Works!

# JSONL (one JSON per line)
with open('data.jsonl') as f:
    for line in f:
        item = json.loads(line)
```

### Large JSON Files

```python
import ijson  # pip install ijson

# Stream parse large file
with open('huge.json', 'rb') as f:
    for item in ijson.items(f, 'products.item'):
        process(item)
```

### jmespath for Complex Queries

```python
import jmespath  # pip install jmespath

data = {
    'products': [
        {'name': 'Widget', 'price': 99.99, 'stock': True},
        {'name': 'Gadget', 'price': 149.99, 'stock': False}
    ]
}

# Query
names = jmespath.search('products[*].name', data)
# ['Widget', 'Gadget']

in_stock = jmespath.search('products[?stock==`true`].name', data)
# ['Widget']

expensive = jmespath.search('products[?price > `100`]', data)
# [{'name': 'Gadget', ...}]
```

---

## 5. Regex for Parsing

### When to Use Regex

- Quick extraction of simple patterns
- Data not in clean HTML structure
- Embedded in JavaScript
- Performance-critical simple cases

### Common Patterns

```python
import re

html = '<span class="price">$99.99</span>'

# Extract number
price = re.search(r'\$(\d+\.\d{2})', html)
if price:
    value = float(price.group(1))  # 99.99

# All matches
prices = re.findall(r'\$(\d+\.\d{2})', html)

# Extract from JavaScript
js = 'var productId = 12345;'
product_id = re.search(r'productId\s*=\s*(\d+)', js).group(1)

# Multiple groups
pattern = r'(\w+)\s*:\s*"([^"]+)"'
matches = re.findall(pattern, 'name: "Widget", price: "99.99"')
# [('name', 'Widget'), ('price', '99.99')]
```

### Regex Tips

```python
# Non-greedy matching
re.search(r'<div>(.*)</div>', html)   # Greedy - matches too much
re.search(r'<div>(.*?)</div>', html)  # Non-greedy - minimal match

# Multiline
re.search(r'^Price:', html, re.MULTILINE)

# Ignore case
re.search(r'price', html, re.IGNORECASE)

# Verbose (readable)
pattern = re.compile(r'''
    \$                 # Dollar sign
    (\d+)              # Dollars
    \.                 # Decimal
    (\d{2})            # Cents
''', re.VERBOSE)
```

---

## 6. Comparison Table

| Library | Best For | Speed | Learning Curve |
|---------|----------|-------|----------------|
| **BeautifulSoup** | General HTML, messy markup | Medium | Easy |
| **lxml** | High volume, XPath needed | Fast | Medium |
| **parsel** | Scrapy projects, both CSS/XPath | Fast | Easy |
| **json** | Standard JSON | Fast | Easy |
| **regex** | Simple patterns, JS extraction | Very Fast | Medium |

---

## Common Patterns

### Extract All Links

```python
# BeautifulSoup
links = [a['href'] for a in soup.find_all('a', href=True)]

# lxml
links = tree.xpath('//a/@href')

# parsel
links = sel.css('a::attr(href)').getall()
```

### Extract Table Data

```python
# BeautifulSoup
table = soup.find('table')
rows = []
for tr in table.find_all('tr'):
    row = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
    rows.append(row)

# With pandas (easiest)
import pandas as pd
tables = pd.read_html(html)
df = tables[0]  # First table
```

### Extract JSON from Script

```python
import re
import json

# Find script with data
script = soup.find('script', string=re.compile('__INITIAL_STATE__'))
if script:
    match = re.search(r'__INITIAL_STATE__\s*=\s*({.*?});', script.string, re.DOTALL)
    if match:
        data = json.loads(match.group(1))
```

---

## Summary

| Task | Best Tool |
|------|-----------|
| General HTML parsing | BeautifulSoup |
| High-performance parsing | lxml |
| Need both CSS and XPath | parsel |
| Simple pattern extraction | regex |
| JSON API responses | json (stdlib) |
| Complex JSON queries | jmespath |
| HTML tables | pandas.read_html |

---

*Next: [04_proxy_services_overview.md](04_proxy_services_overview.md) - Proxy providers and services*
