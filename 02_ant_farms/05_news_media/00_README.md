# 05_news_media

> **News Sites & Article Scrapers**

Scrapers for news articles, blogs, and media content extraction.

---

## 📰 Available Ants

| Ant | Description | Use Case |
|-----|-------------|----------|
| [article_ant.py](article_ant.py) | Generic article extractor | Any news/blog site |
| [rss_ant.py](rss_ant.py) | RSS/Atom feed parser | Content aggregation |

---

## 🎯 Common Use Cases

```
News Scraping Scenarios:
├── Content Aggregation
│   ├── Multi-source news feeds
│   ├── Topic monitoring
│   └── Competitive content tracking
│
├── Media Monitoring
│   ├── Brand mentions
│   ├── Industry news
│   └── PR tracking
│
├── Research
│   ├── Historical archives
│   ├── Sentiment analysis
│   └── Trend detection
│
└── Content Analysis
    ├── Author tracking
    ├── Topic categorization
    └── Publication patterns
```

---

## ⚠️ Important Considerations

### Copyright & Fair Use

- **Headlines/titles**: Generally okay to use
- **Full article text**: Likely copyright infringement
- **Excerpts**: May be fair use (context dependent)
- **Recommendation**: Use for indexing/analysis, not republishing

### Paywalls

```python
# Common paywall indicators
paywall_patterns = [
    'subscribe to continue',
    'premium content',
    'members only',
    'paywall',
    'subscription required',
]

# Check before extracting
if any(p in content.lower() for p in paywall_patterns):
    # Only partial content available
    pass
```

### Rate Limits

| Site Type | Recommended Rate |
|-----------|------------------|
| Major news (CNN, BBC) | 1 req/3 sec |
| Local news | 1 req/5 sec |
| Blogs | 1 req/2 sec |
| News APIs | Per API limits |

---

## 📊 Standard Article Schema

```python
ARTICLE_SCHEMA = {
    'title': str,
    'author': str,
    'published_date': str,
    'modified_date': str,
    'content': str,
    'excerpt': str,
    'url': str,
    'source': str,
    'categories': list,
    'tags': list,
    'images': list,
    'word_count': int,
}
```

---

*Part of [02_ant_farms](../) - Site-specific scraper collections*
