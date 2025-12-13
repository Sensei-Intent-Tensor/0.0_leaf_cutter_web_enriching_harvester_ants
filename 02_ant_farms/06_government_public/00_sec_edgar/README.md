# SEC EDGAR Scraper

> **Public Company Filings and Financial Data**

SEC EDGAR is the U.S. Securities and Exchange Commission's public database of company filings. This is **legally scrapeable** public government data.

---

## ✅ Legal Status

### Good News!
- SEC EDGAR data is **public domain**
- No ToS restrictions on access
- SEC provides APIs and bulk data
- Completely legal to scrape

### Best Practices
- Use SEC's EDGAR APIs when possible
- Respect rate limits (10 requests/second max)
- Include your email in User-Agent
- Don't overload their servers

---

## 📊 Data Available

| Filing Type | Description |
|-------------|-------------|
| 10-K | Annual report |
| 10-Q | Quarterly report |
| 8-K | Current report (material events) |
| DEF 14A | Proxy statement |
| 4 | Insider trading |
| 13F | Institutional holdings |
| S-1 | IPO registration |

---

## 🔧 Official Resources

### SEC EDGAR APIs
```python
# Company search
https://efts.sec.gov/LATEST/search-index?q=COMPANY&dateRange=custom

# Company filings
https://data.sec.gov/submissions/CIK{cik}.json

# Full-text search
https://efts.sec.gov/LATEST/search-index?q=QUERY
```

### Bulk Data Downloads
- https://www.sec.gov/Archives/edgar/full-index/
- XBRL data: https://www.sec.gov/dera/data

---

## 📁 Files

| File | Description |
|------|-------------|
| `README.md` | This file |
| `edgar_ant.py` | EDGAR scraper implementation |

---

## 📋 Rate Limits

SEC requests you:
- Limit to **10 requests per second**
- Include contact email in User-Agent
- Use bulk downloads for large data needs

---

*Part of [02_ant_farms/06_government_public](../)*
