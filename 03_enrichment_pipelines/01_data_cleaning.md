# Data Cleaning

> **From Raw Scrape to Usable Data**

Raw scraped data is messy. This document covers techniques to clean, normalize, and prepare data for downstream use.

---

## The Cleaning Pipeline

```
Raw Data → Structural Cleaning → Text Normalization → Type Conversion → Validation → Clean Data
```

```python
class DataCleaner:
    """Pipeline for cleaning scraped data."""
    
    def __init__(self):
        self.steps = []
    
    def add_step(self, func):
        """Add a cleaning step."""
        self.steps.append(func)
        return self
    
    def clean(self, data):
        """Run all cleaning steps."""
        result = data
        for step in self.steps:
            result = step(result)
        return result

# Usage
cleaner = DataCleaner()
cleaner.add_step(strip_whitespace)
cleaner.add_step(normalize_unicode)
cleaner.add_step(remove_html_tags)
cleaner.add_step(convert_types)

clean_data = cleaner.clean(raw_data)
```

---

## 1. Structural Cleaning

### Remove HTML Tags

```python
import re
from bs4 import BeautifulSoup

def strip_html(text):
    """Remove HTML tags from text."""
    if not text:
        return text
    
    # Method 1: BeautifulSoup (handles malformed HTML)
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text(separator=' ')

def strip_html_regex(text):
    """Faster but less robust HTML stripping."""
    if not text:
        return text
    return re.sub(r'<[^>]+>', '', text)

# Handle common HTML entities
def decode_entities(text):
    """Convert HTML entities to characters."""
    import html
    return html.unescape(text)
```

### Flatten Nested Structures

```python
def flatten_dict(d, parent_key='', sep='_'):
    """Flatten nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}_{i}", sep).items())
                else:
                    items.append((f"{new_key}_{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)

# Example
nested = {
    'product': {
        'name': 'Widget',
        'pricing': {
            'amount': 99.99,
            'currency': 'USD'
        }
    }
}

flat = flatten_dict(nested)
# {'product_name': 'Widget', 'product_pricing_amount': 99.99, 'product_pricing_currency': 'USD'}
```

### Extract from Wrappers

```python
def unwrap_single_element(data):
    """Unwrap single-element lists and dicts."""
    if isinstance(data, list) and len(data) == 1:
        return unwrap_single_element(data[0])
    if isinstance(data, dict) and len(data) == 1:
        key = list(data.keys())[0]
        if key in ('data', 'result', 'results', 'items', 'records'):
            return unwrap_single_element(data[key])
    return data

# Example
wrapped = {'data': {'results': [{'name': 'Widget'}]}}
unwrapped = unwrap_single_element(wrapped)
# {'name': 'Widget'}
```

---

## 2. Text Normalization

### Whitespace Handling

```python
import re

def normalize_whitespace(text):
    """Normalize all whitespace to single spaces."""
    if not text:
        return text
    
    # Replace various whitespace with space
    text = re.sub(r'[\t\n\r\f\v]+', ' ', text)
    
    # Collapse multiple spaces
    text = re.sub(r' +', ' ', text)
    
    # Strip leading/trailing
    return text.strip()

def clean_text(text):
    """Full text cleaning pipeline."""
    if not text:
        return text
    
    # Strip HTML
    text = BeautifulSoup(text, 'html.parser').get_text()
    
    # Decode entities
    text = html.unescape(text)
    
    # Normalize whitespace
    text = normalize_whitespace(text)
    
    # Remove control characters
    text = ''.join(c for c in text if c.isprintable() or c == ' ')
    
    return text
```

### Unicode Normalization

```python
import unicodedata

def normalize_unicode(text):
    """Normalize Unicode to canonical form."""
    if not text:
        return text
    
    # NFKC: Compatibility decomposition + canonical composition
    # Converts things like ﬁ → fi, ① → 1
    return unicodedata.normalize('NFKC', text)

def remove_accents(text):
    """Remove accents from characters."""
    if not text:
        return text
    
    # NFD: Canonical decomposition (separates base char from accent)
    normalized = unicodedata.normalize('NFD', text)
    
    # Remove combining characters (accents)
    return ''.join(c for c in normalized 
                   if unicodedata.category(c) != 'Mn')

# "Café" → "Cafe"
```

### Case Normalization

```python
def normalize_case(text, style='lower'):
    """Normalize text case."""
    if not text:
        return text
    
    styles = {
        'lower': str.lower,
        'upper': str.upper,
        'title': str.title,
        'sentence': lambda s: s[0].upper() + s[1:].lower() if s else s
    }
    
    return styles.get(style, str.lower)(text)
```

---

## 3. Field-Specific Cleaning

### Price Cleaning

```python
import re
from decimal import Decimal

def clean_price(price_str):
    """Extract numeric price from string."""
    if not price_str:
        return None
    
    if isinstance(price_str, (int, float)):
        return Decimal(str(price_str))
    
    # Remove currency symbols and words
    cleaned = re.sub(r'[£$€¥₹]|USD|EUR|GBP', '', str(price_str))
    
    # Handle thousands separators (1,234.56 or 1.234,56)
    if ',' in cleaned and '.' in cleaned:
        if cleaned.rindex(',') > cleaned.rindex('.'):
            # European format: 1.234,56
            cleaned = cleaned.replace('.', '').replace(',', '.')
        else:
            # US format: 1,234.56
            cleaned = cleaned.replace(',', '')
    elif ',' in cleaned:
        # Could be 1,234 or 1,23
        parts = cleaned.split(',')
        if len(parts[-1]) == 2:
            # Likely decimal: 1,23
            cleaned = cleaned.replace(',', '.')
        else:
            # Likely thousands: 1,234
            cleaned = cleaned.replace(',', '')
    
    # Extract number
    match = re.search(r'[\d.]+', cleaned)
    if match:
        try:
            return Decimal(match.group())
        except:
            return None
    return None

# Examples:
# "$1,234.56" → 1234.56
# "€1.234,56" → 1234.56
# "£99.99" → 99.99
```

### Date Cleaning

```python
from datetime import datetime
import dateutil.parser

def clean_date(date_str, output_format='%Y-%m-%d'):
    """Parse various date formats to standard format."""
    if not date_str:
        return None
    
    if isinstance(date_str, datetime):
        return date_str.strftime(output_format)
    
    # Common replacements
    replacements = {
        'yesterday': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
        'today': datetime.now().strftime('%Y-%m-%d'),
    }
    
    lower = date_str.lower().strip()
    if lower in replacements:
        return replacements[lower]
    
    # Handle relative dates like "3 days ago"
    relative_match = re.match(r'(\d+)\s*(day|week|month|year)s?\s*ago', lower)
    if relative_match:
        num, unit = relative_match.groups()
        num = int(num)
        if unit == 'day':
            delta = timedelta(days=num)
        elif unit == 'week':
            delta = timedelta(weeks=num)
        elif unit == 'month':
            delta = timedelta(days=num * 30)
        elif unit == 'year':
            delta = timedelta(days=num * 365)
        return (datetime.now() - delta).strftime(output_format)
    
    # Use dateutil for everything else
    try:
        parsed = dateutil.parser.parse(date_str)
        return parsed.strftime(output_format)
    except:
        return None

# Examples:
# "3 days ago" → "2024-01-12"
# "Jan 15, 2024" → "2024-01-15"
# "15/01/2024" → "2024-01-15"
```

### Phone Number Cleaning

```python
import re

def clean_phone(phone_str, country_code='+1'):
    """Clean and format phone number."""
    if not phone_str:
        return None
    
    # Remove everything except digits and +
    digits = re.sub(r'[^\d+]', '', str(phone_str))
    
    # Remove leading + if present and store
    has_plus = digits.startswith('+')
    if has_plus:
        digits = digits[1:]
    
    # Handle US numbers
    if len(digits) == 10:
        return f"{country_code} ({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits.startswith('1'):
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    elif len(digits) > 10:
        return f"+{digits}"
    
    return phone_str  # Return original if can't parse

# "(555) 123-4567" → "+1 (555) 123-4567"
# "5551234567" → "+1 (555) 123-4567"
```

### URL Cleaning

```python
from urllib.parse import urlparse, urljoin, unquote

def clean_url(url, base_url=None):
    """Clean and normalize URL."""
    if not url:
        return None
    
    # Decode URL encoding
    url = unquote(url)
    
    # Handle relative URLs
    if base_url and not url.startswith(('http://', 'https://', '//')):
        url = urljoin(base_url, url)
    
    # Handle protocol-relative URLs
    if url.startswith('//'):
        url = 'https:' + url
    
    # Parse and reconstruct
    parsed = urlparse(url)
    
    # Remove tracking parameters
    if parsed.query:
        import re
        clean_query = re.sub(
            r'(^|&)(utm_[^&]+|fbclid|gclid|ref|source)=[^&]*',
            '',
            parsed.query
        )
        clean_query = clean_query.strip('&')
    else:
        clean_query = ''
    
    # Reconstruct URL
    clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if clean_query:
        clean += f"?{clean_query}"
    
    # Remove trailing slash for consistency
    return clean.rstrip('/')
```

---

## 4. Null/Empty Handling

```python
def clean_nulls(data, null_values=None):
    """Replace null-like values with None."""
    null_values = null_values or {
        '', 'null', 'none', 'n/a', 'na', 'nan', 
        '-', '--', 'undefined', 'not available'
    }
    
    if isinstance(data, dict):
        return {k: clean_nulls(v, null_values) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_nulls(item, null_values) for item in data]
    elif isinstance(data, str):
        if data.lower().strip() in null_values:
            return None
        return data
    return data

def remove_empty_fields(data):
    """Remove fields with None/empty values."""
    if isinstance(data, dict):
        return {
            k: remove_empty_fields(v) 
            for k, v in data.items() 
            if v is not None and v != '' and v != []
        }
    elif isinstance(data, list):
        return [remove_empty_fields(item) for item in data if item]
    return data
```

---

## 5. Complete Cleaning Class

```python
from dataclasses import dataclass
from typing import Any, Dict, List, Callable, Optional

@dataclass
class CleaningRule:
    """A single cleaning rule."""
    field: str
    cleaner: Callable
    required: bool = False
    default: Any = None

class RecordCleaner:
    """Clean records according to defined rules."""
    
    def __init__(self):
        self.rules: List[CleaningRule] = []
        self.global_cleaners: List[Callable] = []
    
    def add_rule(self, field: str, cleaner: Callable, 
                 required: bool = False, default: Any = None):
        """Add a field-specific cleaning rule."""
        self.rules.append(CleaningRule(field, cleaner, required, default))
        return self
    
    def add_global(self, cleaner: Callable):
        """Add a cleaner that runs on all fields."""
        self.global_cleaners.append(cleaner)
        return self
    
    def clean(self, record: Dict) -> Optional[Dict]:
        """Clean a single record."""
        result = {}
        
        for rule in self.rules:
            value = record.get(rule.field)
            
            # Apply cleaner
            try:
                cleaned = rule.cleaner(value)
            except Exception:
                cleaned = None
            
            # Handle None/missing
            if cleaned is None:
                if rule.required:
                    return None  # Skip record
                cleaned = rule.default
            
            result[rule.field] = cleaned
        
        # Copy non-ruled fields
        for key, value in record.items():
            if key not in result:
                # Apply global cleaners
                for cleaner in self.global_cleaners:
                    try:
                        value = cleaner(value)
                    except:
                        pass
                result[key] = value
        
        return result
    
    def clean_many(self, records: List[Dict]) -> List[Dict]:
        """Clean multiple records, filtering out invalid ones."""
        cleaned = []
        for record in records:
            result = self.clean(record)
            if result is not None:
                cleaned.append(result)
        return cleaned

# Usage
cleaner = RecordCleaner()
cleaner.add_rule('price', clean_price, required=True)
cleaner.add_rule('name', clean_text, required=True)
cleaner.add_rule('date', clean_date, default=None)
cleaner.add_rule('url', clean_url)
cleaner.add_global(normalize_whitespace)

clean_records = cleaner.clean_many(raw_records)
```

---

## Summary

| Task | Function | Example |
|------|----------|---------|
| Strip HTML | `strip_html()` | `<b>text</b>` → `text` |
| Clean price | `clean_price()` | `$1,234.56` → `1234.56` |
| Clean date | `clean_date()` | `3 days ago` → `2024-01-12` |
| Clean phone | `clean_phone()` | `(555) 123-4567` → `+1 (555) 123-4567` |
| Clean URL | `clean_url()` | Remove tracking params |
| Normalize text | `normalize_whitespace()` | Collapse spaces |

---

*Next: [02_entity_resolution.md](02_entity_resolution.md) - Matching and deduplicating entities*
