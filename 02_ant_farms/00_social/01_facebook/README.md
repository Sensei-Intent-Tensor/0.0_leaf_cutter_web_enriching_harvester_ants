# Facebook Scraper

> **Social Network Data**

Facebook is a major social platform - but heavily protected.

---

## 🚫 CRITICAL WARNING

### Legal Risks
- Facebook/Meta aggressively enforces ToS
- Scraping can result in legal action
- All meaningful data requires authentication
- **DO NOT scrape Facebook without authorization**

### Recommended Alternatives
- **Facebook Graph API** - For authorized developers
- **CrowdTangle** - For researchers
- **Meta Business Suite** - For page owners

---

## 📊 API-Accessible Data (Authorized)

| Data | API Access |
|------|------------|
| Public Pages | Graph API |
| Page Posts | Graph API |
| Page Insights | Graph API (page owner) |
| Ad Library | Public API |

---

## 🔧 Facebook Graph API

```python
import facebook

graph = facebook.GraphAPI(access_token='YOUR_TOKEN')

# Get page info
page = graph.get_object(id='page-id', fields='name,about,fan_count')

# Get page posts
posts = graph.get_connections(id='page-id', connection_name='posts')
```

---

*Part of [02_ant_farms/00_social](../)*
