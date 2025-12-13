# 01_business_directories

> **Business Listing & Directory Scrapers**

Scrapers for extracting business information from directories and maps.

---

## 📍 Available Ants

| Ant | Site | Data Extracted |
|-----|------|----------------|
| [generic_directory_ant.py](generic_directory_ant.py) | Any LocalBusiness schema | Business details |

---

## 🎯 Common Use Cases

- Lead generation
- Market research
- Competitor analysis
- Local SEO monitoring
- Data enrichment

---

## ⚠️ Considerations

### Major Platforms

| Site | Status | Recommendation |
|------|--------|----------------|
| Google Maps | Prohibits scraping | Use Places API |
| Yelp | Restrictive ToS | Use Fusion API |
| Yellow Pages | Generally permissive | Check robots.txt |
| Local directories | Varies | Check per-site |

### Best Practices

```python
# 1. Use Schema.org LocalBusiness when available
schema = soup.find('script', type='application/ld+json')

# 2. Respect rate limits heavily
# Business directories are often small operations

# 3. Consider APIs
# Yelp, Google, Foursquare all have APIs
```

---

*Part of [02_ant_farms](../) - Site-specific scraper collections*
