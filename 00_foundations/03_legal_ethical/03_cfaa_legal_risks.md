# CFAA & Legal Risks

> **The Computer Fraud and Abuse Act and Web Scraping**

The CFAA is a U.S. federal law that criminalizes certain computer-related activities. Understanding its scope helps you avoid serious legal trouble.

---

## What is the CFAA?

The **Computer Fraud and Abuse Act** (18 U.S.C. § 1030) is a federal law that prohibits:

- Accessing a computer without authorization
- Exceeding authorized access to obtain information
- Damaging computers or data
- Trafficking in passwords or access devices

### Why It Matters for Scraping

The CFAA was used to prosecute/sue scrapers by arguing that:
- Violating ToS = "exceeding authorized access"
- Bypassing blocks = "unauthorized access"
- Scraping = "obtaining information"

---

## Key CFAA Provisions

### § 1030(a)(2) - Obtaining Information

```
"Whoever intentionally accesses a computer without authorization 
or exceeds authorized access, and thereby obtains information 
from any protected computer..."
```

**Penalty**: Up to 5 years imprisonment (first offense)

### § 1030(a)(5) - Damaging Computers

```
"Whoever knowingly causes the transmission of a program, 
information, code, or command, and as a result intentionally 
causes damage without authorization..."
```

**Penalty**: Up to 10 years imprisonment

### "Protected Computer"

Includes ANY computer:
- Used in interstate/foreign commerce
- Connected to the internet

**Translation**: Basically every website.

---

## Van Buren v. United States (2021)

### The Game-Changer

Supreme Court case that narrowed CFAA interpretation.

**Facts:**
- Police officer accessed license plate database
- Had authorized access but used it for unauthorized purpose
- Government charged CFAA violation

**Holding:**
> "An individual 'exceeds authorized access' when he accesses a 
> computer with authorization but then obtains information located 
> in particular areas of the computer—such as files, folders, or 
> databases—that are off limits to him."

### What This Means for Scraping

**Before Van Buren:**
- Some courts: ToS violation = exceeds authorized access
- Risk: Criminal charges for scraping public data

**After Van Buren:**
- CFAA is about access gates, not use policies
- Simply violating ToS ≠ CFAA violation
- If you can access data, CFAA less likely to apply

### Important Limitations

Van Buren does NOT say:
- ❌ All scraping is legal
- ❌ ToS violations are fine
- ❌ You can bypass any security

Van Buren DOES say:
- ✅ CFAA is about access barriers
- ✅ Misuse of authorized access ≠ CFAA crime
- ✅ Narrower interpretation going forward

---

## Risk Factors Under CFAA

### Higher Risk Scenarios

| Scenario | Risk Level | Why |
|----------|------------|-----|
| Bypassing authentication | HIGH | Clearly "without authorization" |
| Ignoring IP blocks | HIGH | Circumventing access control |
| Using stolen credentials | VERY HIGH | Unauthorized access |
| After cease-and-desist | HIGH | Notice of revoked authorization |
| Causing server damage | VERY HIGH | § 1030(a)(5) violation |

### Lower Risk Scenarios

| Scenario | Risk Level | Why |
|----------|------------|-----|
| Public data, no login | LOW | No access barrier |
| Following robots.txt | LOW | Respecting stated preferences |
| ToS violation only | LOWER (post-Van Buren) | Not an access issue |
| Research purposes | LOWER | May have additional protections |

---

## Other Legal Risks

### State Computer Crime Laws

Many states have their own versions:
- California Penal Code § 502
- New York Penal Law § 156
- Texas Penal Code § 33

These may be broader than CFAA.

### Copyright Infringement

Scraping copyrighted content raises separate issues:
- Text, images, videos are copyrighted
- Facts themselves aren't copyrightable
- Compilation can have thin copyright
- Fair use may apply (research, commentary)

### Breach of Contract

Civil lawsuit for ToS violation:
- Doesn't require "unauthorized access"
- Can result in monetary damages
- Injunctions (court orders to stop)

### Trespass to Chattels

Old tort theory applied to computing:
- Interfering with another's property
- Server resources = property
- Must show actual damage (usually)

### Trade Secret Misappropriation

If data includes trade secrets:
- Confidential business information
- Economic value from secrecy
- Reasonable efforts to protect

---

## Protecting Yourself

### Technical Measures

```python
PROTECTIVE_PRACTICES = {
    # Identify yourself
    "user_agent": "MyBot/1.0 (+https://site.com/bot; me@email.com)",
    
    # Respect limits
    "rate_limiting": True,
    "respect_robots_txt": True,
    
    # Avoid triggers
    "no_auth_bypass": True,
    "no_credential_use": True,
    "no_block_circumvention": True,
    
    # Document everything
    "logging": True,
    "purpose_documented": True,
}
```

### Legal Measures

1. **Consult an attorney** for commercial projects
2. **Document your purpose** (research, personal, etc.)
3. **Keep records** of respectful practices
4. **Respond to cease-and-desist** letters seriously
5. **Consider insurance** for business operations

### If You Receive a Cease-and-Desist

1. **Take it seriously** - Don't ignore
2. **Stop scraping** (usually safest)
3. **Don't respond emotionally** 
4. **Consult a lawyer** before responding
5. **Document your actions** going forward

---

## Jurisdiction Matters

### United States

- CFAA applies
- State laws vary
- Civil litigation common

### European Union

- GDPR for personal data
- Database Directive (sui generis rights)
- National computer crime laws

### United Kingdom

- Computer Misuse Act 1990
- GDPR (retained)
- Copyright considerations

### Other Countries

Laws vary significantly:
- Some more permissive
- Some more restrictive
- Consider where data is located AND where you are

---

## Real-World Examples

### Aaron Swartz (2011)

- Downloaded academic articles from JSTOR
- Had authorized access through MIT
- Charged with CFAA violations
- Faced up to 35 years in prison
- Case dropped after his death
- Led to calls for CFAA reform

### Andrew Auernheimer (2010)

- Found AT&T customer data exposed online
- No authentication bypassed
- Charged under CFAA
- Conviction later overturned (venue issues)

### hiQ Labs (2017-2022)

- Scraped public LinkedIn profiles
- LinkedIn sent cease-and-desist
- hiQ sued for declaratory judgment
- Complex litigation, multiple appeals
- Shows even "winning" cases are expensive

---

## Summary

| Concern | Status Post-Van Buren |
|---------|----------------------|
| Bypassing login | Still CFAA risk |
| ToS violation only | Lower CFAA risk |
| After C&D letter | Elevated risk |
| Public data | Lower CFAA risk |
| Causing damage | Still serious risk |

### Key Takeaways

1. **Van Buren helps** - But doesn't make everything legal
2. **Access matters** - Bypassing gates is riskier
3. **ToS still matter** - For civil liability
4. **Geography matters** - Different laws apply
5. **When in doubt** - Get legal advice

---

*Next: [04_copyright_data_ownership.md](04_copyright_data_ownership.md) - Who owns scraped data?*
