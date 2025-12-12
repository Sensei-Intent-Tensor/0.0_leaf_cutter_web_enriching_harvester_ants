# Harvesting & Enrichment Pipeline

> **From Raw Web Data to High-Value Datasets**

The journey from a web page to actionable data involves multiple stages. This document defines the pipeline concept and explains how raw "harvested" data becomes "enriched" information ready for analysis or application.

---

## The Pipeline Concept

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   SOURCE    │───▶│   HARVEST   │───▶│   CLEAN     │───▶│   ENRICH    │───▶│   OUTPUT    │
│             │    │             │    │             │    │             │    │             │
│  Web Pages  │    │  Raw Data   │    │  Valid Data │    │  Enhanced   │    │  Datasets   │
│  APIs       │    │  Extraction │    │  Normalized │    │  Augmented  │    │  Ready      │
│  Feeds      │    │             │    │             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

Each stage transforms data, adding value and reducing noise.

---

## Stage 1: Source Identification

### What It Is

Identifying and cataloging where data lives on the web.

### Activities

| Activity | Description |
|----------|-------------|
| **URL Discovery** | Finding pages that contain target data |
| **Pattern Recognition** | Identifying URL structures and pagination |
| **Source Evaluation** | Assessing data quality, update frequency, accessibility |
| **Access Planning** | Determining authentication needs, rate limits |

### Output

```json
{
  "source": {
    "name": "Yelp Business Listings",
    "base_url": "https://www.yelp.com",
    "data_type": "business_directory",
    "url_pattern": "/biz/{business_slug}",
    "pagination": "/search?find_loc={location}&start={offset}",
    "update_frequency": "daily",
    "anti_scraping": "moderate",
    "requires_auth": false
  }
}
```

---

## Stage 2: Harvesting (Raw Extraction)

### What It Is

The act of retrieving and extracting raw data from web sources. This is where scraping happens.

### The Harvest Mindset

> **"Get everything that might be useful, filter later."**

At the harvesting stage, you're collecting raw material. Don't over-filter—capture more than you think you need.

### Activities

| Activity | Description |
|----------|-------------|
| **HTTP Requests** | Fetching page content |
| **HTML Parsing** | Converting HTML to traversable structure |
| **Element Selection** | Using CSS/XPath to target data |
| **Data Extraction** | Pulling text, attributes, links |
| **Raw Storage** | Saving unprocessed extracted data |

### Harvested Data Characteristics

- **Messy**: Contains HTML artifacts, whitespace, encoding issues
- **Redundant**: May have duplicates across pages
- **Inconsistent**: Different formats, missing fields
- **Unvalidated**: No guarantee of accuracy
- **Complete**: Captures everything available

### Example: Raw Harvest Output

```json
{
  "_harvest_meta": {
    "url": "https://www.yelp.com/biz/joes-pizza-new-york",
    "harvested_at": "2024-01-15T14:32:00Z",
    "html_hash": "a3f2b1c4..."
  },
  "raw_data": {
    "name": "  Joe's Pizza  ",
    "address": "7 Carmine St\nNew York, NY 10014",
    "phone": "(212) 366-1182",
    "rating": "4.5",
    "review_count": "2,847 reviews",
    "price_range": "$$",
    "categories": ["Pizza", "Italian"],
    "hours_text": "Mon-Sun 10:00 AM - 2:00 AM",
    "website": "http://www.joespizzanyc.com"
  }
}
```

Notice: Extra whitespace, inconsistent formats, text that needs parsing.

---

## Stage 3: Cleaning (Data Hygiene)

### What It Is

Transforming raw harvested data into consistent, valid records.

### The Cleaning Mindset

> **"Make it consistent, make it valid, make it usable."**

### Activities

| Activity | Description |
|----------|-------------|
| **Whitespace Normalization** | Trim, collapse, standardize |
| **Format Standardization** | Consistent date, phone, address formats |
| **Type Conversion** | Strings to numbers, dates, booleans |
| **Null Handling** | Empty strings → null, missing field defaults |
| **Character Encoding** | UTF-8 normalization, entity decoding |
| **Deduplication** | Remove exact duplicates |

### Cleaning Operations

```python
# Before cleaning
raw = {
    "name": "  Joe's Pizza  ",
    "rating": "4.5",
    "review_count": "2,847 reviews",
    "phone": "(212) 366-1182",
    "price_range": "$$"
}

# After cleaning
clean = {
    "name": "Joe's Pizza",
    "rating": 4.5,                    # String → Float
    "review_count": 2847,             # Parsed number
    "phone": "+12123661182",          # E.164 format
    "price_level": 2                  # $$ → 2
}
```

### Validation Rules

```python
VALIDATION_RULES = {
    "name": {
        "type": "string",
        "min_length": 1,
        "max_length": 500,
        "required": True
    },
    "rating": {
        "type": "float",
        "min": 0.0,
        "max": 5.0,
        "required": False
    },
    "phone": {
        "type": "string",
        "pattern": r"^\+?[1-9]\d{1,14}$",  # E.164
        "required": False
    },
    "latitude": {
        "type": "float",
        "min": -90,
        "max": 90,
        "required": False
    }
}
```

---

## Stage 4: Enrichment (Value Addition)

### What It Is

Augmenting cleaned data with additional information from other sources or computed fields.

### The Enrichment Mindset

> **"What else can we know about this entity?"**

### Types of Enrichment

#### 4.1 Cross-Reference Enrichment

Adding data from other sources about the same entity:

```
Business Record
├── Base: Name, Address, Phone (from Yelp)
├── + BBB Rating (from BBB)
├── + LinkedIn Company Info (from LinkedIn)
├── + Domain Registration (from WHOIS)
└── + Social Profiles (from various platforms)
```

#### 4.2 Derived Enrichment

Computing new fields from existing data:

```python
enriched = {
    **clean_data,
    
    # Derived fields
    "slug": slugify(clean_data["name"]),
    "name_words": len(clean_data["name"].split()),
    "has_website": clean_data.get("website") is not None,
    "price_category": categorize_price(clean_data["price_level"]),
    "popularity_score": calculate_popularity(
        clean_data["rating"],
        clean_data["review_count"]
    )
}
```

#### 4.3 Geocoding Enrichment

Converting addresses to coordinates:

```python
enriched = {
    **clean_data,
    
    # Geocoded
    "latitude": 40.7303,
    "longitude": -74.0023,
    "neighborhood": "West Village",
    "borough": "Manhattan",
    "timezone": "America/New_York"
}
```

#### 4.4 Classification Enrichment

Adding categorical labels:

```python
enriched = {
    **clean_data,
    
    # Classified
    "business_type": "restaurant",
    "cuisine_primary": "italian",
    "price_tier": "mid_range",
    "size_category": "small_business",
    "chain_status": "independent"
}
```

#### 4.5 Temporal Enrichment

Adding time-based context:

```python
enriched = {
    **clean_data,
    
    # Temporal
    "business_age_years": 15,
    "last_review_days_ago": 3,
    "review_velocity": 12.5,  # reviews per month
    "trending": True
}
```

### Enrichment Example: Full Pipeline

```json
{
  "_meta": {
    "source": "yelp",
    "harvested_at": "2024-01-15T14:32:00Z",
    "cleaned_at": "2024-01-15T14:32:05Z",
    "enriched_at": "2024-01-15T14:32:10Z",
    "pipeline_version": "2.1.0"
  },
  
  "base": {
    "name": "Joe's Pizza",
    "address": "7 Carmine St, New York, NY 10014",
    "phone": "+12123661182",
    "rating": 4.5,
    "review_count": 2847,
    "price_level": 2,
    "categories": ["pizza", "italian"]
  },
  
  "enriched": {
    "geo": {
      "latitude": 40.7303,
      "longitude": -74.0023,
      "neighborhood": "West Village",
      "borough": "Manhattan",
      "zip": "10014"
    },
    "derived": {
      "slug": "joes-pizza-new-york",
      "popularity_score": 92.3,
      "review_velocity": 47.5,
      "has_website": true
    },
    "cross_reference": {
      "google_place_id": "ChIJ...",
      "bbb_rating": "A+",
      "facebook_page": "joespizzanyc"
    },
    "classification": {
      "business_type": "restaurant",
      "cuisine": "italian",
      "price_tier": "budget_friendly",
      "chain_status": "independent"
    }
  }
}
```

---

## Stage 5: Output (Storage & Delivery)

### What It Is

Storing enriched data in its final form for consumption.

### Output Formats

| Format | Use Case |
|--------|----------|
| **JSON/JSONL** | API consumption, flexible schema |
| **CSV** | Spreadsheet analysis, simple exports |
| **Parquet** | Big data, columnar analytics |
| **Database** | Queryable storage, relationships |
| **API** | Real-time access, integration |

### Output Schema

```python
OUTPUT_SCHEMA = {
    "id": "string",           # Unique identifier
    "source": "string",       # Origin platform
    "source_id": "string",    # ID on source platform
    "harvested_at": "datetime",
    "data": {},               # The enriched record
    "quality_score": "float", # Data quality metric
    "version": "integer"      # Record version
}
```

---

## Pipeline Orchestration

### Sequential vs Parallel

```
Sequential (Simple):
Source → Harvest → Clean → Enrich → Output

Parallel (Scalable):
                    ┌─ Clean ─┐
Source → Harvest ──┼─ Clean ─┼── Merge → Enrich → Output
                    └─ Clean ─┘
```

### Incremental Processing

```
Full Pipeline (Initial):
├── Harvest ALL records
├── Clean ALL records
├── Enrich ALL records
└── Output ALL records

Incremental Pipeline (Updates):
├── Harvest CHANGED records only
├── Clean CHANGED records only
├── Enrich CHANGED records only
└── Upsert to output
```

### Error Handling in Pipelines

```python
PIPELINE_CONFIG = {
    "stages": ["harvest", "clean", "enrich", "output"],
    "error_handling": {
        "harvest": "retry_3x_then_skip",
        "clean": "quarantine_invalid",
        "enrich": "partial_ok",
        "output": "retry_indefinitely"
    },
    "checkpoints": True,  # Save state between stages
    "dead_letter_queue": True  # Store failed records
}
```

---

## Quality Metrics

### Per-Stage Metrics

| Stage | Key Metrics |
|-------|-------------|
| **Harvest** | Success rate, pages/hour, bytes fetched |
| **Clean** | Validation pass rate, null rate, format errors |
| **Enrich** | Enrichment coverage, API success rate |
| **Output** | Records written, duplicates, schema violations |

### Data Quality Score

```python
def calculate_quality_score(record):
    score = 100
    
    # Penalize missing required fields
    for field in REQUIRED_FIELDS:
        if not record.get(field):
            score -= 10
    
    # Penalize missing optional fields
    for field in OPTIONAL_FIELDS:
        if not record.get(field):
            score -= 2
    
    # Penalize failed enrichments
    if not record.get("enriched", {}).get("geo"):
        score -= 5
    
    return max(0, score)
```

---

## The Leaf Cutter Ant Analogy

| Pipeline Stage | Ant Colony Equivalent |
|----------------|----------------------|
| **Source** | Scout ants finding food sources |
| **Harvest** | Forager ants cutting leaves |
| **Clean** | Worker ants trimming and processing |
| **Enrich** | Fungus garden adding nutrients |
| **Output** | Food storage for colony consumption |

Just as leaf cutter ants don't eat leaves directly—they process them to grow fungus which feeds the colony—we don't use raw web data directly. We process it through stages to create something more valuable.

---

## Summary

| Stage | Input | Output | Goal |
|-------|-------|--------|------|
| **Source** | Web | URLs + Metadata | Know where to look |
| **Harvest** | URLs | Raw extracted data | Get the raw material |
| **Clean** | Raw data | Valid, consistent data | Make it usable |
| **Enrich** | Clean data | Augmented data | Add value |
| **Output** | Enriched data | Stored datasets | Make it accessible |

---

## Key Principles

1. **Harvest wide, filter later** - Capture more than you need at extraction
2. **Clean aggressively** - Invalid data is worse than no data
3. **Enrich strategically** - Not all enrichment is worth the cost
4. **Version everything** - Track changes through the pipeline
5. **Fail gracefully** - One bad record shouldn't stop the pipeline

---

*Next: [03_bots_agents_spiders_glossary.md](03_bots_agents_spiders_glossary.md) - Complete glossary of scraping terminology*
