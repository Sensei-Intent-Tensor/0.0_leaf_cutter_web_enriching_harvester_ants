# LinkedIn Scraper

> **Professional Network Data**

LinkedIn is the primary source for professional data, company information, and B2B contacts.

---

## ⚠️ CRITICAL WARNING

### Legal Risks
- LinkedIn actively sues scrapers (hiQ Labs v. LinkedIn)
- ToS strictly prohibits scraping
- Can result in legal action and account bans
- **USE OFFICIAL APIs OR LICENSED DATA PROVIDERS**

### Technical Challenges
- Sophisticated bot detection
- Login required for most data
- CAPTCHA and verification loops
- Rate limiting based on multiple signals
- Session fingerprinting

---

## 📊 Data Categories

### Public Profiles (Limited)
- Name, headline, location
- Current company
- Public posts

### Authenticated Access
- Full work history
- Education
- Skills & endorsements
- Connections
- Contact info (with permission)

### Company Pages
- Company overview
- Employee count
- Recent updates
- Job listings

---

## 🔧 Legitimate Alternatives

### 1. LinkedIn Official APIs
```python
# Marketing API, Sales Navigator API (require partnership)
# https://www.linkedin.com/developers/
```

### 2. Licensed Data Providers
- People Data Labs
- Clearbit  
- ZoomInfo
- Apollo.io

### 3. Public Data Only (With Caution)
```python
# Only scrape truly public data
# Respect robots.txt
# Use minimal request rate
# Don't store PII without consent
```

---

## 📁 Files

| File | Description |
|------|-------------|
| `README.md` | This file (warnings and guidance) |
| `linkedin_public_ant.py` | Public profile scraper (educational) |
| `company_ant.py` | Company page scraper |

---

## 🚫 What NOT to Do

1. **Don't** scrape logged-in content at scale
2. **Don't** create fake accounts
3. **Don't** bypass security measures  
4. **Don't** store personal data without consent
5. **Don't** use for spam or unsolicited contact

---

## ✅ Ethical Alternatives

1. **Ask for data directly** - Many people share on request
2. **Use official channels** - LinkedIn APIs, data partnerships
3. **Purchase licensed data** - Legal and compliant
4. **Scrape your own connections** - With rate limits

---

*Part of [02_ant_farms/00_social](../)*
