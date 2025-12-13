# 06_government_public

> **Government & Public Records Scrapers**

Scrapers for public government data, court records, and official documents.

---

## 📜 Categories

### Generally Scrapable
- SEC filings (EDGAR)
- Patent databases (USPTO)
- Court records (PACER - paid)
- Census data
- Open data portals

### Restricted
- Some state DMV records
- Sealed court records
- National security data

---

## 🏛️ Common Sources

| Source | Type | Access |
|--------|------|--------|
| SEC EDGAR | Financial filings | Free API |
| USPTO | Patents | Free API |
| Congress.gov | Legislation | Free |
| Data.gov | Open data | Free |
| State Open Data | Varies | Free |

---

## 💡 Tips

```python
# 1. Many government sites have APIs
# SEC: https://www.sec.gov/developer
# USPTO: https://developer.uspto.gov/

# 2. Use bulk download when available
# Often more efficient than scraping

# 3. Be extra patient
# Government sites are often slow
```

---

*Part of [02_ant_farms](../) - Site-specific scraper collections*
