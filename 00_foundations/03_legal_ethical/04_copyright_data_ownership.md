# Copyright & Data Ownership

> **Who Owns What You Scrape?**

Copyright law determines what you can do with scraped content. Understanding these rules is essential for staying legal.

---

## Copyright Basics

### What Is Copyrighted?

Copyright automatically protects **original works of authorship**:

| Protected | NOT Protected |
|-----------|---------------|
| Text/articles | Facts |
| Images | Ideas |
| Videos | Data |
| Code | Common phrases |
| Music | Government works (usually) |
| Creative compilations | Functional elements |

### Key Principle

```
FACTS ≠ COPYRIGHTABLE
EXPRESSION OF FACTS = COPYRIGHTABLE
```

**Example:**
- ❌ "The price is $99.99" (fact) - Not copyrightable
- ✅ "This stunning deal at an unbelievable $99.99!" (expression) - Copyrightable

---

## The Data vs. Expression Problem

### What You Can Scrape

| Data Type | Copyright Status | Example |
|-----------|------------------|---------|
| Raw facts | Not copyrightable | Prices, dates, addresses |
| Statistics | Not copyrightable | Stock prices, weather data |
| Public records | Usually not protected | Court filings, property records |
| Contact info | Facts, not protected | Phone numbers, emails |
| Creative writing | COPYRIGHTED | Articles, descriptions |
| Images | COPYRIGHTED | Photos, graphics |
| Reviews | COPYRIGHTED | User-generated content |

### Database Rights

Some jurisdictions recognize database protection:

**United States:**
- No separate database right
- But: creative selection/arrangement can be protected
- Feist v. Rural (1991): Facts aren't copyrightable

**European Union:**
- Sui generis database right
- Protects "substantial investment" in obtaining, verifying, presenting data
- Lasts 15 years, renewable with updates
- Applies to extraction of substantial portions

---

## Fair Use (U.S.)

### Four Factors

Courts consider:

1. **Purpose and character of use**
   - Commercial vs. non-commercial
   - Transformative use favored

2. **Nature of copyrighted work**
   - Factual works have less protection
   - Published works have less protection

3. **Amount used**
   - Both quantity and quality
   - Using the "heart" weighs against fair use

4. **Market effect**
   - Does it substitute for the original?
   - Does it harm potential markets?

### Fair Use Examples in Scraping

| Scenario | Likely Fair Use? |
|----------|------------------|
| Scraping for search index | ✅ Yes (transformative) |
| Academic text analysis | ✅ Often yes |
| Price comparison | ✅ Usually (facts) |
| Reprinting full articles | ❌ No |
| Thumbnail images | ✅ Often yes |
| Copying for competitor site | ❌ No |

### Not Fair Use

```python
NOT_FAIR_USE = [
    "Republishing full articles",
    "Creating a mirror site",
    "Selling scraped creative content",
    "Replacing need for original",
    "Scraping to train commercial AI (contested)",
]
```

---

## Specific Content Types

### Text Content

```python
text_rules = {
    # Safe
    "facts": "Prices, dates, names, addresses",
    "short_quotes": "With attribution, for commentary",
    "titles": "Generally not copyrightable",
    
    # Risky
    "full_articles": "Copyright infringement",
    "product_descriptions": "Often copyrighted",
    "reviews": "User owns copyright",
    
    # Transform to be safer
    "summarization": "May be fair use if truly transformed",
    "analysis": "Extracting facts/insights usually OK",
}
```

### Images

```python
image_rules = {
    # Generally NOT OK
    "full_resolution": "Copyright infringement",
    "rehosting": "Infringement unless licensed",
    "commercial_use": "Requires license",
    
    # May be OK
    "thumbnails": "Fair use for search/index",
    "metadata_only": "Facts about image OK",
    "linking": "Generally OK (not copying)",
    
    # Safe
    "creative_commons": "Follow license terms",
    "public_domain": "Free to use",
}
```

### User-Generated Content

Users own copyright in their content:
- Reviews they write
- Comments they post
- Photos they upload

The platform has a license, but you may not.

---

## Practical Guidelines

### Scraping for Facts

```python
# SAFE: Extract facts only
product_data = {
    "name": "Widget X",       # Factual
    "price": 99.99,           # Factual
    "sku": "WX-12345",        # Factual
    "in_stock": True,         # Factual
}

# RISKY: Copying expression
product_data = {
    "description": "This revolutionary widget transforms...",  # Copyrighted
    "marketing_copy": "Experience the difference...",          # Copyrighted
}
```

### Transformative Use

```python
# Original: Full article text
# Transformation: Extract entities, sentiment, topics

from transformations import extract_entities, analyze_sentiment

article = scrape_article(url)

# Transform into facts
transformed = {
    "entities": extract_entities(article),      # Facts derived
    "sentiment": analyze_sentiment(article),    # Analysis
    "topics": classify_topics(article),         # Classification
    "word_count": len(article.split()),         # Statistic
    # NOT: "full_text": article                 # Would be copying
}
```

### Attribution

Always attribute sources:
```python
data_record = {
    "value": scraped_value,
    "source_url": "https://original-source.com/page",
    "source_name": "Original Site",
    "scraped_date": "2024-01-15",
}
```

---

## Safe Practices

### What You CAN Generally Do

✅ Extract facts (prices, dates, statistics)
✅ Create indexes and search tools
✅ Analyze and derive insights
✅ Quote briefly with attribution
✅ Transform content (summarize, classify)
✅ Link back to original sources

### What You Should AVOID

❌ Republishing full articles
❌ Rehosting images without license
❌ Creating substitute/mirror sites
❌ Selling scraped creative content
❌ Removing attribution/watermarks
❌ Claiming scraped content as your own

---

## Special Cases

### News Aggregation

```
Generally OK:
- Headlines + brief snippets
- Links to original
- Transformative selection

Not OK:
- Full article reproduction
- Eliminating need to visit original
```

### Research & Academia

```
Often Protected:
- Text mining for research (some jurisdictions)
- Non-commercial analysis
- Criticism and commentary

Still Consider:
- Institutional guidelines
- IRB approval
- Data retention limits
```

### APIs and Licensed Data

```
API Terms Matter:
- May restrict use beyond TOS
- Often prohibit redistribution
- May limit commercial use
- Read the license!
```

---

## International Considerations

### EU Database Directive

- 15-year protection for databases
- Covers "substantial investment" in data
- Prohibits extraction of substantial parts
- Can affect scraping strategy

### UK Copyright

- Similar to US with differences
- No comprehensive fair use (fair dealing instead)
- Database right applies

### Other Jurisdictions

- Canada: Fair dealing categories
- Australia: Fair dealing + some exceptions
- Japan: Expanded text/data mining exception

---

## Summary

| Content Type | Copyright? | Can Scrape? | Can Republish? |
|--------------|------------|-------------|----------------|
| Facts/Data | No | ✅ Yes | ✅ Yes |
| Prices/Stats | No | ✅ Yes | ✅ Yes |
| Article text | Yes | ⚠️ Careful | ❌ No |
| Images | Yes | ⚠️ Careful | ❌ License needed |
| User reviews | Yes | ⚠️ Careful | ❌ No |
| Creative descriptions | Yes | ⚠️ Careful | ❌ No |

### Key Takeaways

1. **Facts are free** - Copyright doesn't protect facts
2. **Expression is protected** - The way facts are presented can be
3. **Transform when possible** - Analysis > copying
4. **Attribute sources** - Good practice regardless
5. **When in doubt** - Extract facts, not expression

---

*Next: [05_ethical_scraping_guidelines.md](05_ethical_scraping_guidelines.md) - Being a good citizen of the web*
