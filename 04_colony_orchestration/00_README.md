# 04_colony_orchestration

> **Running Scrapers at Scale**

Moving from a single script to a production scraping operation requires orchestration - scheduling, queuing, distributing work, monitoring, and handling failures.

---

## 📚 Documents in This Section

| # | Document | Lines | Description |
|---|----------|-------|-------------|
| 01 | [Scheduling](01_scheduling.md) | 422 | When and how often to run scrapers |
| 02 | [Queue Management](02_queue_management.md) | 455 | Managing job queues and priorities |
| 03 | [Distributed Crawling](03_distributed_crawling.md) | 484 | Scaling across multiple machines |
| 04 | [Monitoring & Logging](04_monitoring_logging.md) | 510 | Observability and alerting |
| 05 | [Failure Recovery](05_failure_recovery.md) | 561 | Handling failures gracefully |

**Total: ~2,432 lines of orchestration guidance**

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATION LAYER                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────────┐ │
│  │  SCHEDULER  │───▶│    QUEUE    │───▶│         WORKERS             │ │
│  │             │    │             │    │  ┌───┐ ┌───┐ ┌───┐ ┌───┐   │ │
│  │ Cron/Timer  │    │ Redis/RMQ   │    │  │ W │ │ W │ │ W │ │ W │   │ │
│  └─────────────┘    └─────────────┘    │  └───┘ └───┘ └───┘ └───┘   │ │
│                                        └─────────────────────────────┘ │
│                                                     │                   │
│                           ┌─────────────────────────┘                   │
│                           ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      SHARED INFRASTRUCTURE                       │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │   │
│  │  │  Redis   │  │ Database │  │  Metrics │  │     Logs         │ │   │
│  │  │(frontier)│  │ (results)│  │(Prometheus)│ │(Elasticsearch)   │ │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Quick Reference

### Scheduling

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()
scheduler.add_job(scrape_products, CronTrigger(hour=9))  # Daily at 9 AM
scheduler.start()
```

### Queue Management

```python
from celery import Celery

app = Celery('scraper', broker='redis://localhost:6379')

@app.task(bind=True, max_retries=3)
def scrape_url(self, url):
    try:
        return do_scrape(url)
    except TransientError as e:
        raise self.retry(exc=e)
```

### Distributed Frontier

```python
class DistributedFrontier:
    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)
    
    def add_url(self, url, priority=5):
        if not self.redis.sismember('seen', url):
            self.redis.sadd('seen', url)
            self.redis.zadd('pending', {url: priority})
```

### Retry with Backoff

```python
@retry(stop=stop_after_attempt(3),
       wait=wait_exponential(min=1, max=60))
def fetch(url):
    response = requests.get(url)
    if response.status_code == 429:
        raise RetryableError()
    return response
```

---

## 📊 Choosing Your Stack

| Scale | Scheduler | Queue | Workers | Monitoring |
|-------|-----------|-------|---------|------------|
| **Small** | APScheduler | In-memory | Threads | Logging |
| **Medium** | Celery Beat | Redis | Celery | Prometheus |
| **Large** | Airflow | RabbitMQ | Kubernetes | Grafana + ELK |
| **Enterprise** | Custom | Kafka | Auto-scaling | Full observability |

---

## 🔄 Orchestration Patterns

### Pattern 1: Simple Cron Job
```
Cron → Script → Database
```
Best for: Low-volume, single site

### Pattern 2: Queue-Based
```
Scheduler → Queue → Workers → Database
```
Best for: Medium volume, multiple sites

### Pattern 3: Distributed Frontier
```
Frontier ←→ Workers ←→ Results Store
    ↑           ↓
    └── New URLs ──┘
```
Best for: Large-scale crawling

---

## ⚠️ Key Considerations

| Factor | Small Scale | Large Scale |
|--------|-------------|-------------|
| **Scheduling** | Cron/APScheduler | Distributed scheduler |
| **Queue** | In-memory | Redis/RabbitMQ |
| **Deduplication** | Set in memory | Redis/Bloom filter |
| **Rate Limiting** | Per-process | Distributed (Redis) |
| **Checkpointing** | File-based | Database |
| **Monitoring** | Logs | Metrics + Alerts |

---

## 🔗 Related Sections

- **[00_foundations/](../00_foundations/)** - Core concepts
- **[01_ant_anatomy/](../01_ant_anatomy/)** - Scraper structure
- **[03_enrichment_pipelines/](../03_enrichment_pipelines/)** - Data processing

---

*Part of the [Leaf Cutter Web Enriching Harvester Ants](../) framework*
