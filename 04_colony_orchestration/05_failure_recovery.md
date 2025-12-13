# Failure Recovery

> **Building Resilient Scraping Systems**

Failures are inevitable. Networks drop, sites go down, HTML changes, and rate limits hit. This document covers strategies for graceful failure handling and recovery.

---

## Failure Types

```
┌─────────────────────────────────────────────────────────────────┐
│                      FAILURE TAXONOMY                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TRANSIENT (Retry usually works)                               │
│  ├── Network timeout                                           │
│  ├── 429 Rate limited                                          │
│  ├── 503 Service unavailable                                   │
│  └── Connection reset                                          │
│                                                                 │
│  PERMANENT (Retry won't help)                                  │
│  ├── 404 Not found                                             │
│  ├── 410 Gone                                                  │
│  ├── 401/403 Auth required                                     │
│  └── Invalid URL                                               │
│                                                                 │
│  STRUCTURAL (Site changed)                                     │
│  ├── Selector not found                                        │
│  ├── Unexpected data format                                    │
│  └── New anti-bot measures                                     │
│                                                                 │
│  SYSTEM (Infrastructure issues)                                │
│  ├── Out of memory                                             │
│  ├── Disk full                                                 │
│  ├── Database connection lost                                  │
│  └── Worker crash                                              │
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
from typing import Tuple, Type

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Decorator for retry with exponential backoff."""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        raise
                    
                    # Calculate delay
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay = delay * (0.5 + random.random())
                    
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s")
                    time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator

# Usage
@retry_with_backoff(
    max_retries=3,
    base_delay=1.0,
    retryable_exceptions=(requests.exceptions.Timeout, requests.exceptions.ConnectionError)
)
def fetch_url(url: str):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response
```

### Status Code Aware Retry

```python
from dataclasses import dataclass
from typing import Set

@dataclass
class RetryPolicy:
    """Retry policy based on status codes."""
    retryable_codes: Set[int] = None
    permanent_failure_codes: Set[int] = None
    max_retries: int = 3
    
    def __post_init__(self):
        self.retryable_codes = self.retryable_codes or {429, 500, 502, 503, 504}
        self.permanent_failure_codes = self.permanent_failure_codes or {400, 401, 403, 404, 410}
    
    def should_retry(self, status_code: int, attempt: int) -> bool:
        if attempt >= self.max_retries:
            return False
        if status_code in self.permanent_failure_codes:
            return False
        return status_code in self.retryable_codes
    
    def get_retry_delay(self, status_code: int, attempt: int, 
                        response_headers: dict = None) -> float:
        # Respect Retry-After header
        if response_headers and 'Retry-After' in response_headers:
            try:
                return float(response_headers['Retry-After'])
            except ValueError:
                pass
        
        # Longer delay for rate limiting
        if status_code == 429:
            return min(30 * (2 ** attempt), 300)
        
        # Standard exponential backoff
        return min(1 * (2 ** attempt), 60)

def fetch_with_policy(url: str, policy: RetryPolicy = None):
    """Fetch URL with retry policy."""
    policy = policy or RetryPolicy()
    
    for attempt in range(policy.max_retries + 1):
        try:
            response = requests.get(url, timeout=30)
            
            if response.ok:
                return response
            
            if not policy.should_retry(response.status_code, attempt):
                response.raise_for_status()
            
            delay = policy.get_retry_delay(
                response.status_code, 
                attempt,
                dict(response.headers)
            )
            time.sleep(delay)
            
        except requests.exceptions.RequestException as e:
            if attempt == policy.max_retries:
                raise
            time.sleep(policy.get_retry_delay(0, attempt))
    
    raise Exception(f"Max retries exceeded for {url}")
```

---

## 2. Circuit Breaker

Prevent cascading failures by stopping requests to failing services.

```python
from enum import Enum
from datetime import datetime, timedelta
from threading import Lock

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """Circuit breaker pattern implementation."""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: float = 30.0,
                 half_open_max_calls: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0
        self._lock = Lock()
    
    def can_execute(self) -> bool:
        """Check if request can proceed."""
        with self._lock:
            if self.state == CircuitState.CLOSED:
                return True
            
            if self.state == CircuitState.OPEN:
                # Check if recovery timeout passed
                if self._recovery_timeout_passed():
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
        with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.half_open_max_calls:
                    self._reset()
            else:
                self.failure_count = 0
    
    def record_failure(self):
        """Record failed request."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.state == CircuitState.HALF_OPEN:
                self._trip()
            elif self.failure_count >= self.failure_threshold:
                self._trip()
    
    def _trip(self):
        """Trip the circuit breaker."""
        self.state = CircuitState.OPEN
        self.success_count = 0
    
    def _reset(self):
        """Reset the circuit breaker."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
    
    def _recovery_timeout_passed(self) -> bool:
        if self.last_failure_time is None:
            return True
        return datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)

# Usage with per-domain circuit breakers
class DomainCircuitBreakers:
    def __init__(self):
        self.breakers = {}
        self._lock = Lock()
    
    def get_breaker(self, domain: str) -> CircuitBreaker:
        with self._lock:
            if domain not in self.breakers:
                self.breakers[domain] = CircuitBreaker()
            return self.breakers[domain]

breakers = DomainCircuitBreakers()

def fetch_with_circuit_breaker(url: str):
    domain = urlparse(url).netloc
    breaker = breakers.get_breaker(domain)
    
    if not breaker.can_execute():
        raise Exception(f"Circuit open for {domain}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        breaker.record_success()
        return response
    except Exception as e:
        breaker.record_failure()
        raise
```

---

## 3. Checkpointing

Save progress to resume after failures.

```python
import json
from pathlib import Path
from datetime import datetime
from typing import Set, Optional

class Checkpoint:
    """Save and restore crawl progress."""
    
    def __init__(self, checkpoint_file: str = 'checkpoint.json'):
        self.checkpoint_file = Path(checkpoint_file)
        self.completed_urls: Set[str] = set()
        self.pending_urls: list = []
        self.metadata: dict = {}
        self._load()
    
    def _load(self):
        """Load checkpoint from file."""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file) as f:
                data = json.load(f)
                self.completed_urls = set(data.get('completed', []))
                self.pending_urls = data.get('pending', [])
                self.metadata = data.get('metadata', {})
    
    def save(self):
        """Save checkpoint to file."""
        data = {
            'completed': list(self.completed_urls),
            'pending': self.pending_urls,
            'metadata': self.metadata,
            'saved_at': datetime.now().isoformat()
        }
        
        # Atomic write
        temp_file = self.checkpoint_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(data, f)
        temp_file.rename(self.checkpoint_file)
    
    def mark_completed(self, url: str):
        """Mark URL as completed."""
        self.completed_urls.add(url)
        if url in self.pending_urls:
            self.pending_urls.remove(url)
    
    def add_pending(self, urls: list):
        """Add URLs to pending list."""
        for url in urls:
            if url not in self.completed_urls and url not in self.pending_urls:
                self.pending_urls.append(url)
    
    def get_next_url(self) -> Optional[str]:
        """Get next URL to process."""
        while self.pending_urls:
            url = self.pending_urls[0]
            if url not in self.completed_urls:
                return url
            self.pending_urls.pop(0)
        return None
    
    def is_completed(self, url: str) -> bool:
        """Check if URL already processed."""
        return url in self.completed_urls

# Usage
checkpoint = Checkpoint('my_crawl_checkpoint.json')

# Add seed URLs
checkpoint.add_pending(seed_urls)

# Process with checkpointing
while True:
    url = checkpoint.get_next_url()
    if not url:
        break
    
    try:
        result = scrape(url)
        checkpoint.mark_completed(url)
        
        # Add discovered URLs
        checkpoint.add_pending(result.get('links', []))
        
        # Save periodically
        if len(checkpoint.completed_urls) % 100 == 0:
            checkpoint.save()
            
    except Exception as e:
        print(f"Failed: {url} - {e}")
        # Don't mark as completed, will retry on restart

# Final save
checkpoint.save()
```

---

## 4. Dead Letter Queue

Handle permanently failing items.

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import json

@dataclass
class FailedItem:
    url: str
    error: str
    attempts: int
    first_failure: datetime
    last_failure: datetime
    metadata: dict = None

class DeadLetterQueue:
    """Store and manage permanently failed items."""
    
    def __init__(self, storage_path: str = 'dlq.jsonl'):
        self.storage_path = Path(storage_path)
        self.items: List[FailedItem] = []
        self._load()
    
    def _load(self):
        """Load DLQ from file."""
        if self.storage_path.exists():
            with open(self.storage_path) as f:
                for line in f:
                    data = json.loads(line)
                    self.items.append(FailedItem(
                        url=data['url'],
                        error=data['error'],
                        attempts=data['attempts'],
                        first_failure=datetime.fromisoformat(data['first_failure']),
                        last_failure=datetime.fromisoformat(data['last_failure']),
                        metadata=data.get('metadata')
                    ))
    
    def add(self, url: str, error: str, attempts: int = 1, metadata: dict = None):
        """Add item to DLQ."""
        now = datetime.now()
        
        # Check if URL already in DLQ
        existing = next((item for item in self.items if item.url == url), None)
        
        if existing:
            existing.error = error
            existing.attempts += attempts
            existing.last_failure = now
        else:
            self.items.append(FailedItem(
                url=url,
                error=error,
                attempts=attempts,
                first_failure=now,
                last_failure=now,
                metadata=metadata
            ))
        
        self._save_item(self.items[-1])
    
    def _save_item(self, item: FailedItem):
        """Append item to storage."""
        with open(self.storage_path, 'a') as f:
            data = {
                'url': item.url,
                'error': item.error,
                'attempts': item.attempts,
                'first_failure': item.first_failure.isoformat(),
                'last_failure': item.last_failure.isoformat(),
                'metadata': item.metadata
            }
            f.write(json.dumps(data) + '\n')
    
    def get_retriable(self, max_attempts: int = 10) -> List[FailedItem]:
        """Get items that could be retried."""
        return [item for item in self.items if item.attempts < max_attempts]
    
    def get_stats(self) -> dict:
        """Get DLQ statistics."""
        if not self.items:
            return {'total': 0}
        
        errors = {}
        for item in self.items:
            error_type = item.error.split(':')[0]
            errors[error_type] = errors.get(error_type, 0) + 1
        
        return {
            'total': len(self.items),
            'by_error': errors,
            'oldest': min(item.first_failure for item in self.items).isoformat(),
            'newest': max(item.last_failure for item in self.items).isoformat()
        }

# Usage
dlq = DeadLetterQueue()

try:
    result = scrape(url)
except PermanentError as e:
    dlq.add(url, str(e), metadata={'source': 'main_crawler'})
```

---

## 5. Graceful Shutdown

```python
import signal
import threading
from queue import Queue, Empty

class GracefulScraper:
    """Scraper with graceful shutdown support."""
    
    def __init__(self):
        self.shutdown_event = threading.Event()
        self.active_requests = 0
        self.request_lock = threading.Lock()
        self.checkpoint = Checkpoint()
        
        # Register signal handlers
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)
    
    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signal."""
        print("Shutdown signal received, finishing active requests...")
        self.shutdown_event.set()
    
    def should_continue(self) -> bool:
        """Check if should continue processing."""
        return not self.shutdown_event.is_set()
    
    def run(self, urls: list):
        """Run scraper with graceful shutdown."""
        self.checkpoint.add_pending(urls)
        
        while self.should_continue():
            url = self.checkpoint.get_next_url()
            if not url:
                break
            
            with self.request_lock:
                self.active_requests += 1
            
            try:
                result = self._scrape(url)
                self.checkpoint.mark_completed(url)
                
                if result.get('links'):
                    self.checkpoint.add_pending(result['links'])
                    
            except Exception as e:
                print(f"Error: {url} - {e}")
            finally:
                with self.request_lock:
                    self.active_requests -= 1
        
        # Wait for active requests
        print(f"Waiting for {self.active_requests} active requests...")
        while self.active_requests > 0:
            time.sleep(0.1)
        
        # Save checkpoint
        self.checkpoint.save()
        print(f"Saved checkpoint with {len(self.checkpoint.completed_urls)} completed URLs")
    
    def _scrape(self, url: str) -> dict:
        """Scrape single URL."""
        response = requests.get(url, timeout=30)
        # ... parsing logic
        return {'data': {}, 'links': []}
```

---

## 6. Health Checks

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

@dataclass  
class HealthCheck:
    name: str
    check_func: callable
    timeout: float = 5.0

class HealthChecker:
    """System health monitoring."""
    
    def __init__(self):
        self.checks: List[HealthCheck] = []
        self.last_results = {}
    
    def add_check(self, name: str, check_func: callable, timeout: float = 5.0):
        self.checks.append(HealthCheck(name, check_func, timeout))
    
    def run_checks(self) -> dict:
        """Run all health checks."""
        results = {'healthy': True, 'checks': {}}
        
        for check in self.checks:
            try:
                start = time.time()
                check.check_func()
                duration = time.time() - start
                
                results['checks'][check.name] = {
                    'status': 'healthy',
                    'duration': round(duration, 3)
                }
            except Exception as e:
                results['healthy'] = False
                results['checks'][check.name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
        
        self.last_results = results
        return results

# Define health checks
health = HealthChecker()

health.add_check('redis', lambda: redis_client.ping())
health.add_check('database', lambda: db.execute('SELECT 1'))
health.add_check('target_site', lambda: requests.head('https://example.com', timeout=5))
health.add_check('disk_space', lambda: check_disk_space_above(10))  # 10% minimum

# Run periodically or expose via HTTP
@app.route('/health')
def health_endpoint():
    results = health.run_checks()
    status = 200 if results['healthy'] else 503
    return jsonify(results), status
```

---

## Summary

| Strategy | Use Case | Complexity |
|----------|----------|------------|
| Exponential Backoff | Transient failures | Low |
| Circuit Breaker | Prevent cascading | Medium |
| Checkpointing | Resume after crash | Medium |
| Dead Letter Queue | Track failures | Medium |
| Graceful Shutdown | Clean stops | Medium |
| Health Checks | Monitoring | Low |

---

*This completes the Colony Orchestration section!*
