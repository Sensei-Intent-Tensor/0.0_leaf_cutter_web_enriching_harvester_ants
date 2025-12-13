"""
Product Schema Ant
==================

Extracts product data from Schema.org structured data.

Many e-commerce sites include Schema.org Product markup for SEO.
This ant extracts that structured data for clean, reliable extraction.

Usage:
    ant = ProductSchemaAnt()
    result = ant.scrape('https://example.com/product/123')
    
    if result.success and result.data['schema_found']:
        print(result.data['product'])
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

import requests
from bs4 import BeautifulSoup


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


class ProductSchemaAnt:
    """
    Extracts product data from Schema.org JSON-LD.
    
    Works with any site that implements Schema.org Product markup.
    """
    
    name = "product_schema_ant"
    
    def __init__(self, **kwargs):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml',
        })
    
    def scrape(self, url: str) -> ScrapeResult:
        """
        Scrape product data from Schema.org markup.
        
        Args:
            url: Product page URL
            
        Returns:
            ScrapeResult with product data
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            return ScrapeResult(
                success=False,
                url=url,
                error=str(e)
            )
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Try to find Schema.org Product data
        product_data = self._extract_schema(soup)
        
        if product_data:
            return ScrapeResult(
                success=True,
                url=url,
                data={
                    'schema_found': True,
                    'product': self._normalize_product(product_data),
                    'raw_schema': product_data
                }
            )
        
        # Fallback: try to extract basic data from HTML
        basic_data = self._extract_basic(soup, url)
        
        return ScrapeResult(
            success=True,
            url=url,
            data={
                'schema_found': False,
                'product': basic_data
            }
        )
    
    def _extract_schema(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract Schema.org JSON-LD data."""
        
        # Find all JSON-LD scripts
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                
                # Handle array of schemas
                if isinstance(data, list):
                    for item in data:
                        if self._is_product_schema(item):
                            return item
                
                # Handle single schema
                elif self._is_product_schema(data):
                    return data
                
                # Handle @graph format
                elif isinstance(data.get('@graph'), list):
                    for item in data['@graph']:
                        if self._is_product_schema(item):
                            return item
                            
            except (json.JSONDecodeError, TypeError):
                continue
        
        return None
    
    def _is_product_schema(self, data: dict) -> bool:
        """Check if data is a Product schema."""
        schema_type = data.get('@type', '')
        
        if isinstance(schema_type, list):
            return 'Product' in schema_type
        
        return schema_type == 'Product'
    
    def _normalize_product(self, schema: dict) -> dict:
        """Normalize Schema.org Product to standard format."""
        
        # Get offers (pricing)
        offers = schema.get('offers', {})
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        
        # Get price
        price = offers.get('price')
        if price:
            price = float(price)
        
        # Get images
        images = schema.get('image', [])
        if isinstance(images, str):
            images = [images]
        elif isinstance(images, dict):
            images = [images.get('url', images.get('@id', ''))]
        
        # Get rating
        rating_data = schema.get('aggregateRating', {})
        
        return {
            'name': schema.get('name'),
            'description': schema.get('description'),
            'sku': schema.get('sku'),
            'brand': self._get_brand(schema),
            'price': {
                'amount': price,
                'currency': offers.get('priceCurrency', 'USD'),
            },
            'availability': self._parse_availability(offers.get('availability', '')),
            'images': images,
            'rating': {
                'value': rating_data.get('ratingValue'),
                'count': rating_data.get('reviewCount'),
            },
            'url': schema.get('url'),
        }
    
    def _get_brand(self, schema: dict) -> Optional[str]:
        """Extract brand name."""
        brand = schema.get('brand')
        
        if isinstance(brand, str):
            return brand
        elif isinstance(brand, dict):
            return brand.get('name')
        
        return None
    
    def _parse_availability(self, availability: str) -> str:
        """Parse Schema.org availability to simple status."""
        availability = availability.lower()
        
        if 'instock' in availability:
            return 'in_stock'
        elif 'outofstock' in availability:
            return 'out_of_stock'
        elif 'preorder' in availability:
            return 'preorder'
        elif 'discontinued' in availability:
            return 'discontinued'
        
        return 'unknown'
    
    def _extract_basic(self, soup: BeautifulSoup, url: str) -> dict:
        """Fallback extraction from HTML."""
        
        def safe_text(selector):
            el = soup.select_one(selector)
            return el.get_text(strip=True) if el else None
        
        def safe_attr(selector, attr):
            el = soup.select_one(selector)
            return el.get(attr) if el else None
        
        # Try common selectors
        title = (
            safe_text('h1') or 
            safe_text('[data-product-title]') or
            safe_text('.product-title')
        )
        
        price_text = (
            safe_text('[data-price]') or
            safe_text('.price') or
            safe_text('.product-price')
        )
        
        # Parse price
        price = None
        if price_text:
            match = re.search(r'[\d,.]+', price_text.replace(',', ''))
            if match:
                price = float(match.group())
        
        return {
            'name': title,
            'description': safe_text('.product-description'),
            'price': {'amount': price, 'currency': 'USD'},
            'images': [
                safe_attr('.product-image img', 'src') or
                safe_attr('[data-product-image]', 'src')
            ],
            'url': url,
        }


# Example usage
if __name__ == "__main__":
    ant = ProductSchemaAnt()
    
    # Test with a product page
    result = ant.scrape('https://example.com/product')
    
    if result.success:
        if result.data['schema_found']:
            print("Found Schema.org data!")
            print(f"Product: {result.data['product']['name']}")
            print(f"Price: ${result.data['product']['price']['amount']}")
        else:
            print("No Schema.org data, using fallback extraction")
            print(f"Product: {result.data['product']['name']}")
