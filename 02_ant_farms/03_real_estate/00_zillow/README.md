# Zillow Scraper

> **Real Estate Listings and Property Data**

Zillow is the leading U.S. real estate marketplace with extensive property data.

---

## ⚠️ Important Considerations

### Legal & Ethical
- Zillow provides APIs for partners
- ToS prohibits scraping
- Property data has specific legal considerations
- For production, consider Zillow API or ATTOM Data

### Technical Challenges
- Heavy JavaScript rendering
- Complex pagination
- Frequent structure changes
- Regional restrictions

---

## 📊 Data Available

| Field | Availability | Notes |
|-------|--------------|-------|
| Property Address | ✅ Always | |
| Price | ✅ Usually | List price or Zestimate |
| Beds/Baths | ✅ Usually | |
| Square Footage | ✅ Usually | |
| Lot Size | 🔶 Sometimes | |
| Year Built | 🔶 Sometimes | |
| Property Type | ✅ Usually | |
| Zestimate | ✅ Usually | Zillow's estimate |
| Photos | ✅ Usually | |
| Tax History | 🔶 Limited | |
| Price History | 🔶 Limited | |

---

## 🔧 Recommended Approach

### Option 1: Zillow API (For Partners)
Contact Zillow for API access for legitimate business use.

### Option 2: Alternative Data Sources
- ATTOM Data
- CoreLogic
- Public records
- MLS feeds (for licensed agents)

### Option 3: Direct Scraping (Educational)
See `zillow_ant.py` for implementation.

---

*Part of [02_ant_farms/03_real_estate](../)*
