# 06_utils

> **Reusable Utility Modules**

Core utility modules that power the Harvester Ants framework. These provide HTTP handling, parsing, rate limiting, proxy management, and output writing.

---

## 📁 Modules

| Module | Purpose |
|--------|---------|
| `http_client.py` | HTTP requests with retry, sessions, and stealth |
| `parsers.py` | HTML/JSON parsing utilities |
| `rate_limiter.py` | Request rate limiting |
| `proxy_manager.py` | Proxy rotation and management |
| `output_writer.py` | Write data to various formats |

---

## 🚀 Quick Usage

```python
from utils import HttpClient, RateLimiter, ProxyManager, OutputWriter

# Setup
client = HttpClient()
limiter = RateLimiter(requests_per_second=2)
proxies = ProxyManager(['http://proxy1:8080', 'http://proxy2:8080'])
writer = OutputWriter('output.jsonl')

# Scrape with rate limiting
for url in urls:
    limiter.wait()
    response = client.get(url, proxy=proxies.get_next())
    data = parse_response(response)
    writer.write(data)

writer.close()
```

---

## 📦 Installation

These utilities require:

```
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
aiohttp>=3.8.0  # For async support
```

---

*Part of the [Leaf Cutter Web Enriching Harvester Ants](../) framework*
