"""
API Ant Template
================

Scraper for JSON API endpoints.

Usage:
    class ProductAPIAnt(APIAnt):
        name = "product_api"
        base_url = "https://api.example.com"
        
        def extract(self, data):
            return {
                'id': data['product']['id'],
                'name': data['product']['name'],
            }
    
    ant = ProductAPIAnt(api_key='your-key')
    result = ant.scrape('/products/123')
"""

from simple_ant import SimpleAnt, ScrapeResult
from typing import Dict, Any, Optional, List
import time


class APIAnt(SimpleAnt):
    """
    Ant for consuming JSON APIs.
    
    Customize:
        - base_url: API base URL
        - api_key: Optional API key
        - auth_header: Header name for API key
    """
    
    name: str = "api_ant"
    
    # API settings
    base_url: str = ""
    api_key: Optional[str] = None
    auth_header: str = "Authorization"
    auth_prefix: str = "Bearer"
    
    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(**kwargs)
        
        if api_key:
            self.api_key = api_key
        
        # Set up auth header
        if self.api_key:
            self.session.headers[self.auth_header] = f"{self.auth_prefix} {self.api_key}"
        
        # Accept JSON
        self.session.headers['Accept'] = 'application/json'
        self.session.headers['Content-Type'] = 'application/json'
    
    def scrape(self, endpoint: str, params: Dict = None) -> ScrapeResult:
        """Fetch API endpoint."""
        start = time.time()
        
        url = f"{self.base_url}{endpoint}" if self.base_url else endpoint
        
        self._wait_for_rate_limit()
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                return ScrapeResult(
                    success=False,
                    url=url,
                    error=f"HTTP {response.status_code}",
                    status_code=response.status_code,
                    duration_ms=(time.time() - start) * 1000
                )
            
            json_data = response.json()
            data = self.extract(json_data)
            
            return ScrapeResult(
                success=True,
                url=url,
                data=data,
                status_code=response.status_code,
                duration_ms=(time.time() - start) * 1000
            )
            
        except Exception as e:
            return ScrapeResult(
                success=False,
                url=url,
                error=str(e),
                duration_ms=(time.time() - start) * 1000
            )
    
    def extract(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract/transform data from JSON response.
        Override in subclass.
        """
        return data
    
    def paginate(
        self,
        endpoint: str,
        page_param: str = 'page',
        max_pages: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch all pages from paginated API."""
        all_items = []
        page = 1
        
        while page <= max_pages:
            result = self.scrape(endpoint, params={page_param: page})
            
            if not result.success:
                break
            
            items = result.data.get('items', result.data.get('results', []))
            
            if not items:
                break
            
            all_items.extend(items)
            page += 1
        
        return all_items
    
    def paginate_cursor(
        self,
        endpoint: str,
        cursor_param: str = 'cursor',
        cursor_field: str = 'next_cursor'
    ) -> List[Dict[str, Any]]:
        """Fetch all pages using cursor pagination."""
        all_items = []
        cursor = None
        
        while True:
            params = {cursor_param: cursor} if cursor else None
            result = self.scrape(endpoint, params=params)
            
            if not result.success:
                break
            
            items = result.data.get('items', result.data.get('results', []))
            all_items.extend(items)
            
            cursor = result.data.get(cursor_field)
            
            if not cursor:
                break
        
        return all_items


# Example usage
if __name__ == "__main__":
    class ExampleAPIAnt(APIAnt):
        name = "example_api"
        base_url = "https://jsonplaceholder.typicode.com"
        
        def extract(self, data):
            if isinstance(data, list):
                return {'items': data, 'count': len(data)}
            return data
    
    ant = ExampleAPIAnt()
    result = ant.scrape('/posts/1')
    print(f"Success: {result.success}")
    print(f"Data: {result.data}")
