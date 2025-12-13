# 03_real_estate

> **Real Estate & Property Listing Scrapers**

Scrapers for property listings, rental data, and real estate information.

---

## 🏠 Common Data Fields

```python
PROPERTY_SCHEMA = {
    'address': str,
    'city': str,
    'state': str,
    'zip': str,
    'price': float,
    'bedrooms': int,
    'bathrooms': float,
    'sqft': int,
    'lot_size': float,
    'year_built': int,
    'property_type': str,  # 'house', 'condo', 'apartment'
    'listing_type': str,   # 'sale', 'rent'
    'images': list,
    'description': str,
}
```

---

## ⚠️ Considerations

### Major Platforms

| Site | ToS | Notes |
|------|-----|-------|
| Zillow | Restrictive | Has API (limited) |
| Realtor.com | Restrictive | MLS data protected |
| Redfin | Restrictive | Aggressive blocking |
| Apartments.com | Moderate | High rate limits |

### Legal Notes

- MLS data is often copyrighted
- Property records are public (county assessor)
- Listing photos are copyrighted

---

*Part of [02_ant_farms](../) - Site-specific scraper collections*
