# 00_terminology

> **The Language of Web Data Extraction**

Before writing a single line of scraping code, you need to speak the language. This section defines every term, concept, and approach you'll encounter in the world of web data extraction.

---

## 📚 Documents in This Section

| # | Document | Lines | Description |
|---|----------|-------|-------------|
| 01 | [Scraping vs Crawling vs Spidering](01_scraping_vs_crawling_vs_spidering.md) | 319 | The three fundamental approaches and when to use each |
| 02 | [Harvesting & Enrichment Pipeline](02_harvesting_enrichment_pipeline.md) | 491 | The 5-stage journey from raw web data to valuable datasets |
| 03 | [Bots, Agents, Spiders Glossary](03_bots_agents_spiders_glossary.md) | 1,135 | 100+ terms defined across 10 categories |
| 04 | [Data Extraction Taxonomy](04_data_extraction_taxonomy.md) | 736 | Complete classification framework for extraction approaches |

**Total: 2,681 lines of foundational knowledge**

---

## 🎯 Reading Order

**New to scraping?** Read in order:
1. Start with **Scraping vs Crawling vs Spidering** to understand the basics
2. Read **Harvesting & Enrichment Pipeline** to understand the data flow
3. Reference the **Glossary** as you encounter new terms
4. Use the **Taxonomy** to choose your approach

**Experienced scraper?** Jump to what you need:
- Need terminology? → Glossary
- Choosing an approach? → Taxonomy
- Building a pipeline? → Harvesting & Enrichment

---

## 🔑 Key Takeaways

### From Scraping vs Crawling vs Spidering
- **Scraping** = extracting specific data from pages
- **Crawling** = discovering pages by following links
- **Spidering** = mapping complete site structure
- Most real projects combine all three

### From Harvesting & Enrichment Pipeline
- Raw data goes through 5 stages: Source → Harvest → Clean → Enrich → Output
- "Harvest wide, filter later"
- Enrichment adds value through geocoding, cross-referencing, and derived fields

### From the Glossary
- HTTP status codes tell you what happened
- CSS selectors and XPath are your extraction tools
- Understanding anti-scraping helps you work around it
- Legal and ethical considerations matter

### From the Taxonomy
- Choose **static** extraction for speed, **dynamic** for JS-heavy sites
- Scale dictates architecture: single page → site-wide → web-scale
- Match your update pattern to your use case

---

## 🐜 The Leaf Cutter Ant Framework

Throughout these documents, we use the leaf cutter ant colony as a metaphor:

| Ant Behavior | Data Extraction Equivalent |
|--------------|---------------------------|
| Scout ants finding food | Spidering/URL discovery |
| Forager ants cutting leaves | Scraping/data extraction |
| Trail ants making paths | Crawling/link following |
| Workers processing leaves | Data cleaning |
| Fungus garden | Enrichment pipeline |
| Food storage | Output/database |

---

## ➡️ Next Section

Once you understand the terminology, move on to:

**[01_technical_operations/](../01_technical_operations/)** - How the web actually works for scrapers (HTTP, CORS, cookies, headers, JavaScript rendering, rate limiting, proxies)

---

*Part of [00_foundations](../) - The complete web scraping knowledge base*
