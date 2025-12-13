# Monitoring & Logging

> **Observability for Your Scraping Operations**

Without visibility into your scrapers, problems go unnoticed until data stops flowing. This document covers monitoring, logging, and alerting strategies.

---

## Observability Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                    OBSERVABILITY LAYERS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  METRICS (Numbers over time)                                   │
│  └── Requests/sec, error rates, latency, queue depth           │
│                                                                 │
│  LOGS (Events with context)                                    │
│  └── Errors, warnings, debug info, audit trail                 │
│                                                                 │
│  TRACES (Request flow)                                         │
│  └── Request → parse → store pipeline visibility               │
│                                                                 │
│  ALERTS (Notifications)                                        │
│  └── Error spike, queue backup, site blocking                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Structured Logging

```python
import logging
import json
from datetime import datetime
from typing import Any

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for easy parsing."""
    
    def format(self, record):
        log_obj = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        
        # Add extra fields
        if hasattr(record, 'url'):
            log_obj['url'] = record.url
        if hasattr(record, 'domain'):
            log_obj['domain'] = record.domain
        if hasattr(record, 'status_code'):
            log_obj['status_code'] = record.status_code
        if hasattr(record, 'duration'):
            log_obj['duration'] = record.duration
        
        # Add exception info
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_obj)

def setup_logging(name: str, level: str = 'INFO'):
    """Setup structured logging."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # Console handler with JSON
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    # File handler
    file_handler = logging.FileHandler(f'{name}.log')
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    return logger

# Usage
logger = setup_logging('scraper')

logger.info('Starting scrape', extra={'url': url, 'domain': domain})
logger.warning('Rate limited', extra={'url': url, 'status_code': 429})
logger.error('Request failed', extra={'url': url}, exc_info=True)
```

### Context Manager for Request Logging

```python
import time
from contextlib import contextmanager

@contextmanager
def log_request(logger, url: str):
    """Log request with timing."""
    start = time.time()
    domain = urlparse(url).netloc
    
    logger.info('Request started', extra={'url': url, 'domain': domain})
    
    try:
        yield
        duration = time.time() - start
        logger.info('Request completed', extra={
            'url': url,
            'domain': domain,
            'duration': round(duration, 3)
        })
    except Exception as e:
        duration = time.time() - start
        logger.error('Request failed', extra={
            'url': url,
            'domain': domain,
            'duration': round(duration, 3),
            'error': str(e)
        }, exc_info=True)
        raise

# Usage
with log_request(logger, url):
    response = requests.get(url)
```

---

## 2. Metrics Collection

```python
from dataclasses import dataclass, field
from collections import defaultdict
from threading import Lock
import time

@dataclass
class MetricsCollector:
    """Collect scraping metrics."""
    
    counters: dict = field(default_factory=lambda: defaultdict(int))
    gauges: dict = field(default_factory=dict)
    histograms: dict = field(default_factory=lambda: defaultdict(list))
    _lock: Lock = field(default_factory=Lock)
    
    def increment(self, name: str, value: int = 1, tags: dict = None):
        """Increment a counter."""
        key = self._make_key(name, tags)
        with self._lock:
            self.counters[key] += value
    
    def gauge(self, name: str, value: float, tags: dict = None):
        """Set a gauge value."""
        key = self._make_key(name, tags)
        with self._lock:
            self.gauges[key] = value
    
    def histogram(self, name: str, value: float, tags: dict = None):
        """Record a histogram value."""
        key = self._make_key(name, tags)
        with self._lock:
            self.histograms[key].append(value)
    
    def _make_key(self, name: str, tags: dict = None) -> str:
        if tags:
            tag_str = ','.join(f'{k}={v}' for k, v in sorted(tags.items()))
            return f'{name}{{{tag_str}}}'
        return name
    
    def get_stats(self) -> dict:
        """Get all metrics."""
        with self._lock:
            stats = {
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'histograms': {}
            }
            
            for key, values in self.histograms.items():
                if values:
                    stats['histograms'][key] = {
                        'count': len(values),
                        'min': min(values),
                        'max': max(values),
                        'avg': sum(values) / len(values),
                        'p50': sorted(values)[len(values) // 2],
                        'p95': sorted(values)[int(len(values) * 0.95)]
                    }
            
            return stats

# Global metrics instance
metrics = MetricsCollector()

# Usage in scraper
def scrape(url: str):
    domain = urlparse(url).netloc
    start = time.time()
    
    try:
        response = requests.get(url)
        
        metrics.increment('requests_total', tags={'domain': domain})
        metrics.increment(f'status_{response.status_code}', tags={'domain': domain})
        metrics.histogram('request_duration', time.time() - start, tags={'domain': domain})
        
        if response.status_code == 429:
            metrics.increment('rate_limited', tags={'domain': domain})
        
        return response
        
    except Exception as e:
        metrics.increment('requests_failed', tags={'domain': domain, 'error': type(e).__name__})
        raise
```

---

## 3. Prometheus Integration

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Define metrics
REQUESTS_TOTAL = Counter(
    'scraper_requests_total',
    'Total requests made',
    ['domain', 'status']
)

REQUEST_DURATION = Histogram(
    'scraper_request_duration_seconds',
    'Request duration in seconds',
    ['domain'],
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30]
)

QUEUE_SIZE = Gauge(
    'scraper_queue_size',
    'Number of URLs in queue',
    ['queue_name']
)

ACTIVE_WORKERS = Gauge(
    'scraper_active_workers',
    'Number of active workers'
)

def scrape_with_metrics(url: str):
    """Scrape with Prometheus metrics."""
    domain = urlparse(url).netloc
    
    with REQUEST_DURATION.labels(domain=domain).time():
        response = requests.get(url)
    
    REQUESTS_TOTAL.labels(
        domain=domain, 
        status=response.status_code
    ).inc()
    
    return response

# Start metrics server
start_http_server(8000)  # Expose on :8000/metrics
```

### Grafana Dashboard JSON

```json
{
  "panels": [
    {
      "title": "Requests per Second",
      "type": "graph",
      "targets": [
        {
          "expr": "rate(scraper_requests_total[5m])",
          "legendFormat": "{{domain}}"
        }
      ]
    },
    {
      "title": "Error Rate",
      "type": "graph",
      "targets": [
        {
          "expr": "rate(scraper_requests_total{status=~'4..|5..'}[5m]) / rate(scraper_requests_total[5m])",
          "legendFormat": "{{domain}}"
        }
      ]
    },
    {
      "title": "Request Duration p95",
      "type": "graph",
      "targets": [
        {
          "expr": "histogram_quantile(0.95, rate(scraper_request_duration_seconds_bucket[5m]))",
          "legendFormat": "p95"
        }
      ]
    }
  ]
}
```

---

## 4. Alerting

```python
from dataclasses import dataclass
from typing import Callable, List
import smtplib
from email.mime.text import MIMEText

@dataclass
class Alert:
    name: str
    condition: Callable[[dict], bool]
    message_template: str
    cooldown_seconds: int = 300

class AlertManager:
    """Manage and send alerts."""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.last_fired = {}
    
    def add_alert(self, alert: Alert):
        self.alerts.append(alert)
    
    def check(self, metrics: dict):
        """Check all alerts against current metrics."""
        now = time.time()
        
        for alert in self.alerts:
            # Check cooldown
            last = self.last_fired.get(alert.name, 0)
            if now - last < alert.cooldown_seconds:
                continue
            
            # Check condition
            if alert.condition(metrics):
                self._fire_alert(alert, metrics)
                self.last_fired[alert.name] = now
    
    def _fire_alert(self, alert: Alert, metrics: dict):
        """Fire an alert."""
        message = alert.message_template.format(**metrics)
        print(f"ALERT [{alert.name}]: {message}")
        # Send notification (email, Slack, PagerDuty, etc.)

# Define alerts
alerts = AlertManager()

alerts.add_alert(Alert(
    name='high_error_rate',
    condition=lambda m: m.get('error_rate', 0) > 0.1,
    message_template='Error rate is {error_rate:.1%}'
))

alerts.add_alert(Alert(
    name='queue_backup',
    condition=lambda m: m.get('queue_size', 0) > 10000,
    message_template='Queue size is {queue_size}'
))

alerts.add_alert(Alert(
    name='rate_limited',
    condition=lambda m: m.get('rate_limited_count', 0) > 100,
    message_template='Rate limited {rate_limited_count} times'
))

# Check periodically
while True:
    current_metrics = metrics.get_stats()
    alerts.check(current_metrics)
    time.sleep(60)
```

---

## 5. Dashboard

```python
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Scraper Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .metric { display: inline-block; margin: 20px; padding: 20px; border: 1px solid #ccc; }
        .metric h3 { margin: 0; color: #666; }
        .metric .value { font-size: 48px; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Scraper Dashboard</h1>
    <div id="metrics"></div>
    <canvas id="chart" width="800" height="400"></canvas>
    <script>
        async function updateMetrics() {
            const response = await fetch('/api/metrics');
            const data = await response.json();
            
            document.getElementById('metrics').innerHTML = `
                <div class="metric">
                    <h3>Requests</h3>
                    <div class="value">${data.counters.requests_total || 0}</div>
                </div>
                <div class="metric">
                    <h3>Errors</h3>
                    <div class="value">${data.counters.requests_failed || 0}</div>
                </div>
                <div class="metric">
                    <h3>Queue</h3>
                    <div class="value">${data.gauges.queue_size || 0}</div>
                </div>
            `;
        }
        
        setInterval(updateMetrics, 5000);
        updateMetrics();
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/metrics')
def api_metrics():
    return jsonify(metrics.get_stats())

@app.route('/api/health')
def health():
    stats = metrics.get_stats()
    healthy = stats['counters'].get('requests_failed', 0) < 100
    return jsonify({'healthy': healthy}), 200 if healthy else 503

if __name__ == '__main__':
    app.run(port=5000)
```

---

## 6. Log Aggregation

### Sending to Elasticsearch

```python
from elasticsearch import Elasticsearch
import logging

class ElasticsearchHandler(logging.Handler):
    """Send logs to Elasticsearch."""
    
    def __init__(self, es_url: str, index_prefix: str = 'scraper-logs'):
        super().__init__()
        self.es = Elasticsearch([es_url])
        self.index_prefix = index_prefix
    
    def emit(self, record):
        try:
            index = f"{self.index_prefix}-{datetime.now():%Y.%m.%d}"
            doc = {
                '@timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
            }
            
            # Add extra fields
            for key in ['url', 'domain', 'status_code', 'duration']:
                if hasattr(record, key):
                    doc[key] = getattr(record, key)
            
            self.es.index(index=index, body=doc)
        except Exception:
            pass  # Don't fail on logging errors

# Add to logger
logger.addHandler(ElasticsearchHandler('http://localhost:9200'))
```

---

## Summary

| Component | Purpose | Tools |
|-----------|---------|-------|
| Logging | Debug & audit | Python logging, ELK |
| Metrics | Performance tracking | Prometheus, StatsD |
| Dashboards | Visualization | Grafana, custom |
| Alerts | Notification | PagerDuty, Slack |

---

*Next: [05_failure_recovery.md](05_failure_recovery.md) - Handling failures gracefully*
