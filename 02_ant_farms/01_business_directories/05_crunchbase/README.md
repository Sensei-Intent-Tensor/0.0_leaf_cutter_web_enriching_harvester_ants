# Crunchbase Scraper

> **Company and Startup Intelligence**

Crunchbase is the premier database for company information, funding data, and startup intelligence.

---

## ⚠️ Important Considerations

### Legal & Ethical
- Crunchbase offers paid API access
- Heavy anti-scraping measures
- Most valuable data behind paywall
- This code is for educational purposes

### Technical Challenges
- GraphQL API with authentication
- Heavy JavaScript rendering
- Aggressive rate limiting
- Data requires paid subscription

---

## 📊 Data Available (Free Tier)

| Field | Availability | Notes |
|-------|--------------|-------|
| Company Name | ✅ Always | |
| Description | ✅ Usually | Short description |
| Website | ✅ Usually | |
| Founded Date | ✅ Usually | |
| Location | ✅ Usually | HQ location |
| Employee Count | 🔶 Sometimes | Range estimate |
| Industry | ✅ Usually | Categories |
| Funding Total | 🔶 Limited | May need subscription |
| Investors | 🔶 Limited | May need subscription |

---

## 🔧 Recommended Approach

### Option 1: Crunchbase API (Recommended)
```python
import requests

API_KEY = 'YOUR_API_KEY'

response = requests.get(
    'https://api.crunchbase.com/api/v4/entities/organizations/facebook',
    params={'user_key': API_KEY}
)
company = response.json()
```

### Option 2: Direct Scraping (Educational)
See `crunchbase_ant.py` for implementation.

---

*Part of [02_ant_farms/01_business_directories](../)*
