# Terms of Service

> **The Legal Fine Print That Matters**

Terms of Service (ToS) are legal contracts between websites and users. Understanding them is essential for responsible scraping—even if most people never read them.

---

## What Are Terms of Service?

A legal agreement that:
- Defines acceptable use
- Limits liability
- Grants/restricts rights
- May prohibit scraping

### Also Known As

- Terms of Use (ToU)
- Terms & Conditions (T&C)
- User Agreement
- Acceptable Use Policy (AUP)

---

## ToS and Scraping

### Common Prohibitions

Most commercial websites include language like:

```
"You agree not to:
- Use any robot, spider, scraper, or other automated means 
  to access the Service
- Collect or harvest any information from the Service
- Reproduce, copy, or redistribute content from the Service
- Access the Service for competitive purposes"
```

### Why This Matters

1. **Contract Law** - Clicking "I Agree" or using the site may create a contract
2. **Breach of Contract** - Violating terms can have legal consequences
3. **CFAA Concerns** - Some argue ToS violations = "unauthorized access"
4. **Civil Liability** - Site can sue for damages

---

## Legal Landscape

### Key Cases

#### hiQ v. LinkedIn (2022)
- hiQ scraped public LinkedIn profiles
- LinkedIn claimed ToS violation + CFAA
- **Result**: Scraping public data generally allowed
- **But**: Case about *public* data, LinkedIn later won on other grounds

#### Van Buren v. United States (2021)
- Supreme Court CFAA case
- **Result**: CFAA is about access, not misuse
- **Implication**: ToS violations alone may not be "unauthorized access"

#### Sandvig v. Sessions (2020)
- Researchers challenged CFAA scope
- **Result**: ToS violations aren't automatically federal crimes

#### Craigslist v. 3Taps (2013)
- 3Taps ignored cease-and-desist and technical blocks
- **Result**: $3.5M judgment - but involved active evasion

### Current Legal State

| Situation | Risk Level |
|-----------|------------|
| Public data, no ToS violation | Low |
| Public data, ToS prohibits | Medium |
| Behind login, ToS prohibits | Higher |
| Ignoring cease-and-desist | High |
| Bypassing technical blocks | High |
| Commercial use of scraped data | Varies |

---

## What ToS Actually Say

### Amazon

```
"You may not use any robot, spider, scraper, data mining tools,
data gathering and extraction tools, or other automated means
to access the Site for any purpose..."
```

### LinkedIn

```
"You agree that you will not use software, devices, scripts,
robots, other means or processes to access, 'scrape', 'crawl'
or 'spider' any web pages or other services contained in the site."
```

### Twitter/X

```
"Scraping the Services without the prior consent of Twitter
is expressly prohibited."
```

### Facebook

```
"You will not collect users' content or information,
or otherwise access Facebook, using automated means
(such as harvesting bots, robots, spiders, or scrapers)
without our prior permission."
```

### Google

```
"Don't misuse our Services. For example, don't:
- use automated means to access the Services..."
```

---

## Risk Assessment Framework

### Factors That Increase Risk

| Factor | Risk Increase |
|--------|---------------|
| Commercial purpose | ⬆️⬆️⬆️ |
| Competing with site | ⬆️⬆️⬆️ |
| Ignoring cease-and-desist | ⬆️⬆️⬆️ |
| Bypassing technical blocks | ⬆️⬆️ |
| Republishing content | ⬆️⬆️ |
| Creating account to scrape | ⬆️⬆️ |
| High request volume | ⬆️ |
| Impacting site performance | ⬆️⬆️ |

### Factors That Decrease Risk

| Factor | Risk Decrease |
|--------|---------------|
| Public data only | ⬇️⬇️ |
| Academic research | ⬇️⬇️ |
| Personal use | ⬇️⬇️ |
| No republishing | ⬇️ |
| Respectful rate limiting | ⬇️ |
| No login required | ⬇️ |
| Following robots.txt | ⬇️ |

---

## Practical Guidance

### Before Scraping: Checklist

```python
LEGAL_CHECKLIST = {
    "read_tos": "Did you read the Terms of Service?",
    "robots_txt": "Does robots.txt allow your access?",
    "public_data": "Is the data publicly accessible?",
    "login_required": "Did you need to log in?",
    "commercial_use": "Is this for commercial purposes?",
    "republishing": "Will you republish the data?",
    "competing": "Are you competing with the site?",
    "rate_respect": "Will you respect server resources?",
    "purpose": "What's your legitimate purpose?",
}
```

### Low-Risk Scraping

```python
# ✅ Generally safer:
safe_practices = {
    "public_data": True,
    "no_login": True,
    "personal_use": True,
    "no_republish": True,
    "respectful_rate": True,
    "follows_robots": True,
    "minimal_volume": True,
}
```

### Higher-Risk Activities

```python
# ⚠️ Consider carefully:
risky_activities = {
    "commercial_scraping": "May need legal review",
    "logged_in_scraping": "ToS likely violated",
    "mass_republishing": "Copyright concerns",
    "competing_service": "Highest legal risk",
    "ignoring_blocks": "Active evasion = bad",
}
```

---

## When ToS Might Not Apply

### Arguments Against Enforcement

1. **Browsewrap vs Clickwrap**
   - Clickwrap: User explicitly agrees (more enforceable)
   - Browsewrap: Terms exist but no explicit agreement (less enforceable)

2. **Reasonable Notice**
   - Were terms clearly visible?
   - Did user have real opportunity to read?

3. **Unconscionability**
   - Were terms unreasonably one-sided?
   - Was there meaningful choice?

4. **Public Interest**
   - Research purposes
   - Journalism
   - Accessibility

### Not Legal Advice

```
⚠️ DISCLAIMER

This document provides general information, not legal advice.
Laws vary by jurisdiction and change over time.
Consult a qualified attorney for specific situations.
```

---

## Best Practices

### Be Transparent

```python
# Identify yourself
USER_AGENT = "MyResearchBot/1.0 (+https://mysite.com/bot; contact@mysite.com)"

# This allows sites to:
# - Know who you are
# - Contact you if issues
# - Potentially whitelist you
```

### Document Your Purpose

Keep records of:
- Why you're scraping
- What data you're collecting
- How you'll use it
- Steps taken to be respectful

### Respond to Requests

If site contacts you:
- Take it seriously
- Respond professionally
- Stop if asked (usually safest)
- Consult lawyer if commercial/important

### Consider Alternatives

Before scraping, check for:
- Official APIs
- Data downloads
- Research partnerships
- Licensing agreements

```python
ALTERNATIVES = {
    "official_api": "Twitter API, Reddit API, etc.",
    "bulk_downloads": "Wikipedia dumps, Common Crawl",
    "data_providers": "Data.world, Kaggle datasets",
    "partnerships": "Academic data access programs",
}
```

---

## Case-by-Case Analysis

### Scenario 1: Price Monitoring

```
Situation: Track competitor prices for personal shopping
ToS: Prohibits automated access
Risk: LOW (personal use, public data)
Recommendation: Proceed cautiously, low volume
```

### Scenario 2: Research Project

```
Situation: Academic study of social media trends
ToS: Prohibits scraping
Risk: MEDIUM (research exception may apply)
Recommendation: Check for research API, IRB approval
```

### Scenario 3: Commercial Aggregator

```
Situation: Build competing price comparison site
ToS: Explicitly prohibits
Risk: HIGH (commercial + competing)
Recommendation: Seek legal advice, consider licensing
```

### Scenario 4: News Archive

```
Situation: Archive news articles for posterity
ToS: Prohibits copying content
Risk: MEDIUM (public interest vs copyright)
Recommendation: Use Internet Archive instead
```

---

## Summary

| Aspect | Consideration |
|--------|---------------|
| **ToS Binding?** | Usually yes if you used the site |
| **Enforceable?** | Depends on notice and agreement type |
| **Criminal Risk?** | Low for pure ToS violation (post-Van Buren) |
| **Civil Risk** | Real, especially for commercial use |
| **Best Practice** | Read ToS, assess risk, be respectful |

### Key Takeaways

1. **ToS matter** - Even if rarely enforced, they're legal agreements
2. **Public ≠ Permitted** - Public data can still have ToS restrictions
3. **Purpose matters** - Research vs commercial makes a difference
4. **Blocks matter** - Circumventing technical measures increases risk
5. **When in doubt** - Consult a lawyer for commercial projects

---

*Next: [03_cfaa_legal_risks.md](03_cfaa_legal_risks.md) - Understanding the Computer Fraud and Abuse Act*
