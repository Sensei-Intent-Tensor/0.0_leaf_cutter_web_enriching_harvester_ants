"""
Proxy rotation and management.
"""

import random
import time
import threading
from typing import List, Optional, Dict
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class Proxy:
    """Proxy configuration."""
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = 'http'
    
    @property
    def full_url(self) -> str:
        """Get full proxy URL with auth."""
        if self.username and self.password:
            # http://user:pass@host:port
            parts = self.url.replace('http://', '').replace('https://', '')
            return f"{self.protocol}://{self.username}:{self.password}@{parts}"
        return self.url
    
    @classmethod
    def from_string(cls, proxy_str: str) -> 'Proxy':
        """Parse proxy from string format."""
        # Supports: host:port, user:pass@host:port, http://host:port
        if '://' in proxy_str:
            protocol = proxy_str.split('://')[0]
            proxy_str = proxy_str.split('://')[1]
        else:
            protocol = 'http'
        
        if '@' in proxy_str:
            auth, host = proxy_str.rsplit('@', 1)
            username, password = auth.split(':', 1)
            return cls(f"{protocol}://{host}", username, password, protocol)
        
        return cls(f"{protocol}://{proxy_str}", protocol=protocol)


@dataclass
class ProxyStats:
    """Track proxy performance."""
    successes: int = 0
    failures: int = 0
    total_time: float = 0
    last_used: float = 0
    blocked_until: float = 0
    
    @property
    def success_rate(self) -> float:
        total = self.successes + self.failures
        return self.successes / total if total > 0 else 0.5
    
    @property
    def avg_response_time(self) -> float:
        return self.total_time / self.successes if self.successes > 0 else 0


class ProxyManager:
    """Manage and rotate proxies."""
    
    def __init__(self, proxies: Optional[List[str]] = None,
                 rotation_strategy: str = 'round_robin'):
        """
        Args:
            proxies: List of proxy URLs
            rotation_strategy: 'round_robin', 'random', or 'best'
        """
        self.proxies: List[Proxy] = []
        self.stats: Dict[str, ProxyStats] = defaultdict(ProxyStats)
        self.rotation_strategy = rotation_strategy
        self._current_index = 0
        self._lock = threading.Lock()
        
        if proxies:
            for p in proxies:
                self.add_proxy(p)
    
    def add_proxy(self, proxy: str):
        """Add proxy to pool."""
        self.proxies.append(Proxy.from_string(proxy))
    
    def remove_proxy(self, proxy_url: str):
        """Remove proxy from pool."""
        self.proxies = [p for p in self.proxies if p.url != proxy_url]
    
    def get_next(self) -> Optional[str]:
        """Get next proxy based on rotation strategy."""
        if not self.proxies:
            return None
        
        with self._lock:
            available = self._get_available_proxies()
            if not available:
                return None
            
            if self.rotation_strategy == 'round_robin':
                proxy = self._round_robin(available)
            elif self.rotation_strategy == 'random':
                proxy = self._random(available)
            elif self.rotation_strategy == 'best':
                proxy = self._best_performing(available)
            else:
                proxy = available[0]
            
            self.stats[proxy.url].last_used = time.time()
            return proxy.full_url
    
    def _get_available_proxies(self) -> List[Proxy]:
        """Get proxies not currently blocked."""
        now = time.time()
        return [p for p in self.proxies 
                if self.stats[p.url].blocked_until < now]
    
    def _round_robin(self, available: List[Proxy]) -> Proxy:
        """Round robin selection."""
        self._current_index = (self._current_index + 1) % len(available)
        return available[self._current_index]
    
    def _random(self, available: List[Proxy]) -> Proxy:
        """Random selection."""
        return random.choice(available)
    
    def _best_performing(self, available: List[Proxy]) -> Proxy:
        """Select best performing proxy."""
        return max(available, 
                   key=lambda p: self.stats[p.url].success_rate)
    
    def record_success(self, proxy_url: str, response_time: float = 0):
        """Record successful request."""
        with self._lock:
            stats = self.stats[proxy_url]
            stats.successes += 1
            stats.total_time += response_time
    
    def record_failure(self, proxy_url: str, block_seconds: float = 0):
        """Record failed request."""
        with self._lock:
            stats = self.stats[proxy_url]
            stats.failures += 1
            if block_seconds > 0:
                stats.blocked_until = time.time() + block_seconds
    
    def get_stats(self) -> Dict:
        """Get proxy statistics."""
        return {
            proxy.url: {
                'success_rate': self.stats[proxy.url].success_rate,
                'successes': self.stats[proxy.url].successes,
                'failures': self.stats[proxy.url].failures,
                'avg_response_time': self.stats[proxy.url].avg_response_time,
            }
            for proxy in self.proxies
        }
