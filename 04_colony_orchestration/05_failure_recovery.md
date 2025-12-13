# Failure Recovery

> **Building Resilient Scrapers That Handle Failures Gracefully**

Failures are inevitable in web scraping. Sites go down, networks fail, and rate limits trigger. This document covers strategies for handling failures and recovering gracefully.

---

## Types of Failures

```
┌─────────────────────────────────────────────────────────────────┐
│                      FAILURE TAXONOMY                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TRANSIENT (Retry)                                             │
│  ├── Network timeout                                           │
│  ├── Connection reset                                          │
│  ├── 429 Rate limited                                          │
│  ├── 503 Service unavailable                                   │
│  └── 502/504 Gateway errors                                    │
│                                                                 │
│  PERMANENT (Don't retry)                                       │
│  ├── 404 Not found                                             │
│  ├── 403 Forbidden (blocked)                                   │
│  ├── 401 Unauthorized                                          │
│  └── Invalid content/parsing error                             │
│                                                                 │
│  PARTIAL (Retry with modification)                             │
│  ├── CAPTCHA required                                          │
│  ├── Login required                                            │
│  └── Different page structure                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Retry Strategies

### Exponential Backoff

```python
import time
import random
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1, max_delay=60, 
                       exponential_base=2, jitter=True):
    """Decorator for retry with exponential backoff."""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            
            while True:
                try:
                    return func(*args, **kwargs)
                    
                except RetryableError as e:
                    retries += 1
                    
                    if retries > max_retries:
                        raise MaxRetriesExceeded(f"Failed after {max_retries} retries") from e
                    
                    # Calculate delay
                    delay = min(base_delay * (exponential_base ** retries), max_delay)
                    
                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay = delay * (0.5 + random.random())
                    
                    print(f"Retry {retries}/{max_retries} after {delay:.1f}s: {e}")
                    time.sleep(delay)
                    
                except PermanentError:
                    raise  # Don't retry permanent errors
        
        return wrapper
    return decorator

# Define exception types
class RetryableError(Exception):
    """Error that should be retried."""
    pass

class PermanentError(Exception):
    """Error that should not be retried."""
    pass

class MaxRetriesExceeded(Exception):
    """All retries exhausted."""
    pass

# Usage
@retry_with_backoff(max_retries=5, base_delay=2)
def fetch_url(url):
    response = requests.get(url, timeout=30)
    
    if response.status_code == 429:
        raise RetryableError("Rate limited")
    if response.status_code in (502, 503, 504):
        raise RetryableError(f"Server error: {response.status_code}")
    if response.status_code == 404:
        raise PermanentError("Page not found")
    
    return response
```

### Tenacity Library

```python
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, before_sleep_log
)
import logging

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=retry_if_exception_type(RetryableError),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def fetch_with_tenacity(url):
    response = requests.get(url, timeout=30)
    
    if response.status_code == 429:
        # Check for Retry-After header
        retry_after = response.headers.get('Retry-After')
        if retry_after:
            time.sleep(int(retry_after))
        raise RetryableError("Rate limited")
    
    return response
```

---

## 2. Circuit Breaker

Prevent cascading failures by stopping requests to failing services.

```python
from datetime import datetime, timedelta
from enum import Enum
from threading import Lock

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """Circuit breaker pattern implementation."""
    
    def __init__(self, failure_threshold=5, recovery_timeout=60,
                 half_open_max_calls=3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = timedelta(seconds=recovery_timeout)
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = None
        self.half_open_calls = 0
        self.lock = Lock()
    
    def can_execute(self) -> bool:
        """Check if request can proceed."""
        with self.lock:
            if self.state == CircuitState.CLOSED:
                return True
            
            if self.state == CircuitState.OPEN:
                # Check if recovery timeout passed
                if datetime.now() - self.last_failure_time > self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                    return True
                return False
            
            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls < self.half_open_max_calls:
                    self.half_open_calls += 1
                    return True
                return False
        
        return False
    
    def record_success(self):
        """Record successful request."""
        with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
            self.failures = 0
    
    def record_failure(self):
        """Record failed request."""
        with self.lock:
            self.failures += 1
            self.last_failure_time = datetime.now()
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
            elif self.failures >= self.failure_threshold:
                self.state = CircuitState.OPEN

# Per-domain circuit breakers
circuit_breakers = {}

def get_circuit_breaker(domain: str) -> CircuitBreaker:
    if domain not in circuit_breakers:
        circuit_breakers[domain] = CircuitBreaker()
    return circuit_breakers[domain]

def fetch_with_circuit_breaker(url: str):
    domain = urlparse(url).netloc
    cb = get_circuit_breaker(domain)
    
    if not cb.can_execute():
        raise CircuitOpenError(f"Circuit open for {domain}")
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code < 500:
            cb.record_success()
        else:
            cb.record_failure()
        return response
    except Exception as e:
        cb.record_failure()
        raise
```

---

## 3. Checkpoint & Resume

Save progress to resume after crashes.

```python
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Set, Optional

@dataclass
class CrawlCheckpoint:
    """Checkpoint for crawl state."""
    completed_urls: Set[str]
    pending_urls: Set[str]
    failed_urls: dict  # url -> error
    last_url: Optional[str]
    items_scraped: int
    
    def to_dict(self):
        return {
            'completed_urls': list(self.completed_urls),
            'pending_urls': list(self.pending_urls),
            'failed_urls': self.failed_urls,
            'last_url': self.last_url,
            'items_scraped': self.items_scraped
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            completed_urls=set(data['completed_urls']),
            pending_urls=set(data['pending_urls']),
            failed_urls=data['failed_urls'],
            last_url=data['last_url'],
            items_scraped=data['items_scraped']
        )

class CheckpointManager:
    """Manage crawl checkpoints."""
    
    def __init__(self, checkpoint_file: str, save_interval: int = 100):
        self.checkpoint_file = Path(checkpoint_file)
        self.save_interval = save_interval
        self.checkpoint = self._load_or_create()
        self.operations_since_save = 0
    
    def _load_or_create(self) -> CrawlCheckpoint:
        """Load existing checkpoint or create new."""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file) as f:
                data = json.load(f)
                print(f"Resuming from checkpoint: {data['items_scraped']} items scraped")
                return CrawlCheckpoint.from_dict(data)
        
        return CrawlCheckpoint(
            completed_urls=set(),
            pending_urls=set(),
            failed_urls={},
            last_url=None,
            items_scraped=0
        )
    
    def save(self, force: bool = False):
        """Save checkpoint to disk."""
        self.operations_since_save += 1
        
        if force or self.operations_since_save >= self.save_interval:
            with open(self.checkpoint_file, 'w') as f:
                json.dump(self.checkpoint.to_dict(), f)
            self.operations_since_save = 0
    
    def mark_completed(self, url: str):
        """Mark URL as completed."""
        self.checkpoint.completed_urls.add(url)
        self.checkpoint.pending_urls.discard(url)
        self.checkpoint.last_url = url
        self.checkpoint.items_scraped += 1
        self.save()
    
    def mark_failed(self, url: str, error: str):
        """Mark URL as failed."""
        self.checkpoint.failed_urls[url] = error
        self.checkpoint.pending_urls.discard(url)
        self.save()
    
    def add_pending(self, urls: list):
        """Add URLs to pending."""
        for url in urls:
            if url not in self.checkpoint.completed_urls:
                self.checkpoint.pending_urls.add(url)
    
    def get_next_url(self) -> Optional[str]:
        """Get next URL to process."""
        if self.checkpoint.pending_urls:
            return self.checkpoint.pending_urls.pop()
        return None
    
    def is_completed(self, url: str) -> bool:
        """Check if URL already processed."""
        return url in self.checkpoint.completed_urls
    
    def clear(self):
        """Clear checkpoint (start fresh)."""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
        self.checkpoint = CrawlCheckpoint(set(), set(), {}, None, 0)

# Usage
checkpoint = CheckpointManager('crawl_checkpoint.json')

# Add seed URLs (skips already completed)
checkpoint.add_pending(seed_urls)

while True:
    url = checkpoint.get_next_url()
    if not url:
        break
    
    try:
        data = scrape(url)
        save_data(data)
        checkpoint.mark_completed(url)
        
        # Add discovered URLs
        checkpoint.add_pending(data.get('links', []))
        
    except Exception as e:
        checkpoint.mark_failed(url, str(e))

# Final save
checkpoint.save(force=True)
```

---

## 4. Dead Letter Queue

Handle persistently failing items.

```python
class DeadLetterHandler:
    """Handle items that repeatedly fail."""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.retry_counts = {}
        self.dead_letters = []
    
    def should_retry(self, url: str) -> bool:
        """Check if URL should be retried."""
        count = self.retry_counts.get(url, 0)
        return count < self.max_retries
    
    def record_failure(self, url: str, error: str):
        """Record a failure."""
        self.retry_counts[url] = self.retry_counts.get(url, 0) + 1
        
        if not self.should_retry(url):
            self.dead_letters.append({
                'url': url,
                'error': error,
                'attempts': self.retry_counts[url],
                'timestamp': datetime.now().isoformat()
            })
    
    def get_dead_letters(self) -> list:
        """Get all dead letters."""
        return self.dead_letters
    
    def save_dead_letters(self, filepath: str):
        """Save dead letters to file."""
        with open(filepath, 'w') as f:
            json.dump(self.dead_letters, f, indent=2)
    
    def retry_dead_letters(self, scrape_func):
        """Attempt to reprocess dead letters."""
        recovered = []
        still_dead = []
        
        for item in self.dead_letters:
            try:
                scrape_func(item['url'])
                recovered.append(item['url'])
            except Exception as e:
                item['last_error'] = str(e)
                still_dead.append(item)
        
        self.dead_letters = still_dead
        return recovered
```

---

## 5. Graceful Shutdown

```python
import signal
import sys
from threading import Event

class GracefulShutdown:
    """Handle graceful shutdown on signals."""
    
    def __init__(self):
        self.shutdown_event = Event()
        self.checkpoint_manager = None
        
        # Register signal handlers
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
    
    def _handle_signal(self, signum, frame):
        """Handle shutdown signal."""
        print(f"\nReceived signal {signum}, initiating graceful shutdown...")
        self.shutdown_event.set()
    
    def should_stop(self) -> bool:
        """Check if should stop."""
        return self.shutdown_event.is_set()
    
    def set_checkpoint_manager(self, manager: CheckpointManager):
        """Set checkpoint manager for saving on shutdown."""
        self.checkpoint_manager = manager
    
    def run_with_shutdown(self, work_func):
        """Run work function with graceful shutdown."""
        try:
            while not self.should_stop():
                work_func()
        finally:
            print("Saving final checkpoint...")
            if self.checkpoint_manager:
                self.checkpoint_manager.save(force=True)
            print("Shutdown complete")

# Usage
shutdown = GracefulShutdown()
shutdown.set_checkpoint_manager(checkpoint)

def do_work():
    url = checkpoint.get_next_url()
    if url:
        scrape(url)

shutdown.run_with_shutdown(do_work)
```

---

## 6. Health Checks

```python
from datetime import datetime, timedelta

class HealthChecker:
    """Monitor scraper health."""
    
    def __init__(self):
        self.last_success = None
        self.consecutive_failures = 0
        self.total_requests = 0
        self.total_failures = 0
    
    def record_success(self):
        self.last_success = datetime.now()
        self.consecutive_failures = 0
        self.total_requests += 1
    
    def record_failure(self):
        self.consecutive_failures += 1
        self.total_requests += 1
        self.total_failures += 1
    
    def is_healthy(self) -> dict:
        """Check overall health."""
        checks = {}
        
        # Check recent success
        if self.last_success:
            time_since_success = datetime.now() - self.last_success
            checks['recent_success'] = time_since_success < timedelta(minutes=5)
        else:
            checks['recent_success'] = False
        
        # Check consecutive failures
        checks['not_failing'] = self.consecutive_failures < 10
        
        # Check error rate
        if self.total_requests > 0:
            error_rate = self.total_failures / self.total_requests
            checks['error_rate_ok'] = error_rate < 0.1
        else:
            checks['error_rate_ok'] = True
        
        return {
            'healthy': all(checks.values()),
            'checks': checks,
            'stats': {
                'consecutive_failures': self.consecutive_failures,
                'total_requests': self.total_requests,
                'total_failures': self.total_failures
            }
        }
```

---

## Summary

| Strategy | Use Case | Complexity |
|----------|----------|------------|
| Retry + Backoff | Transient errors | Low |
| Circuit Breaker | Cascading failures | Medium |
| Checkpointing | Crash recovery | Medium |
| Dead Letter Queue | Persistent failures | Medium |
| Graceful Shutdown | Clean termination | Low |

---

*This completes the Colony Orchestration section!*
