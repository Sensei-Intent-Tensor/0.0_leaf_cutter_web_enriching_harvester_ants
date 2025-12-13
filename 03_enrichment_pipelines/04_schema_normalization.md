# Schema Normalization

> **Standardizing Data Structures Across Sources**

Different sources return data in different formats. Schema normalization transforms heterogeneous data into a consistent structure.

---

## The Problem

```python
# Source A
{"product_name": "Widget", "cost": "$99.99", "in_stock": "yes"}

# Source B  
{"title": "Widget", "price": 99.99, "availability": True}

# Source C
{"item": {"name": "Widget"}, "pricing": {"amount": 99.99}, "stock": 1}

# Target Schema
{"name": "Widget", "price": 99.99, "available": True}
```

---

## 1. Field Mapping

### Basic Mapping

```python
def map_fields(record, mapping):
    """Map source fields to target fields."""
    result = {}
    
    for target_field, source_field in mapping.items():
        if isinstance(source_field, str):
            # Simple field mapping
            result[target_field] = record.get(source_field)
        elif isinstance(source_field, list):
            # Try multiple possible source fields
            for field in source_field:
                value = record.get(field)
                if value is not None:
                    result[target_field] = value
                    break
        elif callable(source_field):
            # Custom extraction function
            result[target_field] = source_field(record)
    
    return result

# Mapping configuration
mapping = {
    'name': ['product_name', 'title', 'name'],  # Try in order
    'price': lambda r: r.get('cost') or r.get('price'),
    'available': 'in_stock'
}

normalized = map_fields(source_record, mapping)
```

### Nested Field Access

```python
def get_nested(record, path, default=None):
    """Access nested fields using dot notation."""
    keys = path.split('.')
    value = record
    
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        elif isinstance(value, list) and key.isdigit():
            idx = int(key)
            value = value[idx] if idx < len(value) else None
        else:
            return default
        
        if value is None:
            return default
    
    return value

# Usage
record = {'item': {'details': {'name': 'Widget'}}}
name = get_nested(record, 'item.details.name')  # 'Widget'

# In mapping
mapping = {
    'name': lambda r: get_nested(r, 'item.details.name'),
    'price': lambda r: get_nested(r, 'pricing.amount'),
}
```

---

## 2. Type Coercion

```python
from typing import Any, Callable, Dict
from decimal import Decimal
from datetime import datetime
import dateutil.parser

def coerce_bool(value) -> bool:
    """Convert various values to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', 'yes', '1', 'on', 'available', 'in stock')
    if isinstance(value, (int, float)):
        return bool(value)
    return False

def coerce_decimal(value) -> Decimal:
    """Convert to Decimal."""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, str):
        # Remove currency symbols
        import re
        cleaned = re.sub(r'[^\d.-]', '', value)
        return Decimal(cleaned) if cleaned else None
    return Decimal(str(value))

def coerce_int(value) -> int:
    """Convert to integer."""
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        import re
        match = re.search(r'-?\d+', value.replace(',', ''))
        return int(match.group()) if match else None
    return int(value)

def coerce_datetime(value) -> datetime:
    """Convert to datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return dateutil.parser.parse(value)
    if isinstance(value, (int, float)):
        # Assume Unix timestamp
        return datetime.fromtimestamp(value)
    return None

def coerce_list(value) -> list:
    """Ensure value is a list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        # Try comma-separated
        return [v.strip() for v in value.split(',')]
    return [value]

# Type coercion registry
COERCERS = {
    'bool': coerce_bool,
    'decimal': coerce_decimal,
    'int': coerce_int,
    'datetime': coerce_datetime,
    'list': coerce_list,
    'str': str,
}
```

---

## 3. Schema Definition

```python
from dataclasses import dataclass, field
from typing import Optional, List, Any, Callable

@dataclass
class FieldSchema:
    """Schema definition for a single field."""
    name: str
    type: str = 'str'
    source: Any = None  # Field name, list of names, or callable
    required: bool = False
    default: Any = None
    transform: Callable = None  # Post-coercion transform

@dataclass
class RecordSchema:
    """Schema definition for a record type."""
    name: str
    fields: List[FieldSchema] = field(default_factory=list)
    
    def add_field(self, name, **kwargs):
        self.fields.append(FieldSchema(name=name, **kwargs))
        return self

# Define schema
product_schema = RecordSchema('product')
product_schema.add_field('name', 
    source=['product_name', 'title', 'name'],
    required=True
)
product_schema.add_field('price',
    type='decimal',
    source=['cost', 'price', 'pricing.amount'],
    required=True
)
product_schema.add_field('available',
    type='bool',
    source=['in_stock', 'availability', 'stock'],
    default=False
)
product_schema.add_field('categories',
    type='list',
    source='category'
)
```

---

## 4. Schema Normalizer

```python
class SchemaNormalizer:
    """Normalize records to a defined schema."""
    
    def __init__(self, schema: RecordSchema):
        self.schema = schema
    
    def _get_source_value(self, record, source):
        """Extract value from record using source definition."""
        if source is None:
            return None
        
        if callable(source):
            return source(record)
        
        if isinstance(source, list):
            for s in source:
                value = self._get_source_value(record, s)
                if value is not None:
                    return value
            return None
        
        if isinstance(source, str):
            if '.' in source:
                return get_nested(record, source)
            return record.get(source)
        
        return None
    
    def _coerce_value(self, value, type_name):
        """Coerce value to specified type."""
        if value is None:
            return None
        
        coercer = COERCERS.get(type_name, str)
        try:
            return coercer(value)
        except Exception:
            return None
    
    def normalize(self, record: dict) -> Optional[dict]:
        """Normalize a single record."""
        result = {}
        
        for field in self.schema.fields:
            # Get source value
            value = self._get_source_value(record, field.source or field.name)
            
            # Apply type coercion
            if value is not None:
                value = self._coerce_value(value, field.type)
            
            # Apply custom transform
            if value is not None and field.transform:
                value = field.transform(value)
            
            # Handle missing required fields
            if value is None:
                if field.required:
                    return None  # Skip record
                value = field.default
            
            result[field.name] = value
        
        return result
    
    def normalize_many(self, records: List[dict]) -> List[dict]:
        """Normalize multiple records."""
        normalized = []
        for record in records:
            result = self.normalize(record)
            if result is not None:
                normalized.append(result)
        return normalized

# Usage
normalizer = SchemaNormalizer(product_schema)
normalized_products = normalizer.normalize_many(raw_products)
```

---

## 5. Source-Specific Adapters

```python
class SourceAdapter:
    """Base class for source-specific normalization."""
    
    def __init__(self, schema: RecordSchema):
        self.normalizer = SchemaNormalizer(schema)
    
    def extract(self, raw_response) -> List[dict]:
        """Extract records from raw API/scrape response."""
        raise NotImplementedError
    
    def process(self, raw_response) -> List[dict]:
        """Extract and normalize records."""
        records = self.extract(raw_response)
        return self.normalizer.normalize_many(records)

class AmazonAdapter(SourceAdapter):
    """Adapter for Amazon product data."""
    
    def extract(self, raw_response):
        # Amazon-specific extraction logic
        return raw_response.get('results', [])

class EbayAdapter(SourceAdapter):
    """Adapter for eBay product data."""
    
    def extract(self, raw_response):
        # eBay returns items in different structure
        items = raw_response.get('findItemsResponse', [{}])[0]
        return items.get('searchResult', [{}])[0].get('item', [])

# Usage
amazon_adapter = AmazonAdapter(product_schema)
ebay_adapter = EbayAdapter(product_schema)

amazon_products = amazon_adapter.process(amazon_response)
ebay_products = ebay_adapter.process(ebay_response)

# Both produce same schema
all_products = amazon_products + ebay_products
```

---

## 6. Validation

```python
from typing import List, Tuple

class SchemaValidator:
    """Validate records against schema."""
    
    def __init__(self, schema: RecordSchema):
        self.schema = schema
    
    def validate(self, record: dict) -> Tuple[bool, List[str]]:
        """Validate record, return (valid, errors)."""
        errors = []
        
        for field in self.schema.fields:
            value = record.get(field.name)
            
            # Required check
            if field.required and value is None:
                errors.append(f"Missing required field: {field.name}")
                continue
            
            if value is None:
                continue
            
            # Type check
            expected_type = {
                'str': str,
                'int': int,
                'decimal': Decimal,
                'bool': bool,
                'datetime': datetime,
                'list': list,
            }.get(field.type)
            
            if expected_type and not isinstance(value, expected_type):
                errors.append(
                    f"Type mismatch for {field.name}: "
                    f"expected {field.type}, got {type(value).__name__}"
                )
        
        return len(errors) == 0, errors
    
    def validate_many(self, records: List[dict]) -> Tuple[List[dict], List[dict]]:
        """Validate many records, return (valid, invalid)."""
        valid = []
        invalid = []
        
        for record in records:
            is_valid, errors = self.validate(record)
            if is_valid:
                valid.append(record)
            else:
                invalid.append({'record': record, 'errors': errors})
        
        return valid, invalid
```

---

## 7. Complete Pipeline

```python
class NormalizationPipeline:
    """Complete normalization pipeline."""
    
    def __init__(self, schema: RecordSchema):
        self.schema = schema
        self.normalizer = SchemaNormalizer(schema)
        self.validator = SchemaValidator(schema)
        self.adapters = {}
    
    def register_adapter(self, source_name: str, adapter: SourceAdapter):
        """Register a source adapter."""
        self.adapters[source_name] = adapter
        return self
    
    def process(self, source_name: str, raw_data) -> dict:
        """Process data from a specific source."""
        adapter = self.adapters.get(source_name)
        
        if adapter:
            records = adapter.process(raw_data)
        else:
            # Direct normalization
            records = self.normalizer.normalize_many(
                raw_data if isinstance(raw_data, list) else [raw_data]
            )
        
        valid, invalid = self.validator.validate_many(records)
        
        return {
            'valid': valid,
            'invalid': invalid,
            'stats': {
                'total': len(records),
                'valid': len(valid),
                'invalid': len(invalid)
            }
        }

# Usage
pipeline = NormalizationPipeline(product_schema)
pipeline.register_adapter('amazon', AmazonAdapter(product_schema))
pipeline.register_adapter('ebay', EbayAdapter(product_schema))

result = pipeline.process('amazon', amazon_api_response)
print(f"Normalized {result['stats']['valid']} products")
```

---

## Summary

| Component | Purpose |
|-----------|---------|
| Field Mapping | Map source fields to target fields |
| Type Coercion | Convert values to correct types |
| Schema Definition | Define expected structure |
| Normalizer | Apply mapping and coercion |
| Adapter | Source-specific extraction |
| Validator | Verify normalized records |

---

*Next: [05_data_validation.md](05_data_validation.md) - Ensuring data quality*
