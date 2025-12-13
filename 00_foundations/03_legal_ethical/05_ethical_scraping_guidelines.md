# Ethical Scraping Guidelines

> **Being a Good Citizen of the Web**

Legal compliance is the floor, not the ceiling. Ethical scraping goes beyond what's legally required to consider the broader impact of your actions.

---

## The Golden Rule of Scraping

> **Treat websites as you would want your own website treated.**

If you ran a website, would you be okay with:
- Someone making 1000 requests per second?
- Bots consuming 50% of your bandwidth?
- Your content republished elsewhere?
- Your data sold to competitors?

---

## Core Ethical Principles

### 1. Minimize Impact

Your scraper should be invisible to real users.

```python
IMPACT_GUIDELINES = {
    # Rate limiting
    "requests_per_second": 1,  # Start conservative
    "concurrent_requests": 1,  # Don't parallelize aggressively
    "time_between_pages": "2-5 seconds random",
    
    # Resource respect
    "avoid_peak_hours": True,  # Scrape during off-peak
    "stop_on_errors": True,    # 5xx means back off
    "cache_responses": True,   # Don't re-request unnecessarily
    
    # Data minimization
    "only_what_needed": True,  # Don't scrape everything "just in case"
}
```

### 2. Be Transparent

Identify yourself and your purpose.

```python
# Good User-Agent
USER_AGENT = "MyResearchBot/1.0 (+https://mysite.com/about-bot; contact@mysite.com)"

# Provides:
# - Bot name and version
# - URL with more information
# - Contact email for questions
```

### 3. Respect Boundaries

Honor stated and implied limits.

```python
BOUNDARIES = {
    "robots_txt": "Always check and respect",
    "rate_limits": "Stay well under limits",
    "login_walls": "Don't bypass unless authorized",
    "captchas": "Signal to slow down",
    "cease_and_desist": "Take seriously",
}
```

### 4. Consider Purpose

Different purposes warrant different approaches.

| Purpose | Ethical Latitude |
|---------|------------------|
| Personal use | More flexibility |
| Academic research | Usually acceptable |
| Journalism/public interest | Often justified |
| Commercial aggregation | Most scrutiny |
| Competitive intelligence | Careful consideration |

---

## Practical Guidelines

### Before You Scrape

```python
PRE_SCRAPING_CHECKLIST = [
    "Is there an official API?",
    "Is there a data download available?",
    "Can I partner/license the data?",
    "What does robots.txt say?",
    "What does ToS say?",
    "What's the minimum data I need?",
    "How will I use this data?",
    "Could this harm the site or its users?",
]
```

### Rate Limiting Best Practices

```python
import time
import random

class EthicalScraper:
    def __init__(self):
        self.min_delay = 2.0  # Minimum seconds between requests
        self.max_delay = 5.0  # Maximum seconds
        self.error_backoff = 30  # Wait time on errors
        
    def wait(self):
        """Human-like random delay."""
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)
    
    def handle_error(self, status_code):
        """Respectful error handling."""
        if status_code == 429:  # Too many requests
            print("Rate limited - backing off significantly")
            time.sleep(self.error_backoff * 2)
        elif status_code >= 500:  # Server error
            print("Server error - backing off")
            time.sleep(self.error_backoff)
            # Consider stopping if persistent
```

### Time-of-Day Awareness

```python
from datetime import datetime

def is_good_scraping_time():
    """Prefer off-peak hours."""
    hour = datetime.now().hour
    
    # Prefer late night / early morning (server's timezone)
    if 1 <= hour <= 6:
        return True
    
    # Avoid business hours peak
    if 9 <= hour <= 17:
        return False
    
    return True  # Evening is usually okay
```

### Data Minimization

```python
# BAD: Scrape everything
def scrape_profile_bad(url):
    page = get_page(url)
    return page.text  # Stores entire HTML

# GOOD: Extract only what's needed
def scrape_profile_good(url):
    page = get_page(url)
    return {
        "name": extract_name(page),
        "title": extract_title(page),
        # Only the specific fields needed
    }
```

---

## Respecting Different Stakeholders

### Website Operators

**Their Concerns:**
- Server costs and performance
- Data protection
- Competitive position
- Legal liability

**Your Response:**
- Minimize server load
- Don't redistribute protected content
- Don't use data to compete unfairly
- Respond to communications

### End Users

**Their Concerns:**
- Privacy of their data
- Site availability
- Data accuracy

**Your Response:**
- Never scrape private user data
- Don't degrade site performance
- Handle data responsibly

### Data Subjects

**Their Concerns:**
- How their information is used
- Right to privacy
- Control over their data

**Your Response:**
- Minimize personal data collection
- Anonymize where possible
- Comply with privacy laws (GDPR, CCPA)
- Consider purpose and consent

---

## Ethical Decision Framework

### Questions to Ask

```
1. LEGAL: Is this legal?
   └─ If no: Don't do it
   └─ If yes: Continue...

2. TRANSPARENT: Would I be comfortable if the site owner knew?
   └─ If no: Reconsider
   └─ If yes: Continue...

3. IMPACT: Could this harm anyone?
   └─ The website?
   └─ The site's users?
   └─ People whose data is scraped?
   └─ If yes: Mitigate or reconsider

4. PURPOSE: Is my purpose legitimate?
   └─ Would a reasonable person find it acceptable?
   └─ Does the benefit outweigh the burden?

5. ALTERNATIVES: Have I explored other options?
   └─ APIs, downloads, partnerships?
   └─ If not: Try those first
```

### Red Flags

Stop and reconsider if:
- 🚩 You're bypassing security measures
- 🚩 You're accessing private/personal data
- 🚩 You're ignoring explicit prohibitions
- 🚩 Your scraping degrades the site
- 🚩 You wouldn't want this done to you
- 🚩 You're hiding your identity/purpose
- 🚩 The site has asked you to stop

---

## Handling Sensitive Situations

### Personal Data

```python
PERSONAL_DATA_RULES = {
    # Avoid if possible
    "collection": "Minimize personal data scraping",
    "storage": "Encrypt, limit retention",
    "sharing": "Never without proper authorization",
    
    # GDPR/CCPA considerations
    "legal_basis": "Required in many jurisdictions",
    "rights": "Individuals have rights to their data",
    "notification": "May need to inform data subjects",
}
```

### Public Figures vs. Private Individuals

| Category | Approach |
|----------|----------|
| Public figures | Less privacy expectation for public activities |
| Private individuals | Higher privacy protection |
| Minors | Extreme caution, usually avoid |

### Sensitive Categories

Extra care with:
- Health information
- Financial data
- Political affiliation
- Religious beliefs
- Sexual orientation
- Criminal history

---

## Building Ethical Scrapers

### Code-Level Ethics

```python
class EthicalScraperBase:
    """Base class enforcing ethical practices."""
    
    def __init__(self):
        self.robots_parser = RobotsParser()
        self.rate_limiter = RateLimiter(requests_per_second=0.5)
        self.user_agent = "EthicalBot/1.0 (+https://example.com/bot)"
    
    def can_scrape(self, url):
        """Check if scraping is allowed."""
        # Check robots.txt
        if not self.robots_parser.can_fetch(self.user_agent, url):
            print(f"Blocked by robots.txt: {url}")
            return False
        return True
    
    def scrape(self, url):
        """Scrape with ethical guardrails."""
        if not self.can_scrape(url):
            return None
        
        # Respect rate limits
        self.rate_limiter.wait()
        
        # Make request with identification
        response = self.session.get(url, headers={
            "User-Agent": self.user_agent
        })
        
        # Handle errors gracefully
        if response.status_code >= 400:
            self.handle_error(response)
            return None
        
        return response
```

### Logging and Transparency

```python
import logging

# Keep records of your scraping
logging.basicConfig(
    filename='scraping.log',
    format='%(asctime)s - %(message)s'
)

def log_scrape(url, status):
    logging.info(f"Scraped {url} - Status: {status}")

# Be able to demonstrate:
# - What you scraped
# - When you scraped it
# - How you handled it
```

---

## Summary: The Ethical Scraper's Code

```python
ETHICAL_CODE = {
    # Respect
    "respect_robots_txt": True,
    "respect_rate_limits": True,
    "respect_cease_and_desist": True,
    
    # Transparency
    "identify_yourself": True,
    "state_purpose_if_asked": True,
    "provide_contact_info": True,
    
    # Minimization
    "collect_only_needed": True,
    "retain_only_necessary": True,
    "process_only_authorized": True,
    
    # Consideration
    "consider_impact": True,
    "consider_privacy": True,
    "consider_alternatives": True,
    
    # Accountability
    "log_activities": True,
    "handle_complaints": True,
    "update_practices": True,
}
```

### Key Takeaways

1. **Legal is the floor** - Ethics goes further
2. **Be transparent** - Identify yourself and your purpose
3. **Minimize impact** - Rate limit, cache, off-peak
4. **Respect boundaries** - robots.txt, ToS, explicit requests
5. **Consider all stakeholders** - Sites, users, data subjects
6. **When in doubt, don't** - Or ask first

---

*This completes the Legal & Ethical section. Next: [../04_tools_ecosystem/](../04_tools_ecosystem/) - Tools of the trade*
