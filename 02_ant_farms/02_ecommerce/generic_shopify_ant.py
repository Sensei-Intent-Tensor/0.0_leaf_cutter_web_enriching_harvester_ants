"""
Generic Shopify Ant
===================

Scraper for any Shopify-based store.

Most Shopify stores expose a /products.json endpoint that provides
clean JSON data for all products.

Usage:
    ant = ShopifyAnt(store_url='https://example-store.com')
    
    # Get all products
    products = ant.get_all_products()
    
    # Get single product
    product = ant.get_product('product-handle')
"""

import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin

import requests


@dataclass
class ScrapeResult:
    success: bool
    url: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    scraped_at: datetime = None
    
    def __post_init__(self):
        if self.scraped_at is None:
            self.scraped_at = datetime.utcnow()


class ShopifyAnt:
    """
    Scraper for Shopify stores.
    
    Leverages the /products.json API endpoint that most
    Shopify stores expose by default.
    """
    
    name = "shopify_ant"
    
    def __init__(
        self,
        store_url: str,
        delay: float = 1.0,
        **kwargs
    ):
        """
        Initialize Shopify scraper.
        
        Args:
            store_url: Base URL of the Shopify store
            delay: Seconds between requests
        """
        self.store_url = store_url.rstrip('/')
        self.delay = delay
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        })
        
        self.logger = logging.getLogger(f"ant.{self.name}")
        self._last_request = 0
    
    def _wait(self):
        """Rate limiting."""
        elapsed = time.time() - self._last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self._last_request = time.time()
    
    def _get_json(self, endpoint: str, params: dict = None) -> dict:
        """Fetch JSON from endpoint."""
        self._wait()
        
        url = urljoin(self.store_url, endpoint)
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        return response.json()
    
    # -------------------------------------------------------------------------
    # Products API
    # -------------------------------------------------------------------------
    
    def get_all_products(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get all products from the store.
        
        Args:
            limit: Maximum number of products to fetch
            
        Returns:
            List of product dictionaries
        """
        all_products = []
        page = 1
        
        while True:
            self.logger.info(f"Fetching page {page}")
            
            try:
                data = self._get_json('/products.json', params={
                    'page': page,
                    'limit': 250  # Shopify max
                })
            except requests.RequestException as e:
                self.logger.error(f"Failed to fetch page {page}: {e}")
                break
            
            products = data.get('products', [])
            
            if not products:
                break
            
            all_products.extend(products)
            
            if limit and len(all_products) >= limit:
                all_products = all_products[:limit]
                break
            
            page += 1
        
        self.logger.info(f"Total products: {len(all_products)}")
        return all_products
    
    def get_product(self, handle: str) -> ScrapeResult:
        """
        Get a single product by handle.
        
        Args:
            handle: Product URL handle (slug)
            
        Returns:
            ScrapeResult with product data
        """
        url = f"/products/{handle}.json"
        
        try:
            data = self._get_json(url)
            product = data.get('product', {})
            
            return ScrapeResult(
                success=True,
                url=f"{self.store_url}{url}",
                data=self._normalize_product(product)
            )
            
        except requests.RequestException as e:
            return ScrapeResult(
                success=False,
                url=f"{self.store_url}{url}",
                error=str(e)
            )
    
    def _normalize_product(self, product: dict) -> dict:
        """Normalize product data to standard format."""
        
        # Get price from first variant
        variants = product.get('variants', [])
        first_variant = variants[0] if variants else {}
        
        return {
            'id': product.get('id'),
            'title': product.get('title'),
            'handle': product.get('handle'),
            'description': product.get('body_html', ''),
            'vendor': product.get('vendor'),
            'product_type': product.get('product_type'),
            'tags': product.get('tags', []),
            
            'price': {
                'amount': float(first_variant.get('price', 0)),
                'currency': 'USD',  # Shopify doesn't always include
                'compare_at': first_variant.get('compare_at_price'),
            },
            
            'variants': [
                {
                    'id': v.get('id'),
                    'title': v.get('title'),
                    'price': float(v.get('price', 0)),
                    'sku': v.get('sku'),
                    'available': v.get('available', True),
                    'inventory_quantity': v.get('inventory_quantity'),
                }
                for v in variants
            ],
            
            'images': [
                img.get('src') for img in product.get('images', [])
            ],
            
            'url': f"{self.store_url}/products/{product.get('handle')}",
            'created_at': product.get('created_at'),
            'updated_at': product.get('updated_at'),
        }
    
    # -------------------------------------------------------------------------
    # Collections API
    # -------------------------------------------------------------------------
    
    def get_collections(self) -> List[Dict[str, Any]]:
        """Get all collections."""
        try:
            data = self._get_json('/collections.json')
            return data.get('collections', [])
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch collections: {e}")
            return []
    
    def get_collection_products(self, handle: str) -> List[Dict[str, Any]]:
        """Get all products in a collection."""
        all_products = []
        page = 1
        
        while True:
            try:
                data = self._get_json(f'/collections/{handle}/products.json', params={
                    'page': page,
                    'limit': 250
                })
            except requests.RequestException:
                break
            
            products = data.get('products', [])
            
            if not products:
                break
            
            all_products.extend(products)
            page += 1
        
        return [self._normalize_product(p) for p in all_products]
    
    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for products."""
        try:
            data = self._get_json('/search/suggest.json', params={
                'q': query,
                'resources[type]': 'product'
            })
            
            results = data.get('resources', {}).get('results', {}).get('products', [])
            return results
            
        except requests.RequestException as e:
            self.logger.error(f"Search failed: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test if store is accessible and has products.json."""
        try:
            data = self._get_json('/products.json', params={'limit': 1})
            return 'products' in data
        except:
            return False


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example with a public Shopify store
    ant = ShopifyAnt(store_url='https://shop.example.com')
    
    if ant.test_connection():
        products = ant.get_all_products(limit=10)
        
        for product in products:
            print(f"{product['title']}: ${product['price']['amount']}")
    else:
        print("Store doesn't expose products.json endpoint")
