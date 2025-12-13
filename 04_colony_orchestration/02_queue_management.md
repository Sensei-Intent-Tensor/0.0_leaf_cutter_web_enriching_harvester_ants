# Queue Management

> **Organizing and Prioritizing Scrape Jobs**

Queues decouple job submission from execution, enabling better resource management, retry handling, and scalability.

---

## Queue Architecture

```
┌─────────────┐     ┌─────────────────────────────────────┐     ┌─────────────┐
│  PRODUCERS  │────▶│              QUEUE                  │────▶│  WORKERS    │
│             │     │                                     │     │             │
│ Scheduler   │     │  ┌─────┬─────┬─────┬─────┬─────┐   │     │ Worker 1    │
│ API         │     │  │ Job │ Job │ Job │ Job │ Job │   │     │ Worker 2    │
│ Triggers    │     │  └─────┴─────┴─────┴─────┴─────┘   │     │ Worker N    │
└─────────────┘     └─────────────────────────────────────┘     └─────────────┘
```

---

## 1. Simple In-Memory Queue

```python
from queue import Queue, PriorityQueue
from threading import Thread
from dataclasses import dataclass, field
from typing import Any
import time

@dataclass(order=True)
class PrioritizedJob:
    priority: int
    job: Any = field(compare=False)

class SimpleJobQueue:
    """Simple thread-safe job queue."""
    
    def __init__(self, num_workers: int = 4):
        self.queue = PriorityQueue()
        self.workers = []
        self.running = False
        self.num_workers = num_workers
    
    def add_job(self, job, priority: int = 5):
        """Add job to queue. Lower priority = executed first."""
        self.queue.put(PrioritizedJob(priority, job))
    
    def _worker(self, worker_id: int):
        """Worker thread that processes jobs."""
        while self.running:
            try:
                item = self.queue.get(timeout=1)
                print(f"Worker {worker_id} processing: {item.job}")
                try:
                    item.job()
                except Exception as e:
                    print(f"Job failed: {e}")
                finally:
                    self.queue.task_done()
            except:
                continue
    
    def start(self):
        """Start worker threads."""
        self.running = True
        for i in range(self.num_workers):
            t = Thread(target=self._worker, args=(i,), daemon=True)
            t.start()
            self.workers.append(t)
    
    def stop(self):
        """Stop all workers."""
        self.running = False
        for w in self.workers:
            w.join(timeout=5)
    
    def wait(self):
        """Wait for all jobs to complete."""
        self.queue.join()

# Usage
queue = SimpleJobQueue(num_workers=4)
queue.start()

queue.add_job(lambda: scrape('https://site1.com'), priority=1)
queue.add_job(lambda: scrape('https://site2.com'), priority=5)
queue.add_job(lambda: scrape('https://site3.com'), priority=3)

queue.wait()
queue.stop()
```

---

## 2. Redis-Based Queue

```python
import redis
import json
import uuid
from datetime import datetime
from typing import Optional

class RedisJobQueue:
    """Distributed job queue using Redis."""
    
    def __init__(self, redis_url: str = 'redis://localhost:6379', 
                 queue_name: str = 'scrape_jobs'):
        self.redis = redis.from_url(redis_url)
        self.queue_name = queue_name
        self.processing_queue = f"{queue_name}:processing"
        self.failed_queue = f"{queue_name}:failed"
    
    def enqueue(self, job_type: str, payload: dict, priority: int = 5) -> str:
        """Add job to queue."""
        job_id = str(uuid.uuid4())
        job = {
            'id': job_id,
            'type': job_type,
            'payload': payload,
            'priority': priority,
            'created_at': datetime.now().isoformat(),
            'attempts': 0
        }
        
        # Use sorted set for priority queue
        self.redis.zadd(self.queue_name, {json.dumps(job): priority})
        return job_id
    
    def dequeue(self, timeout: int = 0) -> Optional[dict]:
        """Get next job from queue."""
        # Get highest priority (lowest score)
        result = self.redis.bzpopmin(self.queue_name, timeout)
        
        if result:
            _, job_data, _ = result
            job = json.loads(job_data)
            
            # Move to processing queue
            job['started_at'] = datetime.now().isoformat()
            self.redis.hset(self.processing_queue, job['id'], json.dumps(job))
            
            return job
        return None
    
    def complete(self, job_id: str):
        """Mark job as completed."""
        self.redis.hdel(self.processing_queue, job_id)
    
    def fail(self, job_id: str, error: str, retry: bool = True):
        """Mark job as failed."""
        job_data = self.redis.hget(self.processing_queue, job_id)
        if job_data:
            job = json.loads(job_data)
            job['error'] = error
            job['failed_at'] = datetime.now().isoformat()
            job['attempts'] += 1
            
            self.redis.hdel(self.processing_queue, job_id)
            
            if retry and job['attempts'] < 3:
                # Re-queue with lower priority
                job['priority'] += 1
                self.redis.zadd(self.queue_name, {json.dumps(job): job['priority']})
            else:
                # Move to failed queue
                self.redis.lpush(self.failed_queue, json.dumps(job))
    
    def get_stats(self) -> dict:
        """Get queue statistics."""
        return {
            'pending': self.redis.zcard(self.queue_name),
            'processing': self.redis.hlen(self.processing_queue),
            'failed': self.redis.llen(self.failed_queue)
        }

# Worker
def run_worker(queue: RedisJobQueue):
    handlers = {
        'scrape_url': scrape_url_handler,
        'scrape_site': scrape_site_handler,
    }
    
    while True:
        job = queue.dequeue(timeout=5)
        if job:
            handler = handlers.get(job['type'])
            if handler:
                try:
                    handler(job['payload'])
                    queue.complete(job['id'])
                except Exception as e:
                    queue.fail(job['id'], str(e))
```

---

## 3. Celery Task Queue

```python
from celery import Celery, chain, group
from celery.exceptions import MaxRetriesExceededError

app = Celery('scraper', broker='redis://localhost:6379')

app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    task_acks_late=True,  # Acknowledge after completion
    worker_prefetch_multiplier=1,  # One task at a time per worker
    task_reject_on_worker_lost=True,
)

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def scrape_url(self, url: str, config: dict = None):
    """Scrape a single URL."""
    try:
        result = do_scrape(url, config)
        return {'url': url, 'data': result}
    except TransientError as e:
        # Retry on transient errors
        raise self.retry(exc=e)
    except Exception as e:
        # Don't retry on permanent errors
        return {'url': url, 'error': str(e)}

@app.task
def process_results(results: list):
    """Process scraping results."""
    for result in results:
        if 'error' not in result:
            save_to_database(result['data'])

# Chain tasks
workflow = chain(
    scrape_url.s('https://example.com'),
    process_results.s()
)
workflow.delay()

# Parallel scraping
urls = ['https://site1.com', 'https://site2.com', 'https://site3.com']
job = group(scrape_url.s(url) for url in urls)
result = job.apply_async()

# With callback
chord = group(scrape_url.s(url) for url in urls) | process_results.s()
chord.delay()
```

---

## 4. Rate-Limited Queue

```python
import time
from collections import defaultdict
from threading import Lock

class RateLimitedQueue:
    """Queue with per-domain rate limiting."""
    
    def __init__(self, default_rate: float = 1.0):
        self.queues = defaultdict(list)  # domain -> [jobs]
        self.last_request = defaultdict(float)  # domain -> timestamp
        self.rates = {}  # domain -> requests per second
        self.default_rate = default_rate
        self.lock = Lock()
    
    def set_rate(self, domain: str, rate: float):
        """Set rate limit for domain."""
        self.rates[domain] = rate
    
    def _get_domain(self, url: str) -> str:
        from urllib.parse import urlparse
        return urlparse(url).netloc
    
    def enqueue(self, url: str, job: callable):
        """Add job for URL."""
        domain = self._get_domain(url)
        with self.lock:
            self.queues[domain].append((url, job))
    
    def get_next_job(self) -> Optional[tuple]:
        """Get next job respecting rate limits."""
        now = time.time()
        
        with self.lock:
            for domain, jobs in self.queues.items():
                if not jobs:
                    continue
                
                rate = self.rates.get(domain, self.default_rate)
                min_interval = 1.0 / rate
                
                time_since_last = now - self.last_request[domain]
                if time_since_last >= min_interval:
                    url, job = jobs.pop(0)
                    self.last_request[domain] = now
                    return (url, job, domain)
        
        return None
    
    def run(self, num_workers: int = 4):
        """Run queue with workers."""
        from concurrent.futures import ThreadPoolExecutor
        
        def worker():
            while True:
                item = self.get_next_job()
                if item:
                    url, job, domain = item
                    try:
                        job()
                    except Exception as e:
                        print(f"Job failed for {url}: {e}")
                else:
                    time.sleep(0.1)  # Small sleep when no jobs ready
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            for _ in range(num_workers):
                executor.submit(worker)

# Usage
queue = RateLimitedQueue(default_rate=0.5)  # 1 request per 2 seconds
queue.set_rate('api.example.com', 2.0)  # 2 requests per second for this domain

for url in urls:
    queue.enqueue(url, lambda u=url: scrape(u))

queue.run()
```

---

## 5. Dead Letter Queue

Handle persistently failing jobs.

```python
class DeadLetterQueue:
    """Handle jobs that repeatedly fail."""
    
    def __init__(self, redis_url: str, max_retries: int = 3):
        self.redis = redis.from_url(redis_url)
        self.max_retries = max_retries
        self.dlq_name = 'dead_letter_queue'
    
    def should_retry(self, job: dict) -> bool:
        """Check if job should be retried."""
        return job.get('attempts', 0) < self.max_retries
    
    def send_to_dlq(self, job: dict, error: str):
        """Send job to dead letter queue."""
        job['dlq_reason'] = error
        job['dlq_timestamp'] = datetime.now().isoformat()
        self.redis.lpush(self.dlq_name, json.dumps(job))
    
    def get_dlq_jobs(self, limit: int = 100) -> list:
        """Get jobs from DLQ for inspection."""
        jobs = self.redis.lrange(self.dlq_name, 0, limit - 1)
        return [json.loads(j) for j in jobs]
    
    def reprocess_dlq(self, main_queue: RedisJobQueue):
        """Move DLQ jobs back to main queue."""
        while True:
            job_data = self.redis.rpop(self.dlq_name)
            if not job_data:
                break
            
            job = json.loads(job_data)
            job['attempts'] = 0  # Reset attempts
            del job['dlq_reason']
            del job['dlq_timestamp']
            
            main_queue.enqueue(job['type'], job['payload'])
```

---

## 6. Queue Monitoring

```python
import time
from dataclasses import dataclass
from typing import Dict

@dataclass
class QueueMetrics:
    pending: int
    processing: int
    completed: int
    failed: int
    throughput: float  # jobs per second
    avg_processing_time: float

class QueueMonitor:
    """Monitor queue health and performance."""
    
    def __init__(self, queue):
        self.queue = queue
        self.completed_count = 0
        self.total_processing_time = 0
        self.start_time = time.time()
    
    def record_completion(self, processing_time: float):
        """Record job completion."""
        self.completed_count += 1
        self.total_processing_time += processing_time
    
    def get_metrics(self) -> QueueMetrics:
        """Get current metrics."""
        stats = self.queue.get_stats()
        elapsed = time.time() - self.start_time
        
        return QueueMetrics(
            pending=stats['pending'],
            processing=stats['processing'],
            completed=self.completed_count,
            failed=stats['failed'],
            throughput=self.completed_count / elapsed if elapsed > 0 else 0,
            avg_processing_time=self.total_processing_time / self.completed_count 
                if self.completed_count > 0 else 0
        )
    
    def is_healthy(self) -> bool:
        """Check if queue is healthy."""
        metrics = self.get_metrics()
        
        # Alert conditions
        if metrics.pending > 10000:
            return False  # Queue backing up
        if metrics.failed > metrics.completed * 0.1:
            return False  # High failure rate
        
        return True
```

---

## Summary

| Queue Type | Best For | Persistence | Distributed |
|------------|----------|-------------|-------------|
| In-Memory | Simple scripts | No | No |
| Redis | Medium scale | Yes | Yes |
| Celery | Production | Yes | Yes |
| RabbitMQ | Complex workflows | Yes | Yes |

---

*Next: [03_distributed_crawling.md](03_distributed_crawling.md) - Scaling across multiple machines*
