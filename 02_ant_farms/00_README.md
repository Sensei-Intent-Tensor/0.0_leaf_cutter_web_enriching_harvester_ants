# 02_ant_farms

> **Platform-Specific Scrapers Organized by Industry**

This section contains specialized scrapers for specific websites and platforms, organized by industry vertical.

---

## 📁 Directory Structure

```
02_ant_farms/
├── 00_social/                    # Social media platforms
│   ├── 00_linkedin/              # LinkedIn profiles & companies
│   ├── 01_facebook/              # Facebook pages
│   ├── 02_twitter_x/             # Twitter/X data
│   ├── 03_instagram/             # Instagram profiles
│   └── 04_tiktok/                # TikTok data
│
├── 01_business_directories/      # Business listings
│   ├── 00_google_maps/           # Google Maps/Places
│   ├── 01_yelp/                  # Yelp reviews
│   ├── 02_bbb/                   # Better Business Bureau
│   ├── 03_yellow_pages/          # Yellow Pages
│   ├── 04_white_pages/           # White Pages
│   └── 05_crunchbase/            # Startup data
│
├── 02_ecommerce/                 # E-commerce platforms
│   ├── 00_amazon/                # Amazon products
│   ├── 01_ebay/                  # eBay listings
│   ├── 02_walmart/               # Walmart products
│   ├── 03_shopify_stores/        # Generic Shopify
│   ├── generic_shopify_ant.py    # Shopify scraper
│   └── product_schema_ant.py     # Product extractor
│
├── 03_real_estate/               # Property listings
│   ├── 00_zillow/                # Zillow properties
│   ├── 01_redfin/                # Redfin listings
│   ├── 02_realtor/               # Realtor.com
│   └── 03_apartments/            # Apartments.com
│
├── 04_jobs/                      # Job boards
│   ├── 00_indeed/                # Indeed jobs
│   ├── 01_linkedin_jobs/         # LinkedIn Jobs
│   ├── 02_glassdoor/             # Glassdoor listings
│   ├── 03_monster/               # Monster jobs
│   └── generic_job_ant.py        # Generic job scraper
│
├── 05_news_media/                # News & content
│   ├── 00_news_sites/            # General news
│   ├── 01_rss_feeds/             # RSS aggregation
│   ├── 02_press_releases/        # PR newswires
│   ├── article_ant.py            # Article extractor
│   └── rss_ant.py                # RSS parser
│
├── 06_government_public/         # Public records ✅
│   ├── 00_sec_edgar/             # SEC filings (legal!)
│   ├── 01_court_records/         # Court documents
│   ├── 02_property_records/      # Property tax records
│   └── 03_business_registrations/# Secretary of State
│
└── 07_data_aggregators/          # Reference data
    ├── 00_wikipedia/             # Wikipedia
    ├── 01_imdb/                  # Movies/TV
    └── 02_open_data_portals/     # Government data
```

---

## ⚠️ Legal Status by Platform

### ✅ Generally Safe
| Platform | Notes |
|----------|-------|
| SEC EDGAR | Public domain government data |
| Wikipedia | CC-licensed, API available |
| Open Data Portals | Public records |
| RSS Feeds | Designed for syndication |

### ⚠️ Use Official APIs
| Platform | Recommendation |
|----------|----------------|
| Google Maps | Use Places API |
| Yelp | Use Fusion API |
| Twitter/X | Use official API |
| Crunchbase | Use their API |

### 🚫 High Risk
| Platform | Warning |
|----------|---------|
| LinkedIn | Actively sues scrapers |
| Facebook | Aggressive enforcement |
| Amazon | Strong anti-bot measures |

---

## 🎯 Quick Start

### Business Directory Search
```python
from ant_farms.business_directories.google_maps import GoogleMapsAnt

ant = GoogleMapsAnt()
results = ant.search("coffee shops", "Seattle, WA")
```

### SEC Filings (Legal!)
```python
from ant_farms.government_public.sec_edgar import EDGARAnt

ant = EDGARAnt(email="you@email.com")
company = ant.get_company_info("AAPL")  # Apple
```

### Job Listings
```python
from ant_farms.jobs import GenericJobAnt

ant = GenericJobAnt()
jobs = ant.scrape("https://careers.example.com/jobs")
```

---

## 📊 Implemented Scrapers

| Category | Platform | Status | File |
|----------|----------|--------|------|
| Business | Google Maps | ✅ | `google_maps_ant.py` |
| Business | Yelp | ✅ | `yelp_ant.py` |
| Business | Crunchbase | ✅ | `crunchbase_ant.py` |
| Social | LinkedIn | ✅ | `linkedin_public_ant.py` |
| Real Estate | Zillow | ✅ | `zillow_ant.py` |
| Government | SEC EDGAR | ✅ | `edgar_ant.py` |
| E-commerce | Shopify | ✅ | `generic_shopify_ant.py` |
| Jobs | Generic | ✅ | `generic_job_ant.py` |
| News | Articles | ✅ | `article_ant.py` |
| News | RSS | ✅ | `rss_ant.py` |

---

## 🔗 Related Sections

- **[00_foundations/](../00_foundations/)** - Core concepts & legal
- **[01_ant_anatomy/](../01_ant_anatomy/)** - Base scraper patterns
- **[06_utils/](../06_utils/)** - Shared utilities

---

*Part of the [Leaf Cutter Web Enriching Harvester Ants](../) framework*
