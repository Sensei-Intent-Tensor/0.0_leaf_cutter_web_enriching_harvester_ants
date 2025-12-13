# Distributed Crawling

> **Scaling Across Multiple Machines**

When a single machine isn't enough, distribute your crawling across multiple workers for higher throughput and resilience.

---

## Architecture Patterns

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DISTRIBUTED ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  COORDINATOR (Master)                                               │
│  ├── URL Frontier (discovered URLs)                                │
│  ├── Job Scheduler (assigns work)                                   │
│  └── Result Aggregator (collects data)                             │
│                                                                     │
│            ┌──────────────┬──────────────┬──────────────┐          │
│            ▼              ▼              ▼              ▼          │
│       ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐       │
│       │ Worker  │   │ Worker  │   │ Worker  │   │ Worker  │       │
│       │   1     │   │   2     │   │   3     │   │   N     │       │
│       └─────────┘   └─────────┘   └─────────┘   └─────────┘       │
│                                                                     │
│  SHARED STATE                                                       │
│  ├── Redis (URL dedup, rate limits, coordination)                  │
│  ├── Database (results storage)                                    │
│  └── Message Queue (job distribution)                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. URL Frontier

Central management of URLs to crawl.

```python
import redis
import json
from typing import Optional, Set
from urllib.parse import urlparse

class DistributedFrontier:
    """Distributed URL frontier using Redis."""
    
    def __init__(self, redis_url: str = 'redis://localhost:6379'):
        self.redis = redis.from_url(redis_url)
        self.pending_key = 'frontier:pending'
        self.seen_key = 'frontier:seen'
        self.domain_queues_prefix = 'frontier:domain:'
    
    def add_url(self, url: str, priority: int = 5) -> bool:
        """Add URL to frontier if not seen."""
        # Check if already seen
        if self.redis.sismember(self.seen_key, url):
            return False
        
        # Mark as seen
        self.redis.sadd(self.seen_key, url)
        
        # Add to domain-specific queue for politeness
        domain = urlparse(url).netloc
        self.redis.zadd(
            f"{self.domain_queues_prefix}{domain}",
            {url: priority}
        )
        
        # Track active domains
        self.redis.sadd('frontier:domains', domain)
        
        return True
    
    def add_urls(self, urls: list, priority: int = 5) -> int:
        """Add multiple URLs, return count added."""
        added = 0
        for url in urls:
            if self.add_url(url, priority):
                added += 1
        return added
    
    def get_url(self, worker_id: str) -> Optional[str]:
        """Get next URL for worker, respecting politeness."""
        # Get all active domains
        domains = self.redis.smembers('frontier:domains')
        
        for domain in domains:
            domain = domain.decode() if isinstance(domain, bytes) else domain
            
            # Check rate limit for domain
            if self._is_rate_limited(domain):
                continue
            
            # Try to get URL from this domain
            queue_key = f"{self.domain_queues_prefix}{domain}"
            result = self.redis.zpopmin(queue_key)
            
            if result:
                url = result[0][0]
                url = url.decode() if isinstance(url, bytes) else url
                
                # Record access time for rate limiting
                self._record_access(domain)
                
                return url
        
        return None
    
    def _is_rate_limited(self, domain: str) -> bool:
        """Check if domain is rate limited."""
        last_access = self.redis.get(f"frontier:last_access:{domain}")
        if last_access:
            import time
            elapsed = time.time() - float(last_access)
            min_delay = float(self.redis.get(f"frontier:delay:{domain}") or 1.0)
            return elapsed < min_delay
        return False
    
    def _record_access(self, domain: str):
        """Record domain access time."""
        import time
        self.redis.set(f"frontier:last_access:{domain}", time.time())
    
    def set_domain_delay(self, domain: str, delay: float):
        """Set crawl delay for domain."""
        self.redis.set(f"frontier:delay:{domain}", delay)
    
    def get_stats(self) -> dict:
        """Get frontier statistics."""
        domains = self.redis.smembers('frontier:domains')
        pending = 0
        for domain in domains:
            domain = domain.decode() if isinstance(domain, bytes) else domain
            pending += self.redis.zcard(f"{self.domain_queues_prefix}{domain}")
        
        return {
            'pending': pending,
            'seen': self.redis.scard(self.seen_key),
            'domains': len(domains)
        }
```

---

## 2. Worker Implementation

```python
import os
import signal
import time
from threading import Event

class CrawlWorker:
    """Distributed crawl worker."""
    
    def __init__(self, worker_id: str, frontier: DistributedFrontier,
                 result_queue, config: dict = None):
        self.worker_id = worker_id
        self.frontier = frontier
        self.result_queue = result_queue
        self.config = config or {}
        self.shutdown_event = Event()
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)
    
    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signal."""
        print(f"Worker {self.worker_id} shutting down...")
        self.shutdown_event.set()
    
    def run(self):
        """Main worker loop."""
        print(f"Worker {self.worker_id} starting...")
        
        while not self.shutdown_event.is_set():
            # Get URL from frontier
            url = self.frontier.get_url(self.worker_id)
            
            if not url:
                time.sleep(1)  # No URLs available, wait
                continue
            
            # Process URL
            try:
                result = self._process_url(url)
                
                # Submit result
                self.result_queue.put({
                    'worker_id': self.worker_id,
                    'url': url,
                    'data': result.get('data'),
                    'links': result.get('links', [])
                })
                
                # Add discovered links to frontier
                if result.get('links'):
                    self.frontier.add_urls(result['links'])
                    
            except Exception as e:
                self.result_queue.put({
                    'worker_id': self.worker_id,
                    'url': url,
                    'error': str(e)
                })
        
        print(f"Worker {self.worker_id} stopped")
    
    def _process_url(self, url: str) -> dict:
        """Scrape URL and extract data."""
        import requests
        from bs4 import BeautifulSoup
        
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Extract data (customize per use case)
        data = {
            'title': soup.title.string if soup.title else None,
            'text': soup.get_text()[:1000]
        }
        
        # Extract links
        links = []
        for a in soup.find_all('a', href=True):
            link = a['href']
            if link.startswith('http'):
                links.append(link)
        
        return {'data': data, 'links': links}
```

---

## 3. Scrapy Distributed Setup

Using Scrapy with scrapy-redis for distribution.

```python
# settings.py
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

REDIS_URL = 'redis://localhost:6379'

# Allow pause/resume
SCHEDULER_PERSIST = True

# Queue type (priority queue recommended)
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'

# spider.py
from scrapy_redis.spiders import RedisSpider

class DistributedSpider(RedisSpider):
    name = 'distributed'
    redis_key = 'distributed:start_urls'
    
    def parse(self, response):
        # Your parsing logic
        yield {
            'url': response.url,
            'title': response.css('title::text').get()
        }
        
        # Follow links
        for href in response.css('a::attr(href)').getall():
            yield response.follow(href, self.parse)

# Run multiple workers:
# Worker 1: scrapy crawl distributed
# Worker 2: scrapy crawl distributed
# Worker N: scrapy crawl distributed

# Add start URLs:
# redis-cli lpush distributed:start_urls https://example.com
```

---

## 4. Coordinator Pattern

```python
from multiprocessing import Process, Queue
import time

class CrawlCoordinator:
    """Coordinates distributed crawling."""
    
    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self.frontier = DistributedFrontier()
        self.result_queue = Queue()
        self.workers = []
    
    def add_seeds(self, urls: list):
        """Add seed URLs to start crawling."""
        self.frontier.add_urls(urls, priority=1)
    
    def start(self):
        """Start all workers."""
        for i in range(self.num_workers):
            worker = CrawlWorker(
                worker_id=f"worker-{i}",
                frontier=self.frontier,
                result_queue=self.result_queue
            )
            p = Process(target=worker.run)
            p.start()
            self.workers.append(p)
        
        # Start result processor
        self._process_results()
    
    def _process_results(self):
        """Process results from workers."""
        while True:
            try:
                result = self.result_queue.get(timeout=5)
                
                if 'error' in result:
                    print(f"Error from {result['worker_id']}: {result['error']}")
                else:
                    self._save_result(result)
                    
            except:
                # Check if any workers still alive
                alive = any(w.is_alive() for w in self.workers)
                if not alive:
                    break
    
    def _save_result(self, result: dict):
        """Save crawl result."""
        # Implement your storage logic
        print(f"Saved: {result['url']}")
    
    def stop(self):
        """Stop all workers."""
        for worker in self.workers:
            worker.terminate()
            worker.join(timeout=5)
    
    def get_stats(self) -> dict:
        """Get crawl statistics."""
        frontier_stats = self.frontier.get_stats()
        return {
            **frontier_stats,
            'workers_alive': sum(1 for w in self.workers if w.is_alive())
        }

# Usage
coordinator = CrawlCoordinator(num_workers=8)
coordinator.add_seeds([
    'https://example.com',
    'https://other-site.com'
])
coordinator.start()
```

---

## 5. Domain Sharding

Assign domains to specific workers for better politeness.

```python
import hashlib

class ShardedFrontier:
    """Frontier that shards domains across workers."""
    
    def __init__(self, num_shards: int):
        self.num_shards = num_shards
        self.frontiers = [DistributedFrontier() for _ in range(num_shards)]
    
    def _get_shard(self, url: str) -> int:
        """Get shard for URL based on domain."""
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        return int(hashlib.md5(domain.encode()).hexdigest(), 16) % self.num_shards
    
    def add_url(self, url: str, priority: int = 5):
        """Add URL to appropriate shard."""
        shard = self._get_shard(url)
        self.frontiers[shard].add_url(url, priority)
    
    def get_url(self, worker_id: int) -> Optional[str]:
        """Get URL for worker's shard."""
        shard = worker_id % self.num_shards
        return self.frontiers[shard].get_url(str(worker_id))

# Usage - each worker handles specific domains
class ShardedWorker(CrawlWorker):
    def __init__(self, worker_id: int, frontier: ShardedFrontier, **kwargs):
        super().__init__(str(worker_id), frontier, **kwargs)
        self.shard_id = worker_id
    
    def run(self):
        while not self.shutdown_event.is_set():
            # Only get URLs from my shard
            url = self.frontier.get_url(self.shard_id)
            if url:
                self._process_url(url)
```

---

## 6. Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scraper-workers
spec:
  replicas: 10  # Scale workers
  selector:
    matchLabels:
      app: scraper-worker
  template:
    metadata:
      labels:
        app: scraper-worker
    spec:
      containers:
      - name: worker
        image: scraper:latest
        env:
        - name: REDIS_URL
          value: "redis://redis:6379"
        - name: WORKER_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: scraper-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: scraper-workers
  minReplicas: 2
  maxReplicas: 50
  metrics:
  - type: External
    external:
      metric:
        name: redis_queue_length
      target:
        type: Value
        value: 1000
```

---

## Summary

| Pattern | Scale | Complexity | Best For |
|---------|-------|------------|----------|
| Single Machine Multithread | Low | Low | Small crawls |
| Redis + Workers | Medium | Medium | Medium scale |
| Scrapy-Redis | Medium-High | Medium | Scrapy users |
| Kubernetes | High | High | Enterprise |
| Domain Sharding | High | High | Politeness-critical |

---

*Next: [04_monitoring_logging.md](04_monitoring_logging.md) - Observability for your crawlers*
