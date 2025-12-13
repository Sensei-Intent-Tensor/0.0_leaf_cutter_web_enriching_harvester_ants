# 03_legal_ethical

> **Scraping Responsibly: Laws, Ethics, and Citizenship**

Web scraping operates in a complex landscape of laws, norms, and ethical considerations. This section helps you navigate these waters responsibly.

---

## 📚 Documents in This Section

| # | Document | Description |
|---|----------|-------------|
| 01 | [robots.txt Guide](01_robots_txt_guide.md) | Understanding and respecting the robots exclusion protocol |
| 02 | [Terms of Service](02_terms_of_service.md) | Legal implications of website ToS |
| 03 | [Data Privacy Laws](03_data_privacy_laws.md) | GDPR, CCPA, and global privacy regulations |
| 04 | [Ethical Guidelines](04_ethical_guidelines.md) | Principles beyond legal compliance |
| 05 | [Rate Limiting Respect](05_rate_limiting_respect.md) | Being a good citizen of the web |

---

## 🎯 Key Questions This Section Answers

**Legal Questions:**
- Is scraping legal?
- What do Terms of Service mean for me?
- How do privacy laws affect scraping?

**Ethical Questions:**
- Is this the right thing to do?
- Who could be harmed?
- Am I being a good web citizen?

**Practical Questions:**
- How do I read robots.txt?
- What rate should I scrape at?
- How do I handle personal data?

---

## 🔑 Core Principles

### Legal Compliance

- ✅ Read robots.txt before scraping
- ✅ Understand relevant ToS
- ✅ Know applicable privacy laws
- ✅ Document your compliance efforts

### Ethical Standards

**The Golden Rule:** "Scrape unto others as you would have them scrape unto you"

### Technical Respect

- Rate limit conservatively
- Identify your bot
- Honor Crawl-delay directives
- Stop if causing problems

---

## 📊 Quick Reference

### Risk Assessment

| Factor | Lower Risk | Higher Risk |
|--------|------------|-------------|
| **Data** | Public, non-personal | Personal, behind login |
| **ToS** | Silent or permissive | Explicitly prohibits |
| **robots.txt** | Allows or absent | Disallows |
| **Use** | Research, personal | Commercial, competitive |

### Rate Limiting Defaults

| Site Type | Recommended Rate |
|-----------|------------------|
| Unknown | 1 request / 5 seconds |
| Small site | 1 request / 10 seconds |
| Medium site | 1 request / 2 seconds |
| Large site | 2-5 requests / second |

---

## 🔗 Related Sections

- [00_terminology/](../00_terminology/) - Legal terms defined
- [01_technical_operations/](../01_technical_operations/) - Rate limiting implementation
- [02_anti_scraping_tech/](../02_anti_scraping_tech/) - Understanding why sites block

---

*Part of [00_foundations](../) - The complete web scraping knowledge base*
