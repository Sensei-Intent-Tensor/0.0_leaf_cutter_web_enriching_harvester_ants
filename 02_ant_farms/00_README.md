# 02_ant_farms

> **Organized Collections of Site-Specific Scrapers**

Ant farms are organized colonies of scrapers designed for specific website categories. Each farm contains ready-to-use ants for common sites in that category.

---

## 🏗️ Farm Structure

```
02_ant_farms/
│
├── 00_social/              Social media & community platforms
│   ├── twitter_ant.py
│   ├── linkedin_ant.py
│   └── reddit_ant.py
│
├── 01_business_directories/ Business listings & directories
│   ├── yelp_ant.py
│   ├── yellowpages_ant.py
│   └── google_maps_ant.py
│
├── 02_ecommerce/           Online stores & marketplaces
│   ├── amazon_ant.py
│   ├── ebay_ant.py
│   └── shopify_ant.py
│
├── 03_real_estate/         Property listings
│   ├── zillow_ant.py
│   ├── realtor_ant.py
│   └── redfin_ant.py
│
├── 04_jobs/                Job boards & career sites
│   ├── indeed_ant.py
│   ├── linkedin_jobs_ant.py
│   └── glassdoor_ant.py
│
├── 05_news_media/          News sites & publications
│   ├── news_generic_ant.py
│   ├── rss_ant.py
│   └── article_ant.py
│
├── 06_government_public/   Government & public data
│   ├── sec_ant.py
│   ├── patents_ant.py
│   └── court_records_ant.py
│
└── 07_data_aggregators/    Data aggregation sites
    ├── crunchbase_ant.py
    ├── similarweb_ant.py
    └── statista_ant.py
```

---

## 📚 Farm Categories

| Farm | Description | Difficulty | Key Challenges |
|------|-------------|------------|----------------|
| [00_social](00_social/) | Social media platforms | Hard | Auth, rate limits, ToS |
| [01_business_directories](01_business_directories/) | Business listings | Medium | Pagination, geo-targeting |
| [02_ecommerce](02_ecommerce/) | Online stores | Medium-Hard | JS rendering, anti-bot |
| [03_real_estate](03_real_estate/) | Property listings | Medium | Dynamic content, maps |
| [04_jobs](04_jobs/) | Job boards | Medium | Pagination, deduplication |
| [05_news_media](05_news_media/) | News and articles | Easy-Medium | Paywalls, structure varies |
| [06_government_public](06_government_public/) | Public records | Easy-Medium | Old systems, PDFs |
| [07_data_aggregators](07_data_aggregators/) | Data platforms | Hard | Paywalls, authentication |

---

## 🎯 Using Ant Farms

### Quick Start

```python
# Import a specific ant
from ant_farms.ecommerce import AmazonProductAnt

# Initialize and use
ant = AmazonProductAnt()
result = ant.scrape('https://amazon.com/dp/B08N5WRWNW')

print(result.data)
# {'title': 'Product Name', 'price': 99.99, 'rating': 4.5, ...}
```

### Customizing Farm Ants

```python
from ant_farms.ecommerce import AmazonProductAnt

class MyAmazonAnt(AmazonProductAnt):
    # Add custom fields
    additional_selectors = {
        'brand': '#bylineInfo',
        'delivery': '#delivery-message',
    }
    
    # Override extraction
    def extract(self, soup):
        data = super().extract(soup)
        data['custom_field'] = self.safe_extract('#my-field', soup)
        return data
```

---

## ⚠️ Important Notes

### Legal & Ethical Considerations

Each farm README includes:
- robots.txt status for target sites
- ToS implications
- Rate limit recommendations
- Known legal precedents

**Always review before scraping!**

### Site Changes

Websites change frequently. Ants may need updating:

```python
# Check if ant is working
ant = AmazonProductAnt()
result = ant.test()

if not result.success:
    print(f"Ant needs updating: {result.error}")
```

### Contributing

When adding new ants:

1. Follow the naming convention: `{site}_ant.py`
2. Include comprehensive selectors
3. Add tests for common URLs
4. Document any authentication requirements
5. Note rate limit recommendations

---

## 🔗 Related Sections

- [01_ant_anatomy/](../01_ant_anatomy/) - Base ant classes and patterns
- [03_enrichment_pipelines/](../03_enrichment_pipelines/) - Data processing
- [06_utils/](../06_utils/) - Shared utilities

---

*Part of the [Leaf Cutter Web Enriching Harvester Ants](../) framework*
