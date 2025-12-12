# Scraping vs Crawling vs Spidering

> **The Fundamental Terminology of Web Data Extraction**

These three terms are often used interchangeably, but they represent distinct concepts with different purposes, scopes, and implementations. Understanding the differences is essential before building any data extraction system.

---

## Quick Reference

| Term | Primary Purpose | Scope | Depth | Speed Priority |
|------|-----------------|-------|-------|----------------|
| **Scraping** | Extract specific data | Single page or site | Shallow | Fast extraction |
| **Crawling** | Discover & index pages | Multiple sites/web | Broad | Sustainable pace |
| **Spidering** | Map site structure | Single domain | Deep | Complete coverage |

---

## 1. Web Scraping

### Definition

**Web scraping** is the targeted extraction of specific data from web pages. The focus is on *what data you get*, not on discovering new pages.

### Characteristics

- **Goal-oriented**: You know what data you want before you start
- **Structured output**: Extracts data into structured formats (JSON, CSV, database)
- **Page-focused**: Works on known URLs or predictable URL patterns
- **Surgical precision**: Uses selectors (CSS, XPath) to target specific elements

### Example Use Cases

```
Scraping scenarios:
├── Extract all product prices from an e-commerce category page
├── Pull contact information from a business directory listing
├── Gather article headlines and dates from a news site
├── Collect review ratings and text from review pages
└── Extract job posting details from a job board
```

### Technical Approach

```python
# Scraping mindset: "I need THIS data from THIS page"

def scrape_product(url):
    html = fetch(url)
    
    return {
        "name": extract(html, "h1.product-title"),
        "price": extract(html, "span.price"),
        "rating": extract(html, "div.rating"),
        "description": extract(html, "div.description")
    }
```

### Key Distinction

A scraper answers: **"What specific information exists on this page?"**

---

## 2. Web Crawling

### Definition

**Web crawling** is the systematic discovery and traversal of web pages by following links. The focus is on *finding pages*, not necessarily extracting structured data from them.

### Characteristics

- **Discovery-oriented**: Finds new URLs by following links
- **Breadth-first**: Prioritizes covering more ground over deep extraction
- **Index-building**: Often creates an index or catalog of discovered pages
- **Politeness-aware**: Must respect rate limits across many domains
- **Continuous**: Often runs perpetually, revisiting pages for updates

### Example Use Cases

```
Crawling scenarios:
├── Building a search engine index (Google, Bing)
├── Creating a sitemap of all pages on a domain
├── Discovering all outbound links from a site
├── Monitoring the web for new content matching criteria
└── Archiving websites for preservation
```

### Technical Approach

```python
# Crawling mindset: "What pages exist and how are they connected?"

def crawl(start_url, max_pages=1000):
    visited = set()
    queue = [start_url]
    
    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
            
        html = fetch(url)
        visited.add(url)
        
        # The goal is finding more URLs
        new_links = extract_all_links(html)
        queue.extend(new_links)
    
    return visited  # A collection of discovered URLs
```

### Key Distinction

A crawler answers: **"What pages exist and how do they link together?"**

---

## 3. Web Spidering

### Definition

**Web spidering** is the comprehensive mapping of a website's complete structure. The term comes from the metaphor of a spider traversing its web, touching every strand.

### Characteristics

- **Structure-oriented**: Maps the architecture of a site
- **Depth-first or complete**: Aims to find *every* page on a domain
- **Single-domain focus**: Usually confined to one website
- **Hierarchical mapping**: Understands parent-child page relationships
- **Completeness priority**: Would rather be slow than miss pages

### Example Use Cases

```
Spidering scenarios:
├── SEO audits requiring complete site inventory
├── Security scanning of all endpoints
├── Content migration (old site → new site)
├── Competitive analysis of site structure
└── Finding orphan pages (pages with no internal links)
```

### Technical Approach

```python
# Spidering mindset: "Map the COMPLETE structure of this domain"

def spider(domain):
    sitemap = {}
    queue = [f"https://{domain}/"]
    
    while queue:
        url = queue.pop(0)
        if url in sitemap:
            continue
        if not url.startswith(f"https://{domain}"):
            continue  # Stay on this domain only
            
        html = fetch(url)
        links = extract_all_links(html)
        
        sitemap[url] = {
            "title": extract_title(html),
            "links_to": links,
            "depth": calculate_depth(url)
        }
        
        queue.extend(links)
    
    return sitemap  # Complete site structure
```

### Key Distinction

A spider answers: **"What is the complete structure of this website?"**

---

## Comparison Matrix

| Aspect | Scraping | Crawling | Spidering |
|--------|----------|----------|-----------|
| **Primary Output** | Structured data (JSON, CSV) | URL index/database | Site structure map |
| **Typical Scope** | Specific pages | Entire web or multi-site | Single domain |
| **Link Following** | Optional/targeted | Essential | Essential |
| **Domain Boundaries** | Usually single | Often crosses domains | Strictly single |
| **Completeness** | Only needed pages | Best effort | Complete coverage |
| **Data Extraction** | Deep/detailed | Minimal (metadata) | Structural only |
| **Speed vs Coverage** | Favor speed | Balance both | Favor coverage |
| **Typical Duration** | Minutes to hours | Days to forever | Hours to days |

---

## Hybrid Approaches: Real-World Reality

In practice, most data extraction projects combine these techniques:

### Spider → Scrape Pattern

Most common pattern for comprehensive data collection:

```
Phase 1: Spider the site
├── Discover all product category pages
├── Find all product listing pages
└── Collect all individual product URLs

Phase 2: Scrape each URL
├── Extract product details from each page
├── Store structured data
└── Handle pagination
```

### Crawl → Filter → Scrape Pattern

For multi-site or discovery-based projects:

```
Phase 1: Crawl broadly
├── Discover sites matching criteria
├── Build index of relevant domains
└── Classify page types

Phase 2: Filter
├── Identify high-value pages
├── Exclude irrelevant content
└── Prioritize scraping queue

Phase 3: Scrape
├── Deep extraction from filtered pages
├── Structured data output
└── Quality validation
```

---

## Terminology in the Wild

### Industry Usage

Different communities use these terms differently:

| Community | Common Usage |
|-----------|--------------|
| **SEO Industry** | "Spider" and "crawl" used interchangeably for Googlebot-like behavior |
| **Data Science** | "Scraping" is the catch-all term for any web data extraction |
| **Search Engines** | "Crawl" is the standard term for index-building |
| **Security** | "Spider" often means complete site enumeration |
| **Academia** | More precise terminology, distinguishes all three |

### When Someone Says...

| They Say | They Probably Mean |
|----------|-------------------|
| "Scrape that website" | Extract specific data from known pages |
| "Crawl the web for X" | Search broadly to find pages containing X |
| "Spider their site" | Map out everything on that domain |
| "Build a crawler" | Could mean any of the three, ask for clarification |

---

## Choosing Your Approach

### Use Scraping When:

- ✅ You know exactly which pages contain your data
- ✅ URLs follow predictable patterns
- ✅ You need structured data extraction
- ✅ Speed is important
- ✅ The site structure is known and stable

### Use Crawling When:

- ✅ You're building a search index
- ✅ You need to discover content across multiple domains
- ✅ The exact pages aren't known in advance
- ✅ You're monitoring for new content
- ✅ Link relationships matter

### Use Spidering When:

- ✅ You need complete site coverage
- ✅ You're auditing site structure
- ✅ Every page matters, no exceptions
- ✅ You're migrating or archiving a site
- ✅ You need to understand site architecture

---

## The Leaf Cutter Ant Metaphor

In our framework:

| Ant Behavior | Web Equivalent |
|--------------|----------------|
| **Scout ants** find food sources | **Spidering** discovers all pages |
| **Forager ants** cut specific leaves | **Scraping** extracts specific data |
| **Trail ants** create paths | **Crawling** follows and maps links |
| **Harvesting** brings food home | **Data extraction** stores results |

Our "ants" are primarily **scrapers** that operate on known URL patterns, but they can incorporate spidering logic when complete coverage is needed.

---

## Summary

| Term | One-Line Definition |
|------|---------------------|
| **Scraping** | Extracting specific data from web pages |
| **Crawling** | Discovering pages by following links across the web |
| **Spidering** | Completely mapping a single website's structure |

**Remember**: These are conceptual categories, not rigid boundaries. Most real projects blend all three techniques based on the problem at hand.

---

*Next: [02_harvesting_enrichment_pipeline.md](02_harvesting_enrichment_pipeline.md) - Understanding the data flow from raw web content to enriched datasets*
