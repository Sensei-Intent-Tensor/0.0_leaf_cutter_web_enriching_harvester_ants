# Twitter/X Scraper

> **Social Media Data from X (formerly Twitter)**

X is a major social platform for real-time information and public discourse.

---

## ⚠️ Important Considerations

### Legal & Technical
- X has official API (paid tiers)
- Aggressive anti-scraping
- Requires authentication for most data
- Rate limits enforced

### Recommended Approach
- Use X API v2 for production
- Free tier: 1,500 tweets/month read
- Basic tier: $100/month
- Pro tier: $5,000/month

---

## 📊 Data Available via API

| Endpoint | Data |
|----------|------|
| Tweets | Text, media, metrics |
| Users | Profile, followers |
| Spaces | Audio conversations |
| Lists | Curated collections |

---

## 🔧 Official X API

```python
import tweepy

client = tweepy.Client(
    bearer_token="YOUR_BEARER_TOKEN",
    consumer_key="API_KEY",
    consumer_secret="API_SECRET",
    access_token="ACCESS_TOKEN",
    access_token_secret="ACCESS_SECRET"
)

# Search tweets
tweets = client.search_recent_tweets(
    query="python programming",
    max_results=100
)
```

---

*Part of [02_ant_farms/00_social](../)*
