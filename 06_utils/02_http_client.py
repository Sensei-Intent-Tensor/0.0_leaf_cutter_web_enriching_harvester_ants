"""
HTTP Client with retry, sessions, and stealth features.
"""

import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class HttpClientConfig:
    """Configuration for HTTP client."""
    timeout: int = 30
    max_retries: int = 3
    backoff_factor: float = 0.5
    retry_statuses: tuple = (429, 500, 502, 503, 504)
    verify_ssl: bool = True
    

class HttpClient:
    """HTTP client with retry logic and stealth features."""
    
    DEFAULT_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    ]
    
    def __init__(self, config: Optional[HttpClientConfig] = None):
        self.config = config or HttpClientConfig()
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create session with retry logic."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.backoff_factor,
            status_forcelist=self.config.retry_statuses,
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        session.headers.update(self.DEFAULT_HEADERS)
        
        return session
    
    def _get_headers(self, headers: Optional[Dict] = None) -> Dict:
        """Get headers with random user agent."""
        final_headers = {'User-Agent': random.choice(self.USER_AGENTS)}
        if headers:
            final_headers.update(headers)
        return final_headers
    
    def get(self, url: str, headers: Optional[Dict] = None,
            proxy: Optional[str] = None, **kwargs) -> requests.Response:
        """Make GET request."""
        proxies = {'http': proxy, 'https': proxy} if proxy else None
        
        return self.session.get(
            url,
            headers=self._get_headers(headers),
            timeout=self.config.timeout,
            verify=self.config.verify_ssl,
            proxies=proxies,
            **kwargs
        )
    
    def post(self, url: str, data: Any = None, json: Any = None,
             headers: Optional[Dict] = None, proxy: Optional[str] = None,
             **kwargs) -> requests.Response:
        """Make POST request."""
        proxies = {'http': proxy, 'https': proxy} if proxy else None
        
        return self.session.post(
            url,
            data=data,
            json=json,
            headers=self._get_headers(headers),
            timeout=self.config.timeout,
            verify=self.config.verify_ssl,
            proxies=proxies,
            **kwargs
        )
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AsyncHttpClient:
    """Async HTTP client using aiohttp."""
    
    def __init__(self, config: Optional[HttpClientConfig] = None):
        self.config = config or HttpClientConfig()
        self._session = None
    
    async def _get_session(self):
        """Get or create aiohttp session."""
        if self._session is None:
            import aiohttp
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    
    async def get(self, url: str, headers: Optional[Dict] = None,
                  proxy: Optional[str] = None) -> str:
        """Make async GET request."""
        session = await self._get_session()
        
        final_headers = {'User-Agent': random.choice(HttpClient.USER_AGENTS)}
        if headers:
            final_headers.update(headers)
        
        async with session.get(url, headers=final_headers, proxy=proxy) as response:
            return await response.text()
    
    async def close(self):
        """Close the session."""
        if self._session:
            await self._session.close()
            self._session = None
