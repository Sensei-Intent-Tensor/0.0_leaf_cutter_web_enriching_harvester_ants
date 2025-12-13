# 04_jobs

> **Job Board & Career Site Scrapers**

Scrapers for job listings, company reviews, and salary data.

---

## 💼 Available Ants

| Ant | Site | Data Extracted | Difficulty |
|-----|------|----------------|------------|
| [generic_job_ant.py](generic_job_ant.py) | Any job board | Job listings via Schema.org | Easy |
| [job_api_ant.py](job_api_ant.py) | Sites with JSON APIs | Structured job data | Medium |

---

## 🎯 Common Use Cases

```
Job Scraping Scenarios:
├── Job Aggregation
│   ├── Multi-board search
│   ├── Deduplication
│   └── Unified format
│
├── Market Research
│   ├── Salary trends
│   ├── Skill demand analysis
│   └── Hiring patterns
│
├── Competitive Intelligence
│   ├── Competitor hiring
│   ├── Team growth tracking
│   └── Tech stack analysis
│
└── Job Alerts
    ├── New posting notifications
    ├── Keyword matching
    └── Location filtering
```

---

## ⚠️ Important Considerations

### Major Job Boards

| Site | robots.txt | API Available | Notes |
|------|------------|---------------|-------|
| Indeed | Restrictive | Yes (paid) | Aggressive blocking |
| LinkedIn | Restrictive | Yes (paid) | Legal concerns |
| Glassdoor | Restrictive | Limited | Review data protected |
| ZipRecruiter | Moderate | Yes | Partner program |

### Legal Precedent

- **hiQ vs LinkedIn**: Public data scraping upheld
- **However**: Job boards actively defend against scraping
- **Recommendation**: Use official APIs when available

### Best Practices

```python
# 1. Use Schema.org JobPosting when available
schema = soup.find('script', type='application/ld+json')
# Many job sites include structured data

# 2. Respect robots.txt
# Most job boards disallow automated access

# 3. Deduplicate aggressively
# Same job posted on multiple boards
```

---

## 📊 Standard Job Schema

```python
JOB_SCHEMA = {
    'title': str,           # Job title
    'company': str,         # Company name
    'location': {
        'city': str,
        'state': str,
        'country': str,
        'remote': bool,
    },
    'salary': {
        'min': float,
        'max': float,
        'currency': str,
        'period': str,      # 'yearly', 'hourly'
    },
    'description': str,
    'requirements': list,
    'posted_date': str,
    'apply_url': str,
    'source': str,
}
```

---

## 🔧 Example Usage

```python
from jobs import GenericJobAnt

ant = GenericJobAnt()

# Scrape a job posting
result = ant.scrape('https://example.com/jobs/software-engineer')

if result.success:
    job = result.data
    print(f"{job['title']} at {job['company']}")
    print(f"Location: {job['location']['city']}")
    print(f"Salary: ${job['salary']['min']}-${job['salary']['max']}")
```

---

*Part of [02_ant_farms](../) - Site-specific scraper collections*
