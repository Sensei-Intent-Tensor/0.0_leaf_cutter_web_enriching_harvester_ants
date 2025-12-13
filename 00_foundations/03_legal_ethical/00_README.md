# 03_legal_ethical

> **Scraping Responsibly and Legally**

This section covers the legal landscape and ethical considerations for web scraping. Understanding these principles protects you legally and makes you a better citizen of the web.

---

## 📚 Documents in This Section

| # | Document | Lines | Description |
|---|----------|-------|-------------|
| 01 | [robots.txt Explained](01_robots_txt_explained.md) | 491 | The standard for communicating crawling preferences |
| 02 | [Terms of Service](02_terms_of_service.md) | 348 | Understanding ToS implications for scraping |
| 03 | [CFAA & Legal Risks](03_cfaa_legal_risks.md) | 285 | Computer Fraud and Abuse Act and scraping |
| 04 | [Copyright & Data Ownership](04_copyright_data_ownership.md) | 329 | Who owns scraped data and content |
| 05 | [Ethical Scraping Guidelines](05_ethical_scraping_guidelines.md) | 399 | Being a good citizen of the web |

**Total: 1,852 lines of legal and ethical guidance**

---

## 🎯 Reading Order

### Essential Knowledge

Read in order:
1. **robots.txt** - The first thing to check
2. **Terms of Service** - Understanding the legal agreement
3. **CFAA & Legal Risks** - What could go wrong
4. **Copyright** - What you can and can't take
5. **Ethics** - Going beyond legal compliance

### Quick Reference

- Planning a scrape? → robots.txt, ToS
- Commercial project? → CFAA, Copyright
- Want to do it right? → Ethics

---

## 🔑 Key Takeaways by Document

### robots.txt Explained
- Located at `/robots.txt` on every site
- Advisory but industry-standard to respect
- Check before scraping ANY site
- Use `urllib.robotparser` in Python

### Terms of Service
- Most sites prohibit scraping
- ToS violations ≠ criminal (usually)
- But can lead to civil liability
- Commercial use increases risk

### CFAA & Legal Risks
- Van Buren narrowed CFAA scope
- Access barriers matter more than ToS
- Bypassing security is still risky
- Cease-and-desist letters matter

### Copyright & Data Ownership
- Facts aren't copyrightable
- Expression is protected
- Transform data to reduce risk
- EU has database rights

### Ethical Scraping Guidelines
- Legal is the floor, not ceiling
- Identify yourself transparently
- Minimize impact on servers
- Respect all stakeholders

---

## ⚖️ Quick Legal Assessment

```python
def assess_scraping_risk(scenario):
    """Quick risk assessment framework."""
    
    risk_factors = {
        # Lower risk
        "public_data": -2,
        "personal_use": -2,
        "research_purpose": -1,
        "follows_robots_txt": -1,
        "respectful_rate": -1,
        
        # Higher risk
        "behind_login": +2,
        "commercial_use": +2,
        "competing_service": +3,
        "ignoring_blocks": +3,
        "after_cease_desist": +4,
        "bypassing_security": +4,
        "republishing_content": +2,
    }
    
    # Sum applicable factors
    # Negative = lower risk, Positive = higher risk
```

### Risk Levels

| Score | Risk Level | Recommendation |
|-------|------------|----------------|
| < -3 | Low | Proceed with normal caution |
| -3 to 0 | Medium | Consider carefully |
| 0 to 3 | High | Consult attorney |
| > 3 | Very High | Probably don't |

---

## 📋 Pre-Scraping Checklist

```
□ Checked robots.txt
□ Read relevant ToS sections  
□ Data is publicly accessible
□ Purpose is legitimate
□ Rate limiting implemented
□ User-Agent identifies bot
□ Only collecting necessary data
□ Not republishing copyrighted content
□ Considered privacy implications
□ Have plan for cease-and-desist
```

---

## 🚫 Red Lines

Things you should **never** do:

```python
NEVER_DO = [
    "Bypass authentication without authorization",
    "Use stolen or shared credentials",
    "Ignore cease-and-desist letters",
    "Scrape private user data",
    "Republish copyrighted content verbatim",
    "Deny it's automated when asked",
    "Continue after explicitly blocked",
    "Overwhelm servers intentionally",
    "Scrape children's data",
    "Violate privacy laws (GDPR, CCPA)",
]
```

---

## ✅ Safe Practices

Things that are generally **lower risk**:

```python
SAFER_PRACTICES = [
    "Public data only (no login)",
    "Respect robots.txt",
    "Rate limit aggressively",
    "Identify your bot",
    "Personal/research use",
    "Extract facts, not expression",
    "Provide contact information",
    "Respond to communications",
    "Document your purpose",
    "Use official APIs when available",
]
```

---

## 🔗 Related Sections

- **[02_anti_scraping_tech/](../02_anti_scraping_tech/)** - Technical measures you may encounter
- **[01_technical_operations/](../01_technical_operations/)** - How to implement respectful scraping

---

## ⚠️ Disclaimer

```
This section provides general information about legal and ethical
considerations in web scraping. It is NOT legal advice.

Laws vary by jurisdiction and change over time. Individual 
circumstances matter significantly.

For commercial projects or situations with legal risk, consult 
a qualified attorney in your jurisdiction.
```

---

## 📖 Further Reading

- [EFF: CFAA Reform](https://www.eff.org/issues/cfaa)
- [GDPR Text](https://gdpr.eu/)
- [CCPA Text](https://oag.ca.gov/privacy/ccpa)
- [robots.txt Specification](https://www.robotstxt.org/)

---

*Part of [00_foundations](../) - The complete web scraping knowledge base*
