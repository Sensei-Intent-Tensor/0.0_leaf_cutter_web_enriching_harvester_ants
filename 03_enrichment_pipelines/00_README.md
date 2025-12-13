# 03_enrichment_pipelines

> **Transforming Raw Scrapes into Clean, Usable Data**

Raw scraped data is messy, inconsistent, and often duplicated. This section covers the enrichment pipeline that transforms raw data into clean, validated, production-ready records.

---

## 📚 Documents in This Section

| # | Document | Lines | Description |
|---|----------|-------|-------------|
| 01 | [Data Cleaning](01_data_cleaning.md) | 541 | Strip HTML, normalize text, clean prices/dates |
| 02 | [Entity Resolution](02_entity_resolution.md) | 528 | Match records representing same entity |
| 03 | [Deduplication](03_deduplication.md) | 478 | Remove duplicate records |
| 04 | [Schema Normalization](04_schema_normalization.md) | 484 | Standardize data structures |
| 05 | [Data Validation](05_data_validation.md) | 552 | Ensure data quality and integrity |

**Total: ~2,583 lines of data transformation guidance**

---

## 🔄 The Enrichment Pipeline

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   RAW       │   │   CLEAN     │   │  NORMALIZE  │   │  DEDUPE     │   │  VALIDATE   │
│   SCRAPE    │──▶│   DATA      │──▶│  SCHEMA     │──▶│  RECORDS    │──▶│  OUTPUT     │
└─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
     │                  │                 │                 │                 │
     │                  │                 │                 │                 │
  Messy HTML        Strip tags       Map fields        Remove dupes      Check rules
  Mixed formats     Clean text       Coerce types      Merge matches     Score quality
  Duplicates        Fix prices       Standardize       Cluster           Detect anomalies
```

---

## 🎯 Quick Reference

### Data Cleaning

```python
from bs4 import BeautifulSoup
import re

def clean_record(raw):
    return {
        'name': BeautifulSoup(raw['name'], 'html.parser').get_text().strip(),
        'price': float(re.sub(r'[^\d.]', '', raw['price'])),
        'date': dateutil.parser.parse(raw['date']).strftime('%Y-%m-%d')
    }
```

### Deduplication

```python
def dedupe(records, key_fields):
    seen = set()
    unique = []
    for record in records:
        key = tuple(record.get(f) for f in key_fields)
        if key not in seen:
            seen.add(key)
            unique.append(record)
    return unique
```

### Schema Normalization

```python
from pydantic import BaseModel
from decimal import Decimal

class Product(BaseModel):
    name: str
    price: Decimal
    url: str
    available: bool = True

# Validates and coerces types
product = Product(**raw_data)
```

### Validation

```python
def validate(record):
    errors = []
    if record.get('price', 0) <= 0:
        errors.append('Price must be positive')
    if not record.get('url', '').startswith('http'):
        errors.append('Invalid URL')
    return len(errors) == 0, errors
```

---

## 📊 Pipeline Components

| Component | Input | Output | Key Operations |
|-----------|-------|--------|----------------|
| **Cleaner** | Raw HTML/text | Clean text | Strip tags, normalize whitespace |
| **Normalizer** | Varied schemas | Unified schema | Map fields, coerce types |
| **Deduplicator** | All records | Unique records | Hash, compare, merge |
| **Resolver** | Similar records | Merged entities | Block, match, cluster |
| **Validator** | Normalized data | Validated data | Check rules, score quality |

---

## 🛠️ Implementation Pattern

```python
class EnrichmentPipeline:
    """Complete data enrichment pipeline."""
    
    def __init__(self):
        self.cleaner = DataCleaner()
        self.normalizer = SchemaNormalizer(schema)
        self.deduper = Deduplicator()
        self.validator = Validator()
    
    def process(self, raw_records):
        # Step 1: Clean
        cleaned = [self.cleaner.clean(r) for r in raw_records]
        
        # Step 2: Normalize
        normalized = self.normalizer.normalize_many(cleaned)
        
        # Step 3: Deduplicate
        unique = self.deduper.dedupe(normalized)
        
        # Step 4: Validate
        valid, invalid = self.validator.validate_many(unique)
        
        return {
            'valid': valid,
            'invalid': invalid,
            'stats': {
                'input': len(raw_records),
                'output': len(valid),
                'rejected': len(invalid)
            }
        }
```

---

## 📈 Quality Metrics

Track these metrics through your pipeline:

| Metric | Description | Target |
|--------|-------------|--------|
| **Completeness** | % of fields populated | >80% |
| **Validity** | % passing validation | >95% |
| **Uniqueness** | % after deduplication | Track trend |
| **Consistency** | Same entity, same values | >99% |

---

## 🔗 Related Sections

- **[00_foundations/](../00_foundations/)** - Core concepts
- **[01_ant_anatomy/](../01_ant_anatomy/)** - Scraper structure
- **[02_ant_farms/](../02_ant_farms/)** - Source-specific scrapers
- **[04_colony_orchestration/](../04_colony_orchestration/)** - Running at scale

---

*Part of the [Leaf Cutter Web Enriching Harvester Ants](../) framework*
