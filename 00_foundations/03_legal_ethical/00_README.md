# 03_legal_ethical

> **Scraping Responsibly: Laws, Ethics, and Citizenship**

Web scraping operates in a complex landscape of laws, norms, and ethical considerations. This section helps you navigate these waters responsibly.

---

## 📚 Documents in This Section

| # | Document | Lines | Description |
|---|----------|-------|-------------|
| 01 | [robots.txt Guide](01_robots_txt_guide.md) | 510 | Understanding and respecting the robots exclusion protocol |
| 02 | [Terms of Service](02_terms_of_service.md) | 360 | Legal implications of website ToS |
| 03 | [Data Privacy Laws](03_data_privacy_laws.md) | 429 | GDPR, CCPA, and global privacy regulations |
| 04 | [Ethical Guidelines](04_ethical_guidelines.md) | 403 | Principles beyond legal compliance |
| 05 | [Rate Limiting Respect](05_rate_limiting_respect.md) | 464 | Being a good citizen of the web |

**Total: 2,166 lines on responsible scraping**

---

## 🎯 Key Questions This Section Answers

```
Legal Questions:
├── Is scraping legal?
├── What do Terms of Service mean for me?
├── How do privacy laws affect scraping?
└── What are the real-world legal risks?

Ethical Questions:
├── Is this the right thing to do?
├── Who could be harmed?
├── Am I being a good web citizen?
└── How would I feel if this were public?

Practical Questions:
├── How do I read robots.txt?
├── What rate should I scrape at?
├── How do I handle personal data?
└── What documentation should I keep?
```

---

## 🔑 Core Principles

### Legal Compliance

```
Must Do:
├── Read robots.txt before scraping
├── Understand relevant ToS
├── Know applicable privacy laws
└── Document your compliance efforts

Must Not:
├── Ignore cease-and-desist letters
├── Scrape personal data carelessly
├── Bypass access controls
└── Compete unfairly with scraped data
```

### Ethical Standards

```
The Golden Rule: 
"Scrape unto others as you would have them scrape unto you"

Before every project ask:
├── Purpose: Why am I doing this?
├── Harm: Who could be hurt?
├── Alternatives: Is there a better way?
├── Transparency: Can I justify this publicly?
└── Proportionality: Is my impact reasonable?
```

### Technical Respect

```
Good Citizenship:
├── Rate limit conservatively
├── Identify your bot
├── Honor Crawl-delay directives
├── Stop if causing problems
└── Scrape during off-peak hours
```

---

## 📊 Quick Reference

### Risk Assessment Matrix

| Factor | Lower Risk | Higher Risk |
|--------|------------|-------------|
| **Data** | Public, non-personal | Personal, behind login |
| **ToS** | Silent or permissive | Explicitly prohibits |
| **robots.txt** | Allows or absent | Disallows |
| **Use** | Research, personal | Commercial, competitive |
| **Impact** | Minimal server load | Heavy traffic |
| **Region** | Few regulations | GDPR/CCPA applies |

### Rate Limiting Defaults

| Site Type | Recommended Rate |
|-----------|------------------|
| Unknown | 1 request / 5 seconds |
| Small site | 1 request / 10 seconds |
| Medium site | 1 request / 2 seconds |
| Large site | 2-5 requests / second |
| With Crawl-delay | Honor the directive |

### Privacy Law Overview

| Law | Region | Key Point |
|-----|--------|-----------|
| GDPR | EU | Broad "personal data" definition |
| CCPA | California | Consumer rights to data |
| LGPD | Brazil | Similar to GDPR |
| PIPEDA | Canada | Consent-focused |

---

## 🛠️ Practical Implementation

### Before Starting Any Scrape

```python
def pre_scrape_checklist(url):
    """Run through legal/ethical checks."""
    
    # 1. Check robots.txt
    robots_ok = check_robots_txt(url)
    
    # 2. Review ToS (manual)
    print("Have you reviewed the Terms of Service?")
    
    # 3. Assess data type
    has_personal_data = assess_personal_data(url)
    
    # 4. Determine appropriate rate
    rate = determine_rate(url)
    
    # 5. Document purpose
    document_purpose()
    
    return {
        'robots_ok': robots_ok,
        'personal_data': has_personal_data,
        'recommended_rate': rate
    }
```

### Respectful Request Pattern

```python
class RespectfulScraper:
    def __init__(self, user_agent='MyBot/1.0 (contact@email.com)'):
        self.session = requests.Session()
        self.session.headers['User-Agent'] = user_agent
        self.robots_checker = RobotsChecker(user_agent)
        self.rate_limiter = DomainRateLimiter()
    
    def fetch(self, url):
        # Check robots.txt
        if not self.robots_checker.can_fetch(url):
            raise BlockedByRobots(url)
        
        # Apply rate limiting
        self.rate_limiter.wait(url)
        
        return self.session.get(url)
```

---

## ⚠️ Red Flags

### Stop Immediately If:

- 🚩 You receive a cease-and-desist
- 🚩 You're causing site performance issues
- 🚩 You discover you're collecting protected data
- 🚩 Your use case has changed to something questionable
- 🚩 You're being actively blocked

### Seek Legal Advice If:

- Commercial use of substantial scraped data
- Data involves EU/California residents
- Competitor data for business decisions
- Health, financial, or other sensitive data
- Prior legal issues with the site

---

## 🔗 Related Sections

- **[00_terminology/](../00_terminology/)** - Legal terms defined
- **[01_technical_operations/](../01_technical_operations/)** - Rate limiting implementation
- **[02_anti_scraping_tech/](../02_anti_scraping_tech/)** - Understanding why sites block

---

## 📝 Documentation Template

Keep records of your scraping decisions:

```
Project: [Name]
Date: [Date]
Target: [URL]

Legal Review:
- robots.txt checked: [Yes/No]
- ToS reviewed: [Yes/No]
- Privacy assessment: [Notes]

Ethical Assessment:
- Purpose: [Description]
- Potential harm: [Assessment]
- Justification: [Why this is acceptable]

Technical Plan:
- Rate limit: [X requests/second]
- Duration: [Estimate]
- Data handling: [How personal data is handled]

Approval: [Your sign-off]
```

---

*Part of [00_foundations](../) - The complete web scraping knowledge base*
