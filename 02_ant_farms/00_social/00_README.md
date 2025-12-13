# 00_social

> **Social Media & Community Platform Scrapers**

⚠️ **High Risk Category** - Most social platforms actively prohibit scraping.

---

## ⚠️ Critical Warnings

### Legal Considerations

| Platform | ToS Status | API Available | Risk Level |
|----------|------------|---------------|------------|
| LinkedIn | **Prohibits** | Yes (restricted) | **High** |
| Twitter/X | **Prohibits** | Yes (paid) | **High** |
| Facebook | **Prohibits** | Limited | **Very High** |
| Instagram | **Prohibits** | Limited | **Very High** |
| Reddit | **Allows some** | Yes (free) | **Medium** |
| YouTube | **Prohibits** | Yes (free) | **Medium** |

### Recommendations

1. **Use Official APIs** whenever possible
2. **Reddit**: Has permissive API - prefer that
3. **YouTube**: Use YouTube Data API
4. **Others**: Consider legal implications carefully

---

## 📦 Available Ants

| Ant | Platform | Notes |
|-----|----------|-------|
| [reddit_ant.py](reddit_ant.py) | Reddit | Uses official API |

---

## ⚖️ Legal Precedent

- **hiQ vs LinkedIn (2022)**: Court ruled scraping public data not CFAA violation
- **However**: Platforms continue to enforce ToS through other means
- **Best Practice**: Document your use case, use APIs, respect rate limits

---

*Part of [02_ant_farms](../) - Site-specific scraper collections*
