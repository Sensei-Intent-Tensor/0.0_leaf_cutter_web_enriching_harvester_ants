# Google Maps Scraper

> **Business Data from Google's Local Search**

Google Maps is one of the richest sources for local business information, but also one of the most heavily protected.

---

## ⚠️ Important Considerations

### Legal & Ethical
- Google's ToS explicitly prohibits scraping
- Consider using official Google Places API for production use
- Rate limit aggressively if scraping
- This code is for educational purposes

### Technical Challenges
- Heavy JavaScript rendering required
- Sophisticated bot detection
- Infinite scroll pagination
- Dynamic element loading
- Frequent DOM structure changes

---

## 📊 Data Available

| Field | Availability | Notes |
|-------|--------------|-------|
| Business Name | ✅ Always | |
| Address | ✅ Always | |
| Phone | ✅ Usually | May require click |
| Website | ✅ Usually | |
| Rating | ✅ Usually | 1-5 stars |
| Review Count | ✅ Usually | |
| Hours | 🔶 Sometimes | May require expansion |
| Categories | ✅ Usually | |
| Price Level | 🔶 Sometimes | $-$$$$ |
| Photos | ✅ Usually | URLs available |
| Reviews | 🔶 Pagination | Limited without scrolling |

---

## 🔧 Recommended Approach

### Option 1: Official API (Recommended)
```python
import googlemaps

client = googlemaps.Client(key='YOUR_API_KEY')

# Search for businesses
results = client.places(query='restaurants in San Francisco')

# Get place details
details = client.place(place_id='ChIJN1t_tDeuEmsRUsoyG83frY4')
```

### Option 2: SerpAPI (Paid, but reliable)
```python
from serpapi import GoogleSearch

params = {
    "engine": "google_maps",
    "q": "coffee shops",
    "ll": "@37.7749,-122.4194,15z",
    "api_key": "YOUR_KEY"
}

search = GoogleSearch(params)
results = search.get_dict()
```

### Option 3: Direct Scraping (Educational)
See `google_maps_ant.py` for implementation.

---

## 📁 Files

| File | Description |
|------|-------------|
| `README.md` | This file |
| `google_maps_ant.py` | Scraper implementation |
| `schema.py` | Data model |

---

## 🎯 Search Strategies

### By Query
```
https://www.google.com/maps/search/restaurants+near+san+francisco
```

### By Coordinates
```
https://www.google.com/maps/search/restaurants/@37.7749,-122.4194,15z
```

### By Place ID
```
https://www.google.com/maps/place/?q=place_id:ChIJN1t_tDeuEmsRUsoyG83frY4
```

---

## ⚡ Anti-Detection Tips

1. **Use residential proxies** - Datacenter IPs blocked quickly
2. **Randomize viewport** - Google detects headless patterns
3. **Human-like scrolling** - Smooth, variable speed
4. **Session persistence** - Don't create new browser for each request
5. **Respect rate limits** - 1-2 requests per minute max

---

*Part of [02_ant_farms/01_business_directories](../)*
