# Yelp Scraper

> **Business Reviews and Local Business Data**

Yelp is a major source for business information, especially reviews and ratings for local businesses.

---

## ⚠️ Important Considerations

### Legal & Ethical
- Yelp has a [Fusion API](https://www.yelp.com/developers/documentation/v3) for legitimate access
- ToS prohibits scraping
- Consider API for production use
- This code is for educational purposes

### Technical Challenges
- Rate limiting (aggressive)
- CAPTCHA after repeated requests
- Some data requires authentication
- Pagination limits

---

## 📊 Data Available

| Field | Availability | Notes |
|-------|--------------|-------|
| Business Name | ✅ Always | |
| Address | ✅ Always | |
| Phone | ✅ Usually | |
| Website | 🔶 Sometimes | Often redirects through Yelp |
| Rating | ✅ Always | 1-5 stars |
| Review Count | ✅ Always | |
| Price Range | 🔶 Usually | $-$$$$ |
| Categories | ✅ Always | |
| Hours | ✅ Usually | |
| Photos | ✅ Usually | |
| Reviews | ✅ Paginated | Full text available |

---

## 🔧 Recommended Approach

### Option 1: Yelp Fusion API (Recommended)
```python
import requests

API_KEY = 'YOUR_API_KEY'
headers = {'Authorization': f'Bearer {API_KEY}'}

# Search businesses
response = requests.get(
    'https://api.yelp.com/v3/businesses/search',
    headers=headers,
    params={'term': 'restaurants', 'location': 'San Francisco'}
)
businesses = response.json()['businesses']

# Get business details
response = requests.get(
    f'https://api.yelp.com/v3/businesses/{business_id}',
    headers=headers
)
```

### Option 2: Direct Scraping (Educational)
See `yelp_ant.py` for implementation.

---

## 📁 Files

| File | Description |
|------|-------------|
| `README.md` | This file |
| `yelp_ant.py` | Scraper implementation |

---

*Part of [02_ant_farms/01_business_directories](../)*
