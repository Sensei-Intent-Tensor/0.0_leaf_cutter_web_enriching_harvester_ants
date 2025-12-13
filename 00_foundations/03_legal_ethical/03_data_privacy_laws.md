# Data Privacy Laws

> **GDPR, CCPA, and the Global Privacy Landscape**

Scraping personal data can trigger serious legal obligations. This document covers the key privacy regulations you need to understand.

---

## The Privacy Challenge

```
Traditional Scraping:                Privacy-Era Scraping:
┌─────────────────────────┐         ┌─────────────────────────┐
│ Scrape everything       │         │ What data am I getting? │
│ Store forever           │   →     │ Is any of it personal?  │
│ Use however             │         │ Do I have legal basis?  │
│ Share freely            │         │ How long can I keep it? │
└─────────────────────────┘         └─────────────────────────┘
```

---

## What is Personal Data?

### Under GDPR (Broad Definition)

Any information relating to an identified or identifiable person:

```
Definitely Personal:
├── Name
├── Email address
├── Phone number
├── Physical address
├── Social security number
├── ID numbers
├── IP address
├── Location data
├── Cookie identifiers
└── Biometric data

Possibly Personal (Context-Dependent):
├── Job title + company
├── Profile photos
├── User-generated content
├── Purchase history
├── Browsing patterns
└── Device fingerprints
```

### Special Category Data (Extra Sensitive)

```
Requires explicit consent:
├── Racial or ethnic origin
├── Political opinions
├── Religious beliefs
├── Trade union membership
├── Genetic data
├── Biometric data (for ID)
├── Health data
├── Sex life or orientation
└── Criminal records
```

---

## GDPR (European Union)

### General Data Protection Regulation

**Applies to:** 
- Organizations in the EU
- Organizations outside EU processing EU residents' data

### Key Principles

| Principle | Meaning for Scrapers |
|-----------|----------------------|
| **Lawfulness** | Need legal basis to process |
| **Purpose limitation** | Only use for stated purpose |
| **Data minimization** | Only collect what's needed |
| **Accuracy** | Keep data correct and current |
| **Storage limitation** | Don't keep longer than needed |
| **Integrity** | Keep data secure |
| **Accountability** | Document compliance |

### Legal Bases for Processing

To scrape personal data, you need one of:

| Basis | Applicability to Scraping |
|-------|---------------------------|
| **Consent** | Rarely applicable (didn't ask the person) |
| **Contract** | Only if data subject is party |
| **Legal obligation** | Rare |
| **Vital interests** | Emergency only |
| **Public task** | Government/public authority |
| **Legitimate interests** | Most common for scraping |

### Legitimate Interests Test

```
Three-part test:
1. Purpose Test: Is there a legitimate interest?
   └── Business research, market analysis, journalism

2. Necessity Test: Is scraping necessary?
   └── No less intrusive way to get the data?

3. Balancing Test: Does interest outweigh individual rights?
   └── Consider: sensitivity, expectations, safeguards
```

### Individual Rights

People whose data you scrape have rights:

| Right | Implication |
|-------|-------------|
| **Access** | They can ask what you have |
| **Rectification** | They can ask you to correct it |
| **Erasure** | They can ask you to delete it |
| **Restriction** | They can limit how you use it |
| **Portability** | They can get a copy |
| **Object** | They can object to processing |

### Penalties

```
Tier 1: Up to €10 million or 2% global turnover
Tier 2: Up to €20 million or 4% global turnover
```

---

## CCPA/CPRA (California)

### California Consumer Privacy Act / Privacy Rights Act

**Applies to:** Businesses that:
- Have $25M+ annual revenue, OR
- Buy/sell data of 100,000+ consumers, OR
- 50%+ revenue from selling personal data

### Key Rights

| Right | Description |
|-------|-------------|
| **Know** | What data is collected |
| **Delete** | Request deletion |
| **Opt-Out** | Of sale of data |
| **Non-Discrimination** | For exercising rights |
| **Correct** | Inaccurate data |
| **Limit** | Use of sensitive data |

### "Sale" of Data

CCPA defines "sale" broadly:
```
Selling = sharing personal info for monetary 
or other valuable consideration
```

If you scrape data and share it (even free), you may be "selling."

### Penalties

```
$2,500 per unintentional violation
$7,500 per intentional violation
Private right of action for data breaches
```

---

## Other Privacy Laws

### Brazil - LGPD

```
Lei Geral de Proteção de Dados
├── Similar to GDPR
├── Applies to Brazil data processing
├── Fines up to 2% revenue (R$50M cap)
└── Effective since 2020
```

### Canada - PIPEDA

```
Personal Information Protection and Electronic Documents Act
├── Applies to commercial activities
├── Requires consent for collection
├── Less severe than GDPR
└── Being updated (Bill C-27)
```

### UK - UK GDPR

```
Post-Brexit version of GDPR
├── Nearly identical to EU GDPR
├── Enforced by ICO
├── Same penalty structure
└── Minor divergences emerging
```

### Other Jurisdictions

| Region | Law | Notes |
|--------|-----|-------|
| **China** | PIPL | Very strict, requires localization |
| **India** | DPDPA | New law, broad scope |
| **Australia** | Privacy Act | Consent-based, penalties increasing |
| **Japan** | APPI | Adequate finding with EU |
| **South Korea** | PIPA | Strict, high penalties |

---

## Practical Compliance

### Decision Framework

```
Start Here:
    │
    ▼
Am I scraping personal data?
    │
    ├── NO → Proceed with normal scraping ethics
    │
    └── YES
        │
        ▼
    Is the data publicly available?
        │
        ├── NO → High risk, consider stopping
        │
        └── YES
            │
            ▼
        Do I have a legitimate interest?
            │
            ├── NO → Find different approach
            │
            └── YES
                │
                ▼
            Have I minimized data collection?
                │
                ├── NO → Reduce scope
                │
                └── YES
                    │
                    ▼
                Can I handle individual rights requests?
                    │
                    ├── NO → Build capability first
                    │
                    └── YES → Document and proceed carefully
```

### Compliance Checklist

```python
compliance_checklist = {
    'data_audit': {
        'description': 'Know what personal data you have',
        'actions': [
            'Inventory all scraped data',
            'Identify personal data elements',
            'Map data flows',
            'Document sources'
        ]
    },
    'legal_basis': {
        'description': 'Document your legal basis',
        'actions': [
            'Conduct legitimate interests assessment',
            'Document purpose and necessity',
            'Balance against individual rights'
        ]
    },
    'minimization': {
        'description': 'Collect only what you need',
        'actions': [
            'Remove unnecessary personal data',
            'Anonymize where possible',
            'Aggregate rather than individual'
        ]
    },
    'security': {
        'description': 'Protect the data',
        'actions': [
            'Encrypt storage',
            'Limit access',
            'Regular security audits'
        ]
    },
    'retention': {
        'description': 'Dont keep data forever',
        'actions': [
            'Define retention periods',
            'Implement deletion schedules',
            'Document retention policy'
        ]
    },
    'rights_handling': {
        'description': 'Handle individual requests',
        'actions': [
            'Process to receive requests',
            'Ability to find individuals data',
            'Ability to delete on request'
        ]
    }
}
```

### Anonymization Techniques

```python
def anonymize_data(record):
    """Remove or mask personal identifiers."""
    
    anonymized = record.copy()
    
    # Remove direct identifiers
    fields_to_remove = ['name', 'email', 'phone', 'address', 'ssn']
    for field in fields_to_remove:
        if field in anonymized:
            del anonymized[field]
    
    # Generalize quasi-identifiers
    if 'age' in anonymized:
        anonymized['age_range'] = f"{(anonymized['age'] // 10) * 10}s"
        del anonymized['age']
    
    if 'zip_code' in anonymized:
        anonymized['region'] = anonymized['zip_code'][:3] + 'XX'
        del anonymized['zip_code']
    
    # Hash indirect identifiers
    if 'user_id' in anonymized:
        import hashlib
        anonymized['user_hash'] = hashlib.sha256(
            anonymized['user_id'].encode()
        ).hexdigest()[:16]
        del anonymized['user_id']
    
    return anonymized
```

---

## Safe Scraping Patterns

### Pattern 1: Aggregate Only

```python
# DON'T store individual records
bad_data = [
    {'name': 'John', 'age': 32, 'salary': 50000},
    {'name': 'Jane', 'age': 28, 'salary': 60000},
]

# DO store aggregates
good_data = {
    'sample_size': 2,
    'average_age': 30,
    'average_salary': 55000,
    'age_distribution': {'20-29': 1, '30-39': 1}
}
```

### Pattern 2: Immediate Anonymization

```python
def scrape_and_anonymize(url):
    data = scrape(url)
    
    # Anonymize immediately, never store raw
    anonymized = anonymize_data(data)
    
    # Only store anonymized version
    save_to_database(anonymized)
```

### Pattern 3: Purpose-Limited Collection

```python
def targeted_scrape(url, needed_fields):
    """Only extract fields you actually need."""
    
    full_data = scrape(url)
    
    # Only keep needed fields
    filtered = {k: v for k, v in full_data.items() if k in needed_fields}
    
    return filtered

# Usage - only get non-personal data needed for analysis
data = targeted_scrape(url, ['product_name', 'price', 'category'])
```

---

## Summary

| Law | Region | Key Points | Penalties |
|-----|--------|------------|-----------|
| **GDPR** | EU | Broad personal data definition, legitimate interests | €20M or 4% revenue |
| **CCPA/CPRA** | California | Consumer rights, broad "sale" definition | $7,500/violation |
| **LGPD** | Brazil | GDPR-like | 2% revenue |
| **PIPEDA** | Canada | Consent-focused | $100K CAD |
| **UK GDPR** | UK | Same as EU GDPR | £17.5M or 4% |

### Key Takeaways

1. **Know what's personal data** - It's broader than you think
2. **Have a legal basis** - Usually legitimate interests
3. **Minimize collection** - Only what you truly need
4. **Document everything** - Accountability is key
5. **Be ready for requests** - Access, deletion, etc.
6. **When in doubt, anonymize** - Removes most obligations

---

*Next: [04_ethical_guidelines.md](04_ethical_guidelines.md) - Beyond legal compliance*
