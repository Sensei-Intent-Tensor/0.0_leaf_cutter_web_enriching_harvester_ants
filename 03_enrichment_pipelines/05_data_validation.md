# Data Validation

> **Ensuring Data Quality and Integrity**

Validation catches errors before bad data enters your system. This document covers validation strategies for scraped data.

---

## Validation Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    VALIDATION PIPELINE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. SCHEMA VALIDATION                                          │
│     Required fields present? Types correct?                     │
│                                                                 │
│  2. FORMAT VALIDATION                                          │
│     Email valid? URL well-formed? Date parseable?              │
│                                                                 │
│  3. BUSINESS RULES                                             │
│     Price > 0? Date not in future? Consistent values?          │
│                                                                 │
│  4. CROSS-FIELD VALIDATION                                     │
│     sale_price < original_price? end_date > start_date?        │
│                                                                 │
│  5. EXTERNAL VALIDATION                                        │
│     Does URL exist? Is email deliverable?                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Schema Validation

### Using Pydantic

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class Product(BaseModel):
    """Product schema with validation."""
    
    name: str = Field(..., min_length=1, max_length=500)
    price: Decimal = Field(..., gt=0, le=1000000)
    url: str
    description: Optional[str] = None
    categories: List[str] = []
    available: bool = True
    scraped_at: datetime = Field(default_factory=datetime.now)
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    
    @validator('name')
    def clean_name(cls, v):
        return v.strip()
    
    class Config:
        # Allow extra fields (useful during development)
        extra = 'ignore'

# Usage
try:
    product = Product(**raw_data)
    # Valid! Use product.dict() to get clean data
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### Using Marshmallow

```python
from marshmallow import Schema, fields, validate, pre_load, post_load

class ProductSchema(Schema):
    """Product validation schema."""
    
    name = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    price = fields.Decimal(required=True, validate=validate.Range(min=0.01))
    url = fields.Url(required=True)
    description = fields.Str(allow_none=True)
    categories = fields.List(fields.Str())
    available = fields.Bool(load_default=True)
    
    @pre_load
    def clean_data(self, data, **kwargs):
        """Clean data before validation."""
        if 'name' in data:
            data['name'] = data['name'].strip()
        return data
    
    @post_load
    def add_metadata(self, data, **kwargs):
        """Add metadata after validation."""
        data['validated_at'] = datetime.now().isoformat()
        return data

# Usage
schema = ProductSchema()
result = schema.load(raw_data)  # Raises ValidationError if invalid
# Or
result = schema.load(raw_data, partial=True)  # Allow missing fields
```

---

## 2. Format Validators

```python
import re
from urllib.parse import urlparse
from datetime import datetime
import email_validator

class FormatValidators:
    """Collection of format validators."""
    
    @staticmethod
    def is_valid_email(value: str) -> bool:
        """Validate email format."""
        if not value:
            return False
        try:
            email_validator.validate_email(value, check_deliverability=False)
            return True
        except email_validator.EmailNotValidError:
            return False
    
    @staticmethod
    def is_valid_url(value: str) -> bool:
        """Validate URL format."""
        if not value:
            return False
        try:
            result = urlparse(value)
            return all([result.scheme in ('http', 'https'), result.netloc])
        except:
            return False
    
    @staticmethod
    def is_valid_phone(value: str, country='US') -> bool:
        """Validate phone number format."""
        if not value:
            return False
        # Simple US phone validation
        digits = re.sub(r'\D', '', value)
        if country == 'US':
            return len(digits) == 10 or (len(digits) == 11 and digits[0] == '1')
        return len(digits) >= 7
    
    @staticmethod
    def is_valid_date(value: str, formats=None) -> bool:
        """Validate date string."""
        if not value:
            return False
        formats = formats or ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y', '%Y-%m-%dT%H:%M:%S']
        for fmt in formats:
            try:
                datetime.strptime(value, fmt)
                return True
            except ValueError:
                continue
        return False
    
    @staticmethod
    def is_valid_zip(value: str, country='US') -> bool:
        """Validate ZIP/postal code."""
        if not value:
            return False
        patterns = {
            'US': r'^\d{5}(-\d{4})?$',
            'UK': r'^[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}$',
            'CA': r'^[A-Z]\d[A-Z] ?\d[A-Z]\d$',
        }
        pattern = patterns.get(country, r'^\w+$')
        return bool(re.match(pattern, value, re.IGNORECASE))
    
    @staticmethod
    def is_valid_uuid(value: str) -> bool:
        """Validate UUID format."""
        if not value:
            return False
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(pattern, value, re.IGNORECASE))
```

---

## 3. Business Rule Validation

```python
from typing import Callable, List, Tuple, Any
from dataclasses import dataclass

@dataclass
class ValidationRule:
    """A single validation rule."""
    name: str
    check: Callable[[dict], bool]
    message: str
    severity: str = 'error'  # 'error' or 'warning'

class BusinessValidator:
    """Validate records against business rules."""
    
    def __init__(self):
        self.rules: List[ValidationRule] = []
    
    def add_rule(self, name: str, check: Callable, message: str, 
                 severity: str = 'error'):
        """Add a validation rule."""
        self.rules.append(ValidationRule(name, check, message, severity))
        return self
    
    def validate(self, record: dict) -> Tuple[bool, List[dict]]:
        """Validate record against all rules."""
        errors = []
        warnings = []
        
        for rule in self.rules:
            try:
                passed = rule.check(record)
            except Exception as e:
                passed = False
            
            if not passed:
                issue = {
                    'rule': rule.name,
                    'message': rule.message,
                    'severity': rule.severity
                }
                if rule.severity == 'error':
                    errors.append(issue)
                else:
                    warnings.append(issue)
        
        is_valid = len(errors) == 0
        return is_valid, errors + warnings
    
    def validate_many(self, records: List[dict]) -> dict:
        """Validate multiple records."""
        valid = []
        invalid = []
        
        for record in records:
            is_valid, issues = self.validate(record)
            if is_valid:
                valid.append(record)
            else:
                invalid.append({'record': record, 'issues': issues})
        
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
validator = BusinessValidator()

# Price rules
validator.add_rule(
    'positive_price',
    lambda r: r.get('price', 0) > 0,
    'Price must be positive'
)

validator.add_rule(
    'reasonable_price',
    lambda r: r.get('price', 0) < 1000000,
    'Price seems unreasonably high',
    severity='warning'
)

# Sale price rule
validator.add_rule(
    'sale_price_lower',
    lambda r: r.get('sale_price') is None or r.get('sale_price') < r.get('price'),
    'Sale price must be lower than original price'
)

# Date rules
validator.add_rule(
    'not_future_date',
    lambda r: r.get('published_date') is None or 
              datetime.fromisoformat(r['published_date']) <= datetime.now(),
    'Published date cannot be in the future'
)

# Cross-field rule
validator.add_rule(
    'end_after_start',
    lambda r: r.get('end_date') is None or r.get('start_date') is None or
              r['end_date'] > r['start_date'],
    'End date must be after start date'
)

result = validator.validate_many(products)
```

---

## 4. Completeness Scoring

```python
class CompletenessScorer:
    """Score record completeness."""
    
    def __init__(self, required_fields: List[str], optional_fields: List[str]):
        self.required = required_fields
        self.optional = optional_fields
    
    def score(self, record: dict) -> dict:
        """Calculate completeness score."""
        # Required fields
        required_present = sum(
            1 for f in self.required 
            if record.get(f) is not None and record.get(f) != ''
        )
        required_score = required_present / len(self.required) if self.required else 1.0
        
        # Optional fields
        optional_present = sum(
            1 for f in self.optional 
            if record.get(f) is not None and record.get(f) != ''
        )
        optional_score = optional_present / len(self.optional) if self.optional else 1.0
        
        # Overall score (required weighted more)
        overall = (required_score * 0.7) + (optional_score * 0.3)
        
        return {
            'overall': round(overall, 2),
            'required_score': round(required_score, 2),
            'optional_score': round(optional_score, 2),
            'required_present': required_present,
            'required_total': len(self.required),
            'optional_present': optional_present,
            'optional_total': len(self.optional),
            'missing_required': [f for f in self.required if not record.get(f)],
            'missing_optional': [f for f in self.optional if not record.get(f)]
        }

# Usage
scorer = CompletenessScorer(
    required_fields=['name', 'price', 'url'],
    optional_fields=['description', 'brand', 'sku', 'images', 'rating']
)

for product in products:
    score = scorer.score(product)
    product['_completeness'] = score['overall']
    if score['overall'] < 0.5:
        print(f"Low quality: {product['name']} - missing {score['missing_required']}")
```

---

## 5. Anomaly Detection

```python
import statistics
from collections import Counter

class AnomalyDetector:
    """Detect anomalies in scraped data."""
    
    def __init__(self):
        self.numeric_fields = []
        self.categorical_fields = []
    
    def add_numeric(self, field: str):
        self.numeric_fields.append(field)
        return self
    
    def add_categorical(self, field: str):
        self.categorical_fields.append(field)
        return self
    
    def analyze(self, records: List[dict]) -> dict:
        """Analyze records for anomalies."""
        anomalies = []
        
        # Numeric anomalies (using z-score)
        for field in self.numeric_fields:
            values = [r.get(field) for r in records if r.get(field) is not None]
            if len(values) < 3:
                continue
            
            mean = statistics.mean(values)
            stdev = statistics.stdev(values)
            
            if stdev == 0:
                continue
            
            for i, record in enumerate(records):
                value = record.get(field)
                if value is not None:
                    z_score = (value - mean) / stdev
                    if abs(z_score) > 3:
                        anomalies.append({
                            'index': i,
                            'field': field,
                            'value': value,
                            'z_score': round(z_score, 2),
                            'type': 'numeric_outlier'
                        })
        
        # Categorical anomalies (rare values)
        for field in self.categorical_fields:
            values = [r.get(field) for r in records if r.get(field) is not None]
            counts = Counter(values)
            total = sum(counts.values())
            
            # Values appearing less than 1% of time
            rare_threshold = max(1, total * 0.01)
            rare_values = {v for v, c in counts.items() if c < rare_threshold}
            
            for i, record in enumerate(records):
                value = record.get(field)
                if value in rare_values:
                    anomalies.append({
                        'index': i,
                        'field': field,
                        'value': value,
                        'count': counts[value],
                        'type': 'rare_category'
                    })
        
        return {
            'anomalies': anomalies,
            'count': len(anomalies)
        }

# Usage
detector = AnomalyDetector()
detector.add_numeric('price')
detector.add_numeric('rating')
detector.add_categorical('category')
detector.add_categorical('brand')

result = detector.analyze(products)
for anomaly in result['anomalies']:
    print(f"Anomaly: {anomaly}")
```

---

## 6. Complete Validation Pipeline

```python
class ValidationPipeline:
    """Complete validation pipeline."""
    
    def __init__(self, schema_class=None):
        self.schema_class = schema_class
        self.business_validator = BusinessValidator()
        self.completeness_scorer = None
        self.anomaly_detector = None
    
    def process(self, records: List[dict]) -> dict:
        """Run full validation pipeline."""
        results = {
            'input_count': len(records),
            'stages': {}
        }
        
        current = records
        
        # Stage 1: Schema validation
        if self.schema_class:
            valid = []
            invalid = []
            for record in current:
                try:
                    validated = self.schema_class(**record)
                    valid.append(validated.dict())
                except Exception as e:
                    invalid.append({'record': record, 'error': str(e)})
            
            results['stages']['schema'] = {
                'valid': len(valid),
                'invalid': len(invalid)
            }
            current = valid
        
        # Stage 2: Business rules
        biz_result = self.business_validator.validate_many(current)
        results['stages']['business'] = biz_result['stats']
        current = biz_result['valid']
        
        # Stage 3: Completeness
        if self.completeness_scorer:
            for record in current:
                score = self.completeness_scorer.score(record)
                record['_quality_score'] = score['overall']
        
        # Stage 4: Anomaly detection
        if self.anomaly_detector and current:
            anomaly_result = self.anomaly_detector.analyze(current)
            results['stages']['anomalies'] = anomaly_result
        
        results['output_count'] = len(current)
        results['valid_records'] = current
        
        return results

# Usage
pipeline = ValidationPipeline(schema_class=Product)
pipeline.business_validator.add_rule(
    'positive_price',
    lambda r: r.get('price', 0) > 0,
    'Price must be positive'
)
pipeline.completeness_scorer = CompletenessScorer(
    required_fields=['name', 'price'],
    optional_fields=['description', 'brand']
)

result = pipeline.process(raw_products)
print(f"Valid: {result['output_count']} / {result['input_count']}")
```

---

## Summary

| Layer | Purpose | Tools |
|-------|---------|-------|
| Schema | Structure & types | Pydantic, Marshmallow |
| Format | Email, URL, phone | Regex, validators |
| Business | Domain rules | Custom validators |
| Cross-field | Related fields | Custom validators |
| Completeness | Data quality | Custom scorer |
| Anomaly | Outliers | Statistics |

---

*This completes the Enrichment Pipelines section!*
