# Amazon Scraper

> **E-commerce Product Data**

Amazon is the world's largest e-commerce platform with extensive product data.

---

## ⚠️ Important Considerations

### Legal & Ethical
- Amazon strictly prohibits scraping
- Aggressive anti-bot systems
- Consider Amazon Product Advertising API
- This code is for educational purposes

### Technical Challenges
- Sophisticated bot detection (CAPTCHA)
- Dynamic pricing and content
- Regional variations
- Rate limiting
- Frequent page structure changes

---

## 📊 Data Available

| Field | Availability | Notes |
|-------|--------------|-------|
| Product Title | ✅ Always | |
| Price | ✅ Usually | May vary by location |
| Rating | ✅ Usually | |
| Review Count | ✅ Usually | |
| Images | ✅ Usually | |
| Description | ✅ Usually | |
| Features | ✅ Usually | Bullet points |
| Specifications | 🔶 Sometimes | |
| Seller Info | 🔶 Sometimes | |
| Stock Status | 🔶 Sometimes | |

---

## 🔧 Recommended Alternatives

### Amazon Product Advertising API
```python
# Official API for affiliates
# https://webservices.amazon.com/paapi5/documentation/
```

### Third-Party Services
- Keepa API (price history)
- Rainforest API
- ScraperAPI with Amazon support

---

*Part of [02_ant_farms/02_ecommerce](../)*
