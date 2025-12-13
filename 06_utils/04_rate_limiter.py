"""
Rate limiting utilities for polite scraping.
"""

import time
import threading
from typing import Dict, Optional
from collections import defaultdict
from urllib.parse import urlparse


class RateLimiter:
    """Simple rate limiter for controlling request frequency."""
    
    def __init__(self, requests_per_second: float = 1.0, 
                 burst: int = 1):
        """
        Args:
            requests_per_second: Maximum requests per second
            burst: Number of requests allowed in burst
        """
        self.min_interval = 1.0 / requests_per_second
        self.burst = burst
        self.tokens = burst
        self.last_update = time.time()
        self._lock = threading.Lock()
    
    def wait(self):
        """Wait until a request can be made."""
        with self._lock:
            now = time.time()
            
            # Refill tokens based on time passed
            time_passed = now - self.last_update
            self.tokens = min(
                self.burst,
                self.tokens + time_passed / self.min_interval
            )
            self.last_update = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return
            
            # Need to wait
            wait_time = (1 - self.tokens) * self.min_interval
            self.tokens = 0
        
        time.sleep(wait_time)
    
    def __enter__(self):
        self.wait()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class DomainRateLimiter:
    """Rate limiter with per-domain limits."""
    
    def __init__(self, default_rate: float = 1.0):
        """
        Args:
            default_rate: Default requests per second for unknown domains
        """
        self.default_rate = default_rate
        self.domain_rates: Dict[str, float] = {}
        self.limiters: Dict[str, RateLimiter] = {}
        self._lock = threading.Lock()
    
    def set_rate(self, domain: str, requests_per_second: float):
        """Set rate for a specific domain."""
        self.domain_rates[domain] = requests_per_second
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        return urlparse(url).netloc
    
    def _get_limiter(self, domain: str) -> RateLimiter:
        """Get or create limiter for domain."""
        if domain not in self.limiters:
            rate = self.domain_rates.get(domain, self.default_rate)
            self.limiters[domain] = RateLimiter(rate)
        return self.limiters[domain]
    
    def wait(self, url: str):
        """Wait based on URL's domain."""
        domain = self._get_domain(url)
        with self._lock:
            limiter = self._get_limiter(domain)
        limiter.wait()
    
    def wait_for_domain(self, domain: str):
        """Wait for specific domain."""
        with self._lock:
            limiter = self._get_limiter(domain)
        limiter.wait()


class AdaptiveRateLimiter:
    """Rate limiter that adjusts based on response status."""
    
    def __init__(self, initial_rate: float = 1.0,
                 min_rate: float = 0.1,
                 max_rate: float = 10.0):
        self.current_rate = initial_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.limiter = RateLimiter(initial_rate)
        self._lock = threading.Lock()
    
    def wait(self):
        """Wait for next request slot."""
        self.limiter.wait()
    
    def record_success(self):
        """Record successful request - may increase rate."""
        with self._lock:
            self.current_rate = min(self.max_rate, self.current_rate * 1.1)
            self.limiter = RateLimiter(self.current_rate)
    
    def record_rate_limit(self):
        """Record rate limit response - decrease rate."""
        with self._lock:
            self.current_rate = max(self.min_rate, self.current_rate * 0.5)
            self.limiter = RateLimiter(self.current_rate)
    
    def record_error(self):
        """Record error - slightly decrease rate."""
        with self._lock:
            self.current_rate = max(self.min_rate, self.current_rate * 0.9)
            self.limiter = RateLimiter(self.current_rate)
    
    @property
    def requests_per_second(self) -> float:
        """Current rate."""
        return self.current_rate
