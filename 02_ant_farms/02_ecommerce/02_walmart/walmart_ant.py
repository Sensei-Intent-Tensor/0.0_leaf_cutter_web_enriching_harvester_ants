"""
Walmart Product Scraper

WARNING: For educational purposes. Use Walmart APIs for production.
"""

import re
import json
import time
import random
from typing import Optional, List, Dict
from dataclasses import dataclass, field, asdict
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import requests


@dataclass
class WalmartProduct:
    """Data model for a Walmart product."""
    product_id: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    currency: str = "USD"
    rating: Optional[float] = None
    review_count: Optional[int] = None
    availability: Optional[str] = None
    brand: Optional[str] = None
    seller: Optional[str] = None
    images: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class WalmartAnt:
    """Walmart product scraper."""
    
    BASE_URL = "https://www.walmart.com"
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    ]
    
    def __init__(self, delay: float = 3.0):
        self.delay = delay
        self.session = requests.Session()
        self._update_headers()
    
    def _update_headers(self):
        self.session.headers.update({
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })
    
    def _request(self, url: str) -> Optional[BeautifulSoup]:
        time.sleep(self.delay + random.random() * 2)
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'lxml')
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def search(self, query: str, max_results: int = 20) -> List[WalmartProduct]:
        """Search Walmart products."""
        url = f"{self.BASE_URL}/search?q={quote_plus(query)}"
        soup = self._request(url)
        
        if not soup:
            return []
        
        results = []
        
        # Try to extract from JSON data embedded in page
        for script in soup.select('script[type="application/json"]'):
            try:
                text = script.string or ''
                if 'searchResult' in text or 'itemStacks' in text:
                    data = json.loads(text)
                    items = self._find_items_in_json(data)
                    for item in items[:max_results]:
                        product = self._parse_json_item(item)
                        if product and product.title:
                            results.append(product)
                    break
            except:
                continue
        
        # Fallback to HTML parsing
        if not results:
            cards = soup.select('[data-item-id]')
            for card in cards[:max_results]:
                product = self._parse_search_card(card)
                if product and product.title:
                    results.append(product)
        
        return results
    
    def _find_items_in_json(self, data, depth=0) -> List[Dict]:
        """Recursively find product items in JSON."""
        if depth > 10:
            return []
        
        items = []
        
        if isinstance(data, dict):
            if 'usItemId' in data and 'name' in data:
                items.append(data)
            for v in data.values():
                items.extend(self._find_items_in_json(v, depth + 1))
        elif isinstance(data, list):
            for item in data:
                items.extend(self._find_items_in_json(item, depth + 1))
        
        return items
    
    def _parse_json_item(self, item: Dict) -> Optional[WalmartProduct]:
        try:
            product = WalmartProduct()
            
            product.product_id = item.get('usItemId') or item.get('id')
            product.title = item.get('name')
            product.url = f"{self.BASE_URL}/ip/{product.product_id}" if product.product_id else None
            
            # Price
            price_info = item.get('priceInfo', {})
            if price_info:
                current = price_info.get('currentPrice', {})
                product.price = current.get('price') or current.get('priceValue')
                was = price_info.get('wasPrice', {})
                if was:
                    product.original_price = was.get('price')
            elif 'price' in item:
                product.price = float(item['price']) if item['price'] else None
            
            # Rating
            rating_info = item.get('rating', {})
            if isinstance(rating_info, dict):
                product.rating = rating_info.get('averageRating')
                product.review_count = rating_info.get('numberOfReviews')
            elif isinstance(rating_info, (int, float)):
                product.rating = float(rating_info)
            
            # Image
            img = item.get('image') or item.get('imageInfo', {}).get('thumbnailUrl')
            if img:
                product.images = [img]
            
            # Brand
            product.brand = item.get('brand')
            
            # Availability
            avail = item.get('availabilityStatus')
            if avail:
                product.availability = avail
            
            from datetime import datetime
            product.scraped_at = datetime.now().isoformat()
            
            return product
        except Exception as e:
            return None
    
    def _parse_search_card(self, card) -> Optional[WalmartProduct]:
        try:
            product = WalmartProduct()
            
            product.product_id = card.get('data-item-id')
            
            link = card.select_one('a[href*="/ip/"]')
            if link:
                product.url = self.BASE_URL + link.get('href', '')
                product.title = link.get_text(strip=True)
            
            price_el = card.select_one('[data-automation-id="product-price"] span')
            if price_el:
                match = re.search(r'[\d,.]+', price_el.get_text().replace(',', ''))
                if match:
                    product.price = float(match.group())
            
            from datetime import datetime
            product.scraped_at = datetime.now().isoformat()
            
            return product
        except:
            return None


def search_walmart(query: str, max_results: int = 20) -> List[Dict]:
    ant = WalmartAnt()
    results = ant.search(query, max_results)
    return [r.to_dict() for r in results]


if __name__ == '__main__':
    results = search_walmart("laptop", max_results=10)
    for p in results:
        print(f"{p['title'][:50]}... - ${p['price']}")
