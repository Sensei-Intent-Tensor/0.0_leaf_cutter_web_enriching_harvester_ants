# 00_foundations

> **The Complete Web Scraping Knowledge Base**

Welcome to the foundations of the Leaf Cutter Web Enriching Harvester Ants framework. This wiki contains everything you need to know about web scraping—from fundamental concepts to advanced techniques.

---

## 📊 Wiki Statistics

```
┌─────────────────────────────────────────────────────────────────┐
│                    FOUNDATIONS WIKI                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   📁 48 Documents                                               │
│   📝 20,000+ Lines of Documentation                             │
│   📚 5 Comprehensive Sections                                   │
│                                                                 │
│   ✅ All Sections Complete                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📚 Sections Overview

### [00_terminology/](00_terminology/)
**Core Concepts & Vocabulary**

| Document | Description |
|----------|-------------|
| 01_scraping_vs_crawling | Definitions and distinctions |
| 02_pipeline_architecture | Data flow from request to storage |
| 03_terminology_glossary | Comprehensive A-Z glossary |
| 04_data_extraction_taxonomy | Classification of extraction methods |

---

### [01_technical_operations/](01_technical_operations/)
**How the Web Works**

| Document | Description |
|----------|-------------|
| 01_http_requests_anatomy | Request/response cycle explained |
| 02_cors_explained | Cross-origin requests (and why scrapers ignore them) |
| 03_cookies_sessions_state | State management techniques |
| 04_headers_user_agents | Essential headers for stealth |
| 05_javascript_rendering_spa | Handling JavaScript-heavy sites |
| 06_rate_limiting_throttling | Polite scraping techniques |
| 07_proxies_rotation_ips | IP management strategies |

---

### [02_anti_scraping_tech/](02_anti_scraping_tech/)
**Know Your Enemy**

| Document | Description |
|----------|-------------|
| 01_why_anti_scraping_exists | Understanding the business motivation |
| 02_captcha_systems | reCAPTCHA, hCaptcha, and solutions |
| 03_bot_detection_fingerprinting | How sites identify bots |
| 04_honeypots_traps | Hidden snares to avoid |
| 05_cloudflare_akamai_etc | Major WAF providers |
| 06_login_walls_auth_gates | Authentication strategies |
| 07_dynamic_content_obfuscation | Anti-scraping code techniques |

---

### [03_legal_ethical/](03_legal_ethical/)
**Scraping Responsibly**

| Document | Description |
|----------|-------------|
| 01_robots_txt_guide | The robots exclusion protocol |
| 02_terms_of_service | Legal implications of ToS |
| 03_data_privacy_laws | GDPR, CCPA, and compliance |
| 04_ethical_guidelines | Beyond legal requirements |
| 05_rate_limiting_respect | Being a good web citizen |

---

### [04_tools_ecosystem/](04_tools_ecosystem/)
**The Scraper's Toolbox**

| Document | Description |
|----------|-------------|
| 01_python_scraping_stack | Complete Python toolkit |
| 02_browser_automation_compared | Playwright vs Selenium vs Puppeteer |
| 03_parsing_libraries_guide | BeautifulSoup, lxml, parsel |
| 04_proxy_services_overview | Commercial proxy providers |
| 05_data_storage_options | Files, databases, cloud storage |

---

## 🎯 Learning Paths

### Path 1: Complete Beginner
```
1. 00_terminology/01_scraping_vs_crawling
2. 00_terminology/03_terminology_glossary
3. 01_technical_operations/01_http_requests_anatomy
4. 04_tools_ecosystem/01_python_scraping_stack
5. 03_legal_ethical/04_ethical_guidelines
```

### Path 2: JavaScript Sites
```
1. 01_technical_operations/05_javascript_rendering_spa
2. 04_tools_ecosystem/02_browser_automation_compared
3. 02_anti_scraping_tech/03_bot_detection_fingerprinting
4. 02_anti_scraping_tech/05_cloudflare_akamai_etc
```

### Path 3: Enterprise Scale
```
1. 00_terminology/02_pipeline_architecture
2. 01_technical_operations/06_rate_limiting_throttling
3. 01_technical_operations/07_proxies_rotation_ips
4. 04_tools_ecosystem/04_proxy_services_overview
5. 04_tools_ecosystem/05_data_storage_options
```

### Path 4: Legal & Compliance
```
1. 03_legal_ethical/01_robots_txt_guide
2. 03_legal_ethical/02_terms_of_service
3. 03_legal_ethical/03_data_privacy_laws
4. 02_anti_scraping_tech/01_why_anti_scraping_exists
```

---

## 🛠️ Quick Reference

### Essential Code Patterns

```python
# Basic request with headers
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9',
}

response = requests.get(url, headers=headers)
```

```python
# Parse HTML
from bs4 import BeautifulSoup

soup = BeautifulSoup(response.text, 'lxml')
titles = soup.select('h2.title')
```

```python
# Handle JavaScript sites
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url)
    page.wait_for_selector('.content')
    html = page.content()
    browser.close()
```

```python
# Rate limiting
import time
import random

for url in urls:
    response = requests.get(url)
    time.sleep(random.uniform(1, 3))  # Random delay
```

### Decision Quick Guide

| Situation | Solution |
|-----------|----------|
| Simple HTML page | requests + BeautifulSoup |
| JavaScript-rendered | Playwright |
| Cloudflare protected | cloudscraper |
| Need many IPs | Residential proxies |
| Large scale | Scrapy framework |
| Rate limited | Slow down + proxy rotation |
| CAPTCHA blocked | Solving service |

---

## 📈 Project Structure

```
00_foundations/
├── 00_README.md                    ← You are here
├── 00_terminology/
│   ├── 00_README.md
│   ├── 01_scraping_vs_crawling.md
│   ├── 02_pipeline_architecture.md
│   ├── 03_terminology_glossary.md
│   └── 04_data_extraction_taxonomy.md
├── 01_technical_operations/
│   ├── 00_README.md
│   ├── 01_http_requests_anatomy.md
│   ├── 02_cors_explained.md
│   ├── 03_cookies_sessions_state.md
│   ├── 04_headers_user_agents.md
│   ├── 05_javascript_rendering_spa.md
│   ├── 06_rate_limiting_throttling.md
│   └── 07_proxies_rotation_ips.md
├── 02_anti_scraping_tech/
│   ├── 00_README.md
│   ├── 01_why_anti_scraping_exists.md
│   ├── 02_captcha_systems.md
│   ├── 03_bot_detection_fingerprinting.md
│   ├── 04_honeypots_traps.md
│   ├── 05_cloudflare_akamai_etc.md
│   ├── 06_login_walls_auth_gates.md
│   └── 07_dynamic_content_obfuscation.md
├── 03_legal_ethical/
│   ├── 00_README.md
│   ├── 01_robots_txt_guide.md
│   ├── 02_terms_of_service.md
│   ├── 03_data_privacy_laws.md
│   ├── 04_ethical_guidelines.md
│   └── 05_rate_limiting_respect.md
└── 04_tools_ecosystem/
    ├── 00_README.md
    ├── 01_python_scraping_stack.md
    ├── 02_browser_automation_compared.md
    ├── 03_parsing_libraries_guide.md
    ├── 04_proxy_services_overview.md
    └── 05_data_storage_options.md
```

---

## 🔗 Related Framework Sections

This foundations wiki is part of the larger Leaf Cutter framework:

- **[01_harvester_patterns/](../01_harvester_patterns/)** - Reusable scraping patterns
- **[02_colony_architecture/](../02_colony_architecture/)** - System design
- **[03_ant_types/](../03_ant_types/)** - Specialized scrapers
- **[04_food_processing/](../04_food_processing/)** - Data transformation
- **[05_trail_systems/](../05_trail_systems/)** - Communication protocols

---

## 📝 Contributing

This wiki grows with the framework. To add or update documentation:

1. Follow the existing naming conventions
2. Use consistent markdown formatting
3. Include practical code examples
4. Update section README when adding files
5. Cross-reference related documents

---

*Part of the [Leaf Cutter Web Enriching Harvester Ants](../) framework*
*A project of [Auto-Workspace-AI](https://auto-workspace-ai.com) applying Intent Tensor Theory to business automation*
