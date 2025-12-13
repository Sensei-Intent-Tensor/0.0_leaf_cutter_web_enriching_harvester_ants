# 02_ecommerce

> **E-commerce & Marketplace Scrapers**

Scrapers for online stores, marketplaces, and product data extraction.

---

## 🛒 Available Ants

| Ant | Site | Data Extracted | Difficulty |
|-----|------|----------------|------------|
| [amazon_product_ant.py](amazon_product_ant.py) | Amazon | Products, prices, reviews | Hard |
| [generic_shopify_ant.py](generic_shopify_ant.py) | Any Shopify store | Products, variants | Medium |
| [product_schema_ant.py](product_schema_ant.py) | Any site with Schema.org | Structured product data | Easy |

---

## 🎯 Common Use Cases

```
E-commerce Scraping Scenarios:
├── Price Monitoring
│   ├── Track competitor prices
│   ├── Monitor own listings
│   └── Price history analysis
│
├── Product Research
│   ├── Catalog extraction
│   ├── Feature comparison
│   └── Market analysis
│
├── Review Analysis
│   ├── Sentiment analysis
│   ├── Competitive intelligence
│   └── Product feedback
│
└── Inventory Monitoring
    ├── Stock availability
    ├── New product alerts
    └── Category changes
```

---

## ⚠️ Important Considerations

### Amazon Specifics

- **robots.txt**: Disallows most scraping
- **ToS**: Explicitly prohibits scraping
- **Detection**: Aggressive anti-bot measures
- **Recommendation**: Use official Product Advertising API when possible

### Shopify Stores

- **robots.txt**: Usually allows /products
- **Detection**: Varies by store configuration
- **Tip**: Many stores expose `/products.json` endpoint

### General E-commerce Tips

```python
# 1. Use product schema when available
schema = soup.find('script', type='application/ld+json')
if schema:
    data = json.loads(schema.string)
    # Structured data!

# 2. Check for API endpoints
# /api/products, /products.json, etc.

# 3. Handle variants
# Products often have size/color variants with different URLs
```

---

## 📊 Rate Limit Guidelines

| Site | Recommended Rate | Notes |
|------|------------------|-------|
| Amazon | 1 req/5 sec | High risk of blocks |
| eBay | 1 req/2 sec | Use API when possible |
| Shopify stores | 1 req/1 sec | Varies by store |
| Small stores | 1 req/3 sec | Be extra cautious |

---

## 🔧 Example Usage

### Price Monitoring

```python
from ecommerce import AmazonProductAnt

ant = AmazonProductAnt()

# Monitor a product
result = ant.scrape('https://amazon.com/dp/B08N5WRWNW')

if result.success:
    print(f"Current price: ${result.data['price']}")
    print(f"In stock: {result.data['in_stock']}")
```

### Catalog Extraction (Shopify)

```python
from ecommerce import ShopifyAnt

ant = ShopifyAnt(store_url='https://example-store.com')

# Get all products
products = ant.scrape_catalog()

print(f"Found {len(products)} products")
```

---

*Part of [02_ant_farms](../) - Site-specific scraper collections*
