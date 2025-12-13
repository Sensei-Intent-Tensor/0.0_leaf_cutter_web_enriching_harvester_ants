# Scheduling

> **When and How Often to Run Your Scrapers**

Effective scheduling balances data freshness against resource usage and target site impact. This document covers scheduling strategies and implementation.

---

## Scheduling Strategies

```
┌─────────────────────────────────────────────────────────────────┐
│                    SCHEDULING STRATEGIES                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  FIXED INTERVAL                                                 │
│  └── Run every N minutes/hours/days                            │
│      Best for: Regular updates, monitoring                      │
│                                                                 │
│  CRON-BASED                                                    │
│  └── Run at specific times (0 9 * * 1-5 = 9am weekdays)       │
│      Best for: Business hours, avoiding peak times             │
│                                                                 │
│  EVENT-DRIVEN                                                  │
│  └── Trigger on external events (webhook, file, message)       │
│      Best for: Real-time needs, on-demand scraping            │
│                                                                 │
│  ADAPTIVE                                                      │
│  └── Adjust frequency based on change rate                     │
│      Best for: Efficient resource use, varying update rates    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Simple Scheduling with APScheduler

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Create scheduler
scheduler = BackgroundScheduler()

# Interval-based
scheduler.add_job(
    scrape_products,
    IntervalTrigger(hours=6),
    id='product_scraper',
    name='Scrape products every 6 hours'
)

# Cron-based
scheduler.add_job(
    scrape_news,
    CronTrigger(hour=9, minute=0),  # 9:00 AM daily
    id='news_scraper',
    name='Scrape news at 9 AM'
)

# Cron with expression
scheduler.add_job(
    scrape_prices,
    CronTrigger.from_crontab('0 */4 * * *'),  # Every 4 hours
    id='price_scraper'
)

# Start scheduler
scheduler.start()
```

### Common Cron Patterns

| Pattern | Meaning |
|---------|---------|
| `0 * * * *` | Every hour |
| `*/15 * * * *` | Every 15 minutes |
| `0 9 * * *` | Daily at 9 AM |
| `0 9 * * 1-5` | Weekdays at 9 AM |
| `0 0 * * 0` | Weekly on Sunday |
| `0 0 1 * *` | Monthly on 1st |
| `0 9,18 * * *` | At 9 AM and 6 PM |

---

## 2. Distributed Scheduling with Celery

```python
from celery import Celery
from celery.schedules import crontab

app = Celery('scraper', broker='redis://localhost:6379')

# Define tasks
@app.task
def scrape_site(site_id):
    """Scrape a specific site."""
    # Implementation
    pass

@app.task
def scrape_all_products():
    """Scrape all product sources."""
    sources = get_product_sources()
    for source in sources:
        scrape_site.delay(source.id)

# Configure beat schedule
app.conf.beat_schedule = {
    'scrape-products-every-6-hours': {
        'task': 'tasks.scrape_all_products',
        'schedule': crontab(minute=0, hour='*/6'),
    },
    'scrape-news-morning': {
        'task': 'tasks.scrape_news',
        'schedule': crontab(minute=0, hour=9),
    },
    'scrape-prices-frequently': {
        'task': 'tasks.scrape_prices',
        'schedule': 60.0 * 15,  # Every 15 minutes
    },
}

# Run with:
# celery -A tasks worker --beat
```

---

## 3. Priority-Based Scheduling

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List
import heapq

@dataclass
class ScheduledJob:
    priority: int
    next_run: datetime
    job_id: str
    interval: timedelta
    func: callable
    
    def __lt__(self, other):
        # Lower priority number = higher priority
        # Earlier time = higher priority
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.next_run < other.next_run

class PriorityScheduler:
    """Scheduler with job priorities."""
    
    def __init__(self):
        self.jobs: List[ScheduledJob] = []
        self.running = False
    
    def add_job(self, job_id: str, func: callable, 
                interval: timedelta, priority: int = 5):
        """Add a job with priority (1=highest, 10=lowest)."""
        job = ScheduledJob(
            priority=priority,
            next_run=datetime.now(),
            job_id=job_id,
            interval=interval,
            func=func
        )
        heapq.heappush(self.jobs, job)
    
    def run(self):
        """Run the scheduler."""
        self.running = True
        
        while self.running and self.jobs:
            job = heapq.heappop(self.jobs)
            
            # Wait until next run time
            now = datetime.now()
            if job.next_run > now:
                sleep_time = (job.next_run - now).total_seconds()
                time.sleep(sleep_time)
            
            # Execute job
            try:
                job.func()
            except Exception as e:
                print(f"Job {job.job_id} failed: {e}")
            
            # Reschedule
            job.next_run = datetime.now() + job.interval
            heapq.heappush(self.jobs, job)

# Usage
scheduler = PriorityScheduler()
scheduler.add_job('critical_prices', scrape_prices, timedelta(minutes=15), priority=1)
scheduler.add_job('products', scrape_products, timedelta(hours=6), priority=5)
scheduler.add_job('archive', scrape_archive, timedelta(days=1), priority=10)
scheduler.run()
```

---

## 4. Adaptive Scheduling

Adjust scraping frequency based on how often content changes.

```python
from datetime import datetime, timedelta
from collections import deque

class AdaptiveScheduler:
    """Adjust frequency based on change rate."""
    
    def __init__(self, min_interval: timedelta, max_interval: timedelta):
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.change_history = deque(maxlen=10)  # Last 10 scrapes
        self.current_interval = min_interval
    
    def record_scrape(self, changed: bool):
        """Record whether content changed."""
        self.change_history.append(changed)
        self._adjust_interval()
    
    def _adjust_interval(self):
        """Adjust interval based on change rate."""
        if len(self.change_history) < 3:
            return
        
        change_rate = sum(self.change_history) / len(self.change_history)
        
        if change_rate > 0.8:
            # Content changes frequently - increase frequency
            self.current_interval = max(
                self.min_interval,
                self.current_interval * 0.75
            )
        elif change_rate < 0.2:
            # Content rarely changes - decrease frequency
            self.current_interval = min(
                self.max_interval,
                self.current_interval * 1.5
            )
    
    def get_next_run(self) -> datetime:
        """Get next scheduled run time."""
        return datetime.now() + self.current_interval

# Usage
scheduler = AdaptiveScheduler(
    min_interval=timedelta(minutes=15),
    max_interval=timedelta(hours=24)
)

while True:
    old_content = get_cached_content()
    new_content = scrape()
    
    changed = old_content != new_content
    scheduler.record_scrape(changed)
    
    if changed:
        save(new_content)
    
    next_run = scheduler.get_next_run()
    sleep_until(next_run)
```

---

## 5. Time-Aware Scheduling

Consider time zones and business hours.

```python
from datetime import datetime
import pytz

class TimeAwareScheduler:
    """Schedule with time zone and business hours awareness."""
    
    def __init__(self, target_timezone: str = 'America/New_York'):
        self.tz = pytz.timezone(target_timezone)
    
    def is_business_hours(self) -> bool:
        """Check if current time is during business hours."""
        now = datetime.now(self.tz)
        # Monday = 0, Sunday = 6
        if now.weekday() >= 5:  # Weekend
            return False
        if now.hour < 9 or now.hour >= 17:  # Before 9 or after 5
            return False
        return True
    
    def is_off_peak(self) -> bool:
        """Check if current time is off-peak."""
        now = datetime.now(self.tz)
        # Off-peak: nights (10pm-6am) and weekends
        if now.weekday() >= 5:
            return True
        if now.hour >= 22 or now.hour < 6:
            return True
        return False
    
    def get_optimal_time(self, prefer_off_peak: bool = True) -> datetime:
        """Get optimal time for next scrape."""
        now = datetime.now(self.tz)
        
        if prefer_off_peak and not self.is_off_peak():
            # Schedule for next off-peak period
            if now.hour < 22:
                return now.replace(hour=22, minute=0, second=0)
            else:
                return (now + timedelta(days=1)).replace(hour=6, minute=0)
        
        return now

# Usage
scheduler = TimeAwareScheduler('America/New_York')

def scrape_with_awareness():
    if scheduler.is_off_peak():
        # Can be more aggressive during off-peak
        rate_limit = 0.5  # 2 requests/second
    else:
        # Be gentler during business hours
        rate_limit = 2.0  # 0.5 requests/second
    
    scrape(rate_limit=rate_limit)
```

---

## 6. Job Persistence

Survive restarts by persisting job state.

```python
import json
from pathlib import Path
from datetime import datetime

class PersistentScheduler:
    """Scheduler with persistent state."""
    
    def __init__(self, state_file: str = 'scheduler_state.json'):
        self.state_file = Path(state_file)
        self.jobs = {}
        self._load_state()
    
    def _load_state(self):
        """Load state from file."""
        if self.state_file.exists():
            with open(self.state_file) as f:
                state = json.load(f)
                for job_id, job_state in state.items():
                    self.jobs[job_id] = {
                        'last_run': datetime.fromisoformat(job_state['last_run'])
                            if job_state['last_run'] else None,
                        'next_run': datetime.fromisoformat(job_state['next_run']),
                        'interval_seconds': job_state['interval_seconds']
                    }
    
    def _save_state(self):
        """Save state to file."""
        state = {}
        for job_id, job in self.jobs.items():
            state[job_id] = {
                'last_run': job['last_run'].isoformat() if job['last_run'] else None,
                'next_run': job['next_run'].isoformat(),
                'interval_seconds': job['interval_seconds']
            }
        with open(self.state_file, 'w') as f:
            json.dump(state, f)
    
    def register_job(self, job_id: str, interval_seconds: int):
        """Register a job."""
        if job_id not in self.jobs:
            self.jobs[job_id] = {
                'last_run': None,
                'next_run': datetime.now(),
                'interval_seconds': interval_seconds
            }
            self._save_state()
    
    def should_run(self, job_id: str) -> bool:
        """Check if job should run now."""
        job = self.jobs.get(job_id)
        if not job:
            return False
        return datetime.now() >= job['next_run']
    
    def mark_complete(self, job_id: str):
        """Mark job as completed."""
        job = self.jobs.get(job_id)
        if job:
            job['last_run'] = datetime.now()
            job['next_run'] = datetime.now() + timedelta(seconds=job['interval_seconds'])
            self._save_state()
```

---

## Summary

| Strategy | Best For | Complexity |
|----------|----------|------------|
| Fixed Interval | Regular monitoring | Low |
| Cron | Business schedules | Low |
| Priority | Resource management | Medium |
| Adaptive | Efficient scraping | Medium |
| Time-Aware | Polite scraping | Medium |
| Distributed | Large scale | High |

---

*Next: [02_queue_management.md](02_queue_management.md) - Managing scrape job queues*
