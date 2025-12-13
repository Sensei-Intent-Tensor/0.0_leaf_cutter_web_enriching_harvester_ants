# Terms of Service

> **The Legal Fine Print That Can Bite**

Website Terms of Service (ToS) are legal agreements that may restrict scraping. Understanding their implications helps you make informed decisions.

---

## What Are Terms of Service?

A legal contract between the website and its users. By using the site, you may be agreeing to these terms.

```
┌────────────────────────────────────────────┐
│            TERMS OF SERVICE                │
├────────────────────────────────────────────┤
│                                            │
│  By using this website, you agree to:      │
│                                            │
│  • Not scrape, crawl, or spider the site   │
│  • Not use automated tools                 │
│  • Not collect user data                   │
│  • Respect intellectual property           │
│  • Not compete with our services           │
│                                            │
│  Violation may result in:                  │
│  • Account termination                     │
│  • Legal action                            │
│  • Monetary damages                        │
│                                            │
└────────────────────────────────────────────┘
```

---

## Common Anti-Scraping Clauses

### Direct Prohibition

```
"You may not use any automated means, including robots, 
crawlers, or data mining tools, to download, monitor, 
or use data or content from the Service."
```

### Broad Prohibition

```
"You agree not to access the Service by any means other 
than through the interface that is provided by the Company."
```

### Data Collection Prohibition

```
"You may not collect, harvest, or assemble information 
about other users, including email addresses, without 
their consent."
```

### Competition Clause

```
"You may not use information obtained from the Service 
to develop or operate a service that competes with ours."
```

### Rate Limits

```
"You agree not to make more than 100 requests per minute 
to our API or website."
```

---

## Legal Framework

### Contract Law

ToS are contracts. Violating them could be:
- **Breach of contract** - Civil liability
- **Tortious interference** - If affecting business
- **Trespass to chattels** - Unauthorized use of servers

### Computer Fraud and Abuse Act (CFAA)

US federal law that can apply to scraping:

```
CFAA Violations:
├── Accessing computer "without authorization"
├── Exceeding authorized access
└── Obtaining information from protected computers
```

**Key Cases:**
- **hiQ vs LinkedIn (2022)**: Scraping publicly accessible data is not CFAA violation
- **Van Buren vs US (2021)**: CFAA requires bypassing access gates, not just ToS violation

### State Laws

Various states have computer crime laws:
- California: Computer Fraud and Abuse Act
- Texas: Breach of Computer Security
- Many others

---

## ToS Enforceability

### Factors Courts Consider

| Factor | More Enforceable | Less Enforceable |
|--------|------------------|------------------|
| **Notice** | Click-through acceptance | Buried in footer |
| **Clarity** | Specific prohibitions | Vague language |
| **Access** | Requires account | Public data |
| **Damage** | Demonstrated harm | No actual damage |
| **Consent** | Explicit agreement | Implied |

### Browse-Wrap vs Click-Wrap

**Click-Wrap** (More Enforceable):
```
┌─────────────────────────────────────┐
│ ☐ I have read and agree to the     │
│   Terms of Service                  │
│                                     │
│         [Create Account]            │
└─────────────────────────────────────┘
```

**Browse-Wrap** (Less Enforceable):
```
┌─────────────────────────────────────┐
│  [Page content]                     │
│                                     │
│  ───────────────────────────────    │
│  By using this site, you agree to   │
│  our Terms of Service               │
└─────────────────────────────────────┘
```

---

## Risk Assessment Framework

### Low Risk Scenarios

- Public data, no account required
- No robots.txt restrictions
- No ToS or ToS allows scraping
- Non-commercial/research use
- No personal data
- Respectful rate limiting

### Medium Risk Scenarios

- ToS prohibits scraping but not enforced
- Account required but public data
- Commercial use of non-sensitive data
- Aggregation without direct competition

### High Risk Scenarios

- ToS explicitly prohibits + enforced
- Login required to access data
- Competing service using the data
- Personal/proprietary data
- Received cease-and-desist
- Site actively blocks you

---

## Reading ToS Strategically

### Key Sections to Check

```python
def analyze_tos(tos_text):
    """Find scraping-relevant sections in ToS."""
    
    keywords = {
        'scraping_terms': [
            'scrape', 'scraping', 'crawl', 'crawler', 'spider',
            'harvest', 'data mining', 'automated', 'bot', 'robot',
            'programmatic access', 'bulk download'
        ],
        'data_terms': [
            'collect', 'gather', 'aggregate', 'compile',
            'download', 'copy', 'reproduce'
        ],
        'prohibition_terms': [
            'not permitted', 'prohibited', 'forbidden',
            'may not', 'shall not', 'must not', 'agree not to'
        ],
        'exception_terms': [
            'unless', 'except', 'permitted', 'authorized',
            'written consent', 'prior approval'
        ]
    }
    
    findings = {}
    for category, terms in keywords.items():
        for term in terms:
            if term.lower() in tos_text.lower():
                # Find surrounding context
                # ...
                pass
    
    return findings
```

### Questions to Answer

1. Does it explicitly mention scraping/crawling?
2. Does it prohibit automated access?
3. Does it restrict data collection?
4. Are there exceptions for research/personal use?
5. What are the stated consequences?
6. Is it browse-wrap or click-wrap?
7. When was it last updated?

---

## Notable ToS Examples

### LinkedIn

```
"You agree that you will not:

...scrape or copy profiles and information of others through 
any means (including crawlers, browser plugins and add-ons, 
and any other technology or manual work)..."
```

**Enforcement**: Actively sues scrapers, uses aggressive detection.

### Twitter/X

```
"You may not do any of the following while accessing or using 
the Services: access, search, or create accounts for the Services 
by any means other than our publicly supported interfaces..."
```

**Enforcement**: API rate limits, account bans, occasional legal action.

### Amazon

```
"This license does not include any... collection and use of any 
product listings, descriptions, or prices; any derivative use of 
any Amazon Service or its contents; any downloading, copying, or 
other use of account information for the benefit of any third party..."
```

**Enforcement**: Technical blocks, account termination.

### Wikipedia

```
"You are free to: Share, copy and redistribute the material in 
any medium or format; Adapt, remix, transform, and build upon the 
material for any purpose, even commercially."
```

**Enforcement**: Generally permissive, honors CC license.

---

## Risk Mitigation Strategies

### Technical Measures

```python
# Behave more like a legitimate user
measures = {
    'rate_limit': True,           # Don't overwhelm servers
    'identify_bot': True,         # Use honest User-Agent
    'respect_robots': True,       # Follow robots.txt
    'cache_responses': True,      # Don't re-request
    'off_peak_hours': True,       # Scrape during low traffic
}
```

### Business Measures

```
1. Document legitimate purpose
2. Avoid competing directly with source
3. Don't scrape personal data
4. Add value, don't just copy
5. Consider reaching out for permission
6. Have legal review if commercial
```

### If You Receive Cease-and-Desist

```
1. Stop scraping immediately
2. Document what you've done
3. Do not respond without legal counsel
4. Review the claims carefully
5. Consider negotiation
6. Preserve evidence of good faith
```

---

## Alternatives to Risky Scraping

### Official Channels

| Option | Description |
|--------|-------------|
| **API** | Many sites offer official APIs |
| **Data licensing** | Buy/license data directly |
| **Partnerships** | Business development agreement |
| **RSS feeds** | Legitimate syndication |
| **Data providers** | Third parties who have agreements |

### Safe Data Sources

```
Public Data Sources:
├── Government databases
├── Open data initiatives
├── Academic datasets
├── Creative Commons content
├── Official APIs
└── Data marketplaces
```

---

## Summary

| Situation | Risk Level | Recommendation |
|-----------|------------|----------------|
| Public data, no ToS restriction | Low | Proceed carefully |
| ToS prohibits but not enforced | Medium | Consider alternatives |
| ToS prohibits + actively enforced | High | Avoid or get permission |
| Account required + ToS prohibits | High | Use official API |
| Personal/proprietary data | Very High | Do not scrape |

### Key Takeaways

1. **Read the ToS** before scraping
2. **Assess enforceability** - browse-wrap vs click-wrap
3. **Consider the context** - public vs authenticated
4. **Document good faith** - rate limiting, identification
5. **Seek alternatives** - APIs, licensing, partnerships
6. **Consult legal counsel** for commercial projects

---

*Next: [03_data_privacy_laws.md](03_data_privacy_laws.md) - GDPR, CCPA, and data protection*
