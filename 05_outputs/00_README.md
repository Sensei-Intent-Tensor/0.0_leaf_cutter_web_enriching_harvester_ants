# 05_outputs

> **Data Schemas and Output Formats**

This section defines standardized output schemas for scraped data, ensuring consistency across all scrapers in the framework.

---

## 📁 Directory Structure

```
05_outputs/
├── 00_README.md          # This file
└── 00_schemas/           # JSON Schema definitions
    ├── base_item.json    # Common fields for all items
    ├── product.json      # E-commerce product schema
    ├── company.json      # Business entity schema
    ├── person.json       # Person/contact schema
    ├── job.json          # Job listing schema
    ├── property.json     # Real estate schema
    └── article.json      # News/content schema
```

---

## 🎯 Design Principles

### 1. Consistent Base Fields

Every scraped item includes:

```json
{
  "_id": "unique-identifier",
  "_source": "source-site.com",
  "_scraped_at": "2024-01-15T10:30:00Z",
  "_url": "https://source-site.com/page",
  "_version": 1
}
```

### 2. Domain-Specific Extensions

Each domain (products, jobs, etc.) extends the base with specific fields.

### 3. Nullable by Default

Fields may be null/missing - scrapers extract what's available.

---

## 📊 Core Schemas

### Product Schema

```json
{
  "name": "Widget Pro 3000",
  "price": 99.99,
  "currency": "USD",
  "brand": "Acme",
  "sku": "WP3000",
  "description": "Professional grade widget",
  "categories": ["Tools", "Professional"],
  "images": ["https://..."],
  "availability": "in_stock",
  "rating": 4.5,
  "review_count": 128,
  
  "_id": "acme-wp3000",
  "_source": "acme.com",
  "_scraped_at": "2024-01-15T10:30:00Z"
}
```

### Company Schema

```json
{
  "name": "Acme Corporation",
  "legal_name": "Acme Corp LLC",
  "industry": "Manufacturing",
  "description": "Leading widget manufacturer",
  "website": "https://acme.com",
  "phone": "+1-555-123-4567",
  "email": "contact@acme.com",
  "address": {
    "street": "123 Main St",
    "city": "Springfield",
    "state": "IL",
    "zip": "62701",
    "country": "US"
  },
  "employees": "100-500",
  "founded": 1985,
  "social": {
    "linkedin": "https://linkedin.com/company/acme",
    "twitter": "https://twitter.com/acme"
  }
}
```

### Job Schema

```json
{
  "title": "Senior Software Engineer",
  "company": "Acme Corp",
  "location": "San Francisco, CA",
  "remote": "hybrid",
  "salary_min": 150000,
  "salary_max": 200000,
  "salary_currency": "USD",
  "description": "We're looking for...",
  "requirements": ["5+ years experience", "Python"],
  "benefits": ["Health insurance", "401k"],
  "employment_type": "full_time",
  "posted_date": "2024-01-10",
  "apply_url": "https://..."
}
```

---

## 🔄 Output Formats

### JSON Lines (Recommended)

```python
import json

def write_jsonl(items, filepath):
    with open(filepath, 'w') as f:
        for item in items:
            f.write(json.dumps(item) + '\n')
```

### CSV Export

```python
import pandas as pd

def to_csv(items, filepath):
    df = pd.DataFrame(items)
    df.to_csv(filepath, index=False)
```

### Database Insert

```python
def to_database(items, connection, table):
    df = pd.DataFrame(items)
    df.to_sql(table, connection, if_exists='append', index=False)
```

---

## ✅ Validation

Use JSON Schema for validation:

```python
from jsonschema import validate, ValidationError

def validate_item(item, schema):
    try:
        validate(instance=item, schema=schema)
        return True, None
    except ValidationError as e:
        return False, str(e)
```

---

## 🔗 Related Sections

- **[03_enrichment_pipelines/](../03_enrichment_pipelines/)** - Data cleaning and normalization
- **[01_ant_anatomy/](../01_ant_anatomy/)** - Scraper output handling

---

*Part of the [Leaf Cutter Web Enriching Harvester Ants](../) framework*
