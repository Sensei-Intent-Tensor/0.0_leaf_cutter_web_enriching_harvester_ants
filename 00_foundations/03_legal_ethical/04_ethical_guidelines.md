# Ethical Guidelines

> **Doing the Right Thing, Not Just the Legal Thing**

Legal compliance is the floor, not the ceiling. This document outlines ethical principles for responsible web scraping that go beyond minimum legal requirements.

---

## The Ethics Framework

```
┌─────────────────────────────────────────────────────────────┐
│                    Ethical Hierarchy                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌───────────────────────────────────────────────────┐    │
│   │              ASPIRATIONAL                          │    │
│   │   • Contribute to open data                        │    │
│   │   • Improve the ecosystem                          │    │
│   └───────────────────────────────────────────────────┘    │
│                         ▲                                   │
│   ┌───────────────────────────────────────────────────┐    │
│   │              ETHICAL                               │    │
│   │   • Minimize harm                                  │    │
│   │   • Respect intent                                 │    │
│   │   • Be transparent                                 │    │
│   └───────────────────────────────────────────────────┘    │
│                         ▲                                   │
│   ┌───────────────────────────────────────────────────┐    │
│   │              LEGAL                                 │    │
│   │   • Follow the law                                 │    │
│   │   • Respect ToS                                    │    │
│   │   • Honor robots.txt                               │    │
│   └───────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Ethical Principles

### 1. Do No Harm

**To the Website:**
- Don't crash or slow down servers
- Don't interfere with legitimate users
- Don't consume excessive resources

**To Individuals:**
- Don't expose private information
- Don't enable stalking or harassment
- Don't facilitate discrimination

**To Society:**
- Don't spread misinformation
- Don't enable market manipulation
- Don't undermine journalism

### 2. Respect Intent

Even if technically possible, consider:

```
Questions to Ask:
├── Would the site owner approve of this use?
├── Is this use aligned with how the data was shared?
├── Am I circumventing the spirit of restrictions?
└── Would I be comfortable if this were public?
```

### 3. Transparency

```
Good Practice:
├── Identify your bot in User-Agent
├── Provide contact information
├── Explain your purpose if asked
└── Don't pretend to be human
```

### 4. Proportionality

```
Match your impact to your need:

Need: Check price once daily
Impact: 1 request/day ✓

Need: Build complete archive
Impact: 1M requests/hour ✗
Better: Request data feed, use API
```

### 5. Fairness

```
Consider:
├── Am I taking value without giving back?
├── Am I competing unfairly with the source?
├── Am I displacing jobs unethically?
└── Am I exacerbating inequalities?
```

---

## Ethical Decision Framework

### The Ethics Checklist

Before scraping, ask:

```
Purpose
├── What am I trying to accomplish?
├── Is there a less invasive way?
└── Who benefits from this?

Impact
├── How will this affect the website?
├── How will this affect individuals in the data?
├── Are there unintended consequences?

Permissions
├── Have I checked robots.txt?
├── Have I read the ToS?
├── Would the site owner object?

Data Handling
├── Am I collecting only what I need?
├── How will I protect this data?
├── When will I delete it?

Accountability
├── Can I justify this publicly?
├── Am I prepared to stop if asked?
└── Have I documented my reasoning?
```

### Red Flags

Stop and reconsider if:

```
🚩 Scraping requires bypassing security
🚩 Data includes children's information
🚩 Purpose is to harm or harass
🚩 You're creating surveillance tools
🚩 You're facilitating discrimination
🚩 You'd be embarrassed if exposed
🚩 The data could enable identity theft
🚩 You're undercutting original creator's livelihood
```

---

## Ethical Use Cases

### Clearly Ethical

| Use Case | Why |
|----------|-----|
| Academic research (public data) | Knowledge advancement |
| Journalism (public interest) | Accountability |
| Accessibility tools | Enabling disabled access |
| Archival (with permission) | Preservation |
| Price comparison (own products) | Consumer benefit |
| Environmental monitoring | Public good |

### Ethically Complex

| Use Case | Considerations |
|----------|----------------|
| Competitive intelligence | Fair competition vs. unfair advantage |
| Lead generation | Business vs. privacy |
| Content aggregation | Convenience vs. traffic theft |
| Price monitoring | Consumer benefit vs. manipulation |
| Social media analysis | Research vs. surveillance |

### Ethically Problematic

| Use Case | Why Problematic |
|----------|-----------------|
| Building profiles without consent | Privacy violation |
| Enabling harassment | Direct harm |
| Fake review generation | Deception |
| Circumventing paywalls | Theft |
| Mass data selling | Privacy commercialization |
| Political manipulation | Democracy harm |

---

## Responsible Practices

### Identify Your Bot

```python
# Good: Clear identification
headers = {
    'User-Agent': 'MyResearchBot/1.0 (https://mysite.com/bot; contact@mysite.com)'
}

# Bad: Pretending to be browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0...'
}
```

### Implement Rate Limits by Default

```python
class EthicalScraper:
    def __init__(self):
        self.last_request = {}
        self.default_delay = 2.0  # Conservative default
    
    def fetch(self, url):
        domain = urlparse(url).netloc
        
        # Always rate limit
        if domain in self.last_request:
            elapsed = time.time() - self.last_request[domain]
            if elapsed < self.default_delay:
                time.sleep(self.default_delay - elapsed)
        
        self.last_request[domain] = time.time()
        return requests.get(url, headers=self.headers)
```

### Honor Opt-Outs

```python
def check_opt_out(url, response):
    """Check for machine-readable opt-out signals."""
    
    # Check robots.txt
    if not robot_parser.can_fetch(user_agent, url):
        return True
    
    # Check X-Robots-Tag header
    if 'noindex' in response.headers.get('X-Robots-Tag', ''):
        return True
    
    # Check meta robots
    soup = BeautifulSoup(response.text)
    meta = soup.find('meta', {'name': 'robots'})
    if meta and 'noindex' in meta.get('content', ''):
        return True
    
    return False
```

### Minimize Data Collection

```python
def scrape_minimized(url, needed_fields):
    """Only collect what you actually need."""
    
    response = fetch(url)
    full_data = parse(response)
    
    # Filter to needed fields only
    minimal_data = {
        field: full_data[field] 
        for field in needed_fields 
        if field in full_data
    }
    
    return minimal_data
```

### Provide Value Back

```
Ways to Give Back:
├── Report bugs you find
├── Share non-sensitive insights
├── Cite sources properly
├── Contribute to open data
└── Build tools others can use
```

---

## Handling Gray Areas

### When Purpose is Questionable

```
Decision Tree:

Is the purpose clearly beneficial?
├── YES → Proceed carefully
└── NO or UNSURE
    │
    Who could be harmed?
    ├── No one obvious → May proceed with caution
    └── Identifiable groups
        │
        Does benefit outweigh harm?
        ├── YES → Document reasoning, add safeguards
        └── NO or UNSURE → Don't proceed
```

### When Site Preferences Unclear

```
Hierarchy of Signals:
1. Direct communication (email response)
2. robots.txt
3. Terms of Service
4. Rate limiting responses
5. Industry norms
6. Common sense
```

### When Data Sensitivity is Unclear

```
Default Conservative:
├── Treat as sensitive until proven otherwise
├── Apply maximum protections
├── Minimize collection
└── Anonymize proactively
```

---

## Professional Standards

### Journalist Standards

If scraping for journalism:
- Serve public interest
- Verify data accuracy
- Protect sources/subjects
- Be prepared to explain methods

### Research Standards

If scraping for research:
- Obtain IRB approval if applicable
- Follow discipline's ethics guidelines
- Share methodology openly
- Consider long-term data implications

### Business Standards

If scraping commercially:
- Don't misrepresent collected data
- Honor data subject rights
- Compete fairly
- Be prepared for scrutiny

---

## Self-Assessment Questions

### Before Starting

1. Why am I doing this?
2. Who benefits and who might be harmed?
3. Is there a better way to get this data?
4. Would I want this done to my website?
5. Can I justify this to a journalist?

### During Scraping

1. Am I staying within stated limits?
2. Is the site showing signs of stress?
3. Am I collecting more than needed?
4. Have my purposes changed?

### After Scraping

1. Did I minimize data retention?
2. Is the data properly secured?
3. Am I using it as originally intended?
4. Should I delete any of it?

---

## Summary

### The Golden Rules

| Rule | Implementation |
|------|----------------|
| **Do no harm** | Rate limit, minimize collection |
| **Be transparent** | Identify your bot, explain purpose |
| **Respect intent** | Follow robots.txt, honor ToS spirit |
| **Stay proportional** | Match impact to genuine need |
| **Be accountable** | Document decisions, accept responsibility |

### The Test

> "If my scraping activities were front-page news tomorrow, would I be proud of my choices?"

If the answer is no, reconsider.

---

*Next: [05_rate_limiting_respect.md](05_rate_limiting_respect.md) - Being a good citizen of the web*
