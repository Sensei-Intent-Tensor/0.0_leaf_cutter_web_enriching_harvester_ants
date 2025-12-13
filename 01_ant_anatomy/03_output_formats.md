# Output Formats

> **Structuring and Validating Scraped Data**

Raw scraped data is just the beginning. This document covers how to structure, validate, and format your output for reliability and downstream use.

---

## Why Structure Matters

```
Unstructured Output:              Structured Output:
┌─────────────────────────┐      ┌─────────────────────────┐
│ "price": "$99.99"       │      │ "price": {              │
│ "stock": "In Stock"     │  →   │   "amount": 99.99,      │
│ "date": "Dec 12"        │      │   "currency": "USD"     │
│                         │      │ }                       │
│ Problems:               │      │ "stock": {              │
│ • Can't sort by price   │      │   "available": true,    │
│ • Can't filter by stock │      │   "quantity": null      │
│ • Can't compare dates   │      │ }                       │
└─────────────────────────┘      │ "date": "2024-12-12"    │
                                 └─────────────────────────┘
```

---

## Data Classes

### Basic Dataclass

```python
from dataclasses import dataclass, field, asdict
from typing import Optional, List
from datetime import datetime

@dataclass
class Product:
    """Structured product data."""
    
    # Required fields
    url: str
    title: str
    
    # Optional fields with defaults
    price: Optional[float] = None
    currency: str = "USD"
    description: Optional[str] = None
    images: List[str] = field(default_factory=list)
    
    # Metadata
    scraped_at: datetime = field(default_factory=datetime.utcnow)
    source: str = "unknown"
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        import json
        data = self.to_dict()
        data['scraped_at'] = data['scraped_at'].isoformat()
        return json.dumps(data)
```

### Using Dataclasses in Ants

```python
class ProductAnt(BaseAnt):
    def extract(self, soup: BeautifulSoup) -> dict:
        product = Product(
            url=self.current_url,
            title=self.safe_extract('h1', soup),
            price=self._parse_price(self.safe_extract('.price', soup)),
            description=self.safe_extract('.description', soup),
            images=self.safe_extract_all('img.product', soup, 'src'),
            source="example.com"
        )
        
        return product.to_dict()
    
    def _parse_price(self, price_str: str) -> Optional[float]:
        if not price_str:
            return None
        import re
        match = re.search(r'[\d,]+\.?\d*', price_str.replace(',', ''))
        return float(match.group()) if match else None
```

---

## Pydantic Models

### Why Pydantic?

- Runtime validation
- Type coercion
- Clear error messages
- JSON schema generation
- Serialization built-in

### Basic Model

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class Price(BaseModel):
    """Price with currency."""
    amount: float = Field(..., ge=0)
    currency: str = Field(default="USD", max_length=3)
    
    @validator('currency')
    def uppercase_currency(cls, v):
        return v.upper()

class Product(BaseModel):
    """Validated product data."""
    
    url: str
    title: str = Field(..., min_length=1, max_length=500)
    price: Optional[Price] = None
    description: Optional[str] = Field(None, max_length=10000)
    images: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    in_stock: bool = True
    
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        # Allow extra fields (don't fail on unknown)
        extra = 'ignore'
        
        # Example for documentation
        schema_extra = {
            "example": {
                "url": "https://example.com/product/123",
                "title": "Example Product",
                "price": {"amount": 99.99, "currency": "USD"},
                "in_stock": True
            }
        }
```

### Validation Examples

```python
from pydantic import validator, root_validator

class Product(BaseModel):
    title: str
    price: Optional[float] = None
    sale_price: Optional[float] = None
    
    @validator('title')
    def clean_title(cls, v):
        """Remove extra whitespace from title."""
        return ' '.join(v.split())
    
    @validator('price', 'sale_price', pre=True)
    def parse_price(cls, v):
        """Parse price from string."""
        if isinstance(v, str):
            import re
            match = re.search(r'[\d.]+', v.replace(',', ''))
            return float(match.group()) if match else None
        return v
    
    @root_validator
    def check_sale_price(cls, values):
        """Sale price must be less than regular price."""
        price = values.get('price')
        sale = values.get('sale_price')
        
        if price and sale and sale >= price:
            raise ValueError('sale_price must be less than price')
        
        return values
```

### Using Pydantic in Ants

```python
class ProductAnt(BaseAnt):
    def extract(self, soup: BeautifulSoup) -> dict:
        # Extract raw data
        raw_data = {
            'url': self.current_url,
            'title': self.safe_extract('h1', soup),
            'price': self.safe_extract('.price', soup),  # String like "$99.99"
            'description': self.safe_extract('.desc', soup),
        }
        
        # Validate and transform
        try:
            product = Product(**raw_data)
            return product.dict()
        except ValidationError as e:
            self.logger.warning(f"Validation failed: {e}")
            return {'_validation_error': str(e), **raw_data}
```

---

## Output Schemas

### JSON Schema Definition

```python
PRODUCT_SCHEMA = {
    "type": "object",
    "required": ["url", "title"],
    "properties": {
        "url": {
            "type": "string",
            "format": "uri"
        },
        "title": {
            "type": "string",
            "minLength": 1,
            "maxLength": 500
        },
        "price": {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "minimum": 0},
                "currency": {"type": "string", "pattern": "^[A-Z]{3}$"}
            },
            "required": ["amount"]
        },
        "images": {
            "type": "array",
            "items": {"type": "string", "format": "uri"}
        },
        "in_stock": {
            "type": "boolean"
        },
        "scraped_at": {
            "type": "string",
            "format": "date-time"
        }
    }
}
```

### Schema Validation

```python
import jsonschema

def validate_output(data: dict, schema: dict) -> tuple[bool, str]:
    """Validate data against JSON schema."""
    try:
        jsonschema.validate(data, schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, str(e)

# Usage
is_valid, error = validate_output(product_data, PRODUCT_SCHEMA)
```

---

## Common Output Formats

### Format 1: Flat Dictionary

Best for: Simple data, CSV export.

```python
{
    "url": "https://example.com/product/123",
    "title": "Widget Pro",
    "price_amount": 99.99,
    "price_currency": "USD",
    "stock_status": "in_stock",
    "stock_quantity": 45,
    "category_1": "Electronics",
    "category_2": "Gadgets",
    "scraped_at": "2024-12-12T10:30:00Z"
}
```

### Format 2: Nested Structure

Best for: Complex data, JSON storage.

```python
{
    "url": "https://example.com/product/123",
    "title": "Widget Pro",
    "price": {
        "amount": 99.99,
        "currency": "USD",
        "original": 129.99,
        "discount_percent": 23
    },
    "stock": {
        "status": "in_stock",
        "quantity": 45,
        "warehouse": "US-EAST"
    },
    "categories": ["Electronics", "Gadgets"],
    "metadata": {
        "scraped_at": "2024-12-12T10:30:00Z",
        "source": "example.com",
        "scraper_version": "1.0.0"
    }
}
```

### Format 3: With Raw Data

Best for: Debugging, reprocessing.

```python
{
    "extracted": {
        "title": "Widget Pro",
        "price": 99.99
    },
    "raw": {
        "title_element": "<h1 class='title'>Widget Pro</h1>",
        "price_element": "<span class='price'>$99.99</span>"
    },
    "metadata": {
        "url": "https://example.com/product/123",
        "status_code": 200,
        "scraped_at": "2024-12-12T10:30:00Z"
    }
}
```

---

## Data Cleaning Utilities

### Price Parser

```python
import re
from typing import Optional, Tuple

def parse_price(text: str) -> Tuple[Optional[float], str]:
    """
    Parse price from text.
    
    Returns (amount, currency) tuple.
    
    Examples:
        "$99.99" -> (99.99, "USD")
        "€49,99" -> (49.99, "EUR")
        "1,299.00 USD" -> (1299.00, "USD")
    """
    if not text:
        return None, "USD"
    
    # Currency detection
    currency_map = {
        '$': 'USD', '€': 'EUR', '£': 'GBP', '¥': 'JPY',
        'USD': 'USD', 'EUR': 'EUR', 'GBP': 'GBP'
    }
    
    currency = 'USD'
    for symbol, code in currency_map.items():
        if symbol in text:
            currency = code
            break
    
    # Extract number
    # Handle European format (1.234,56) vs US format (1,234.56)
    text_clean = text.replace(' ', '')
    
    # European format detection
    if re.search(r'\d+\.\d{3},\d{2}', text_clean):
        text_clean = text_clean.replace('.', '').replace(',', '.')
    else:
        text_clean = text_clean.replace(',', '')
    
    match = re.search(r'[\d.]+', text_clean)
    
    if match:
        try:
            return float(match.group()), currency
        except ValueError:
            pass
    
    return None, currency
```

### Text Cleaner

```python
import re
import html

def clean_text(text: str) -> str:
    """Clean scraped text."""
    if not text:
        return ""
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove common junk
    junk_patterns = [
        r'\s*\n\s*',  # Newlines
        r'\s{2,}',     # Multiple spaces
        r'^\s+|\s+$',  # Leading/trailing
    ]
    
    for pattern in junk_patterns:
        text = re.sub(pattern, ' ', text)
    
    return text.strip()
```

### Date Parser

```python
from datetime import datetime
from typing import Optional
import re

def parse_date(text: str) -> Optional[datetime]:
    """
    Parse date from various formats.
    
    Handles: "Dec 12, 2024", "12/12/2024", "2024-12-12", "Yesterday", etc.
    """
    if not text:
        return None
    
    text = text.strip().lower()
    
    # Relative dates
    if text == 'today':
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if text == 'yesterday':
        from datetime import timedelta
        return (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Common formats
    formats = [
        '%Y-%m-%d',           # 2024-12-12
        '%Y/%m/%d',           # 2024/12/12
        '%m/%d/%Y',           # 12/12/2024
        '%d/%m/%Y',           # 12/12/2024
        '%B %d, %Y',          # December 12, 2024
        '%b %d, %Y',          # Dec 12, 2024
        '%d %B %Y',           # 12 December 2024
        '%d %b %Y',           # 12 Dec 2024
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(text.title(), fmt)
        except ValueError:
            continue
    
    return None
```

---

## Export Functions

### JSON Export

```python
import json
from datetime import datetime
from pathlib import Path

class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def export_json(data: list, filepath: str, pretty: bool = True):
    """Export data to JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(
            data, f,
            cls=DateTimeEncoder,
            indent=2 if pretty else None,
            ensure_ascii=False
        )

def export_jsonl(data: list, filepath: str):
    """Export data to JSON Lines file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, cls=DateTimeEncoder, ensure_ascii=False))
            f.write('\n')
```

### CSV Export

```python
import csv
from typing import List, Dict

def flatten_dict(d: dict, parent_key: str = '', sep: str = '_') -> dict:
    """Flatten nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        elif isinstance(v, list):
            items.append((new_key, ', '.join(str(x) for x in v)))
        else:
            items.append((new_key, v))
    return dict(items)

def export_csv(data: List[Dict], filepath: str):
    """Export data to CSV file."""
    if not data:
        return
    
    # Flatten all records
    flat_data = [flatten_dict(item) for item in data]
    
    # Get all unique keys
    all_keys = set()
    for item in flat_data:
        all_keys.update(item.keys())
    
    fieldnames = sorted(all_keys)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flat_data)
```

---

## Output Pipeline

```python
class OutputPipeline:
    """Pipeline for processing and exporting scraped data."""
    
    def __init__(self, schema: dict = None):
        self.schema = schema
        self.items = []
        self.errors = []
    
    def process(self, item: dict) -> dict:
        """Process a single item through the pipeline."""
        
        # Step 1: Clean text fields
        item = self._clean_text_fields(item)
        
        # Step 2: Parse special fields
        item = self._parse_special_fields(item)
        
        # Step 3: Validate
        if self.schema:
            is_valid, error = validate_output(item, self.schema)
            if not is_valid:
                self.errors.append({'item': item, 'error': error})
                return None
        
        # Step 4: Add metadata
        item['_processed_at'] = datetime.utcnow().isoformat()
        
        self.items.append(item)
        return item
    
    def _clean_text_fields(self, item: dict) -> dict:
        """Clean all string fields."""
        for key, value in item.items():
            if isinstance(value, str):
                item[key] = clean_text(value)
        return item
    
    def _parse_special_fields(self, item: dict) -> dict:
        """Parse prices, dates, etc."""
        if 'price' in item and isinstance(item['price'], str):
            amount, currency = parse_price(item['price'])
            item['price'] = {'amount': amount, 'currency': currency}
        
        if 'date' in item and isinstance(item['date'], str):
            item['date'] = parse_date(item['date'])
        
        return item
    
    def export(self, filepath: str, format: str = 'json'):
        """Export processed items."""
        if format == 'json':
            export_json(self.items, filepath)
        elif format == 'jsonl':
            export_jsonl(self.items, filepath)
        elif format == 'csv':
            export_csv(self.items, filepath)
    
    def report(self) -> dict:
        """Get processing report."""
        return {
            'processed': len(self.items),
            'errors': len(self.errors),
            'error_rate': len(self.errors) / (len(self.items) + len(self.errors)) if self.items or self.errors else 0
        }
```

---

## Summary

| Approach | Best For | Pros | Cons |
|----------|----------|------|------|
| **Dict** | Quick prototyping | Simple, flexible | No validation |
| **Dataclass** | Internal structure | Type hints, light | Basic validation |
| **Pydantic** | Production | Full validation | Extra dependency |
| **JSON Schema** | API contracts | Standard, shareable | External file |

### Key Principles

1. **Validate early** - Catch errors at extraction
2. **Type appropriately** - Numbers as numbers, dates as dates
3. **Include metadata** - Source, timestamp, version
4. **Handle nulls** - Missing data is normal
5. **Clean consistently** - Same cleaning for same fields

---

*Next: [04_error_handling.md](04_error_handling.md) - Robust error handling strategies*
