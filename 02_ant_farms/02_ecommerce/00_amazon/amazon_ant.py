"""
Amazon Product Scraper

WARNING: Amazon has very aggressive anti-scraping measures.
This is for EDUCATIONAL PURPOSES ONLY.

For production use:
- Amazon Product Advertising API (for affiliates)
- Third-party APIs (Keepa, Rainforest, etc.)
"""

import re
import json
import time
import random
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from urllib.parse import urljoin, quote_plus
from bs4 import BeautifulSoup
import requests


@dataclass
class AmazonProduct:
    """Data model for an Amazon product."""
    asin: Optional[str] = None
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
    features: List[str] = field(default_factory=list)
    description: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    
    # Metadata
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class AmazonAnt:
    """
    Amazon product scraper.
    
    ⚠️ WARNING: Amazon actively blocks scrapers. This will likely
    trigger CAPTCHAs and IP blocks. For production, use official APIs.
    
    Usage:
        ant = AmazonAnt()
        product = ant.get_product("B08N5WRWNW")  # ASIN
    """
    
    BASE_URL = "https://www.amazon.com"
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    ]
    
    def __init__(self, delay: float = 3.0, country: str = "com"):
        self.delay = delay
        self.country = country
        self.base_url = f"https://www.amazon.{country}"
        self.session = requests.Session()
        self._update_headers()
    
    def _update_headers(self):
        """Set realistic browser headers."""
        self.session.headers.update({
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def _request(self, url: str) -> Optional[BeautifulSoup]:
        """Make request with rate limiting."""
        time.sleep(self.delay + random.random() * 2)
        self._update_headers()  # Rotate user agent
        
        try:
            response = self.session.get(url, timeout=30)
            
            # Check for CAPTCHA
            if 'captcha' in response.text.lower() or response.status_code == 503:
                print("⚠️ CAPTCHA detected - Amazon is blocking requests")
                return None
            
            response.raise_for_status()
            return BeautifulSoup(response.text, 'lxml')
            
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def search(self, query: str, max_results: int = 20) -> List[AmazonProduct]:
        """
        Search Amazon for products.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of AmazonProduct objects
        """
        url = f"{self.base_url}/s?k={quote_plus(query)}"
        soup = self._request(url)
        
        if not soup:
            return []
        
        results = []
        
        # Find product cards
        cards = soup.select('[data-component-type="s-search-result"]')
        
        for card in cards[:max_results]:
            product = self._parse_search_card(card)
            if product and product.title:
                results.append(product)
                print(f"  Found: {product.title[:50]}...")
        
        return results
    
    def _parse_search_card(self, card) -> Optional[AmazonProduct]:
        """Parse a search result card."""
        try:
            product = AmazonProduct()
            
            # ASIN
            product.asin = card.get('data-asin')
            if product.asin:
                product.url = f"{self.base_url}/dp/{product.asin}"
            
            # Title
            title_el = card.select_one('h2 a span') or card.select_one('[data-cy="title-recipe"] span')
            if title_el:
                product.title = title_el.get_text(strip=True)
            
            # Price
            price_el = card.select_one('.a-price .a-offscreen')
            if price_el:
                price_text = price_el.get_text(strip=True)
                match = re.search(r'[\d,.]+', price_text.replace(',', ''))
                if match:
                    product.price = float(match.group())
            
            # Rating
            rating_el = card.select_one('[aria-label*="out of 5 stars"]')
            if rating_el:
                label = rating_el.get('aria-label', '')
                match = re.search(r'([\d.]+)\s*out of', label)
                if match:
                    product.rating = float(match.group(1))
            
            # Review count
            review_el = card.select_one('[aria-label*="stars"] + span a span')
            if review_el:
                text = review_el.get_text()
                match = re.search(r'[\d,]+', text)
                if match:
                    product.review_count = int(match.group().replace(',', ''))
            
            # Image
            img_el = card.select_one('img.s-image')
            if img_el:
                product.images = [img_el.get('src')]
            
            from datetime import datetime
            product.scraped_at = datetime.now().isoformat()
            
            return product
            
        except Exception as e:
            print(f"Error parsing card: {e}")
            return None
    
    def get_product(self, asin: str) -> Optional[AmazonProduct]:
        """
        Get detailed product information by ASIN.
        
        Args:
            asin: Amazon Standard Identification Number
            
        Returns:
            AmazonProduct or None
        """
        url = f"{self.base_url}/dp/{asin}"
        soup = self._request(url)
        
        if not soup:
            return None
        
        return self._parse_product_page(soup, asin, url)
    
    def _parse_product_page(self, soup: BeautifulSoup, 
                           asin: str, url: str) -> Optional[AmazonProduct]:
        """Parse product detail page."""
        try:
            product = AmazonProduct(asin=asin, url=url)
            
            # Title
            title_el = soup.select_one('#productTitle')
            if title_el:
                product.title = title_el.get_text(strip=True)
            
            # Price - multiple possible locations
            price_el = (
                soup.select_one('.a-price .a-offscreen') or
                soup.select_one('#priceblock_ourprice') or
                soup.select_one('#priceblock_dealprice') or
                soup.select_one('.apexPriceToPay .a-offscreen')
            )
            if price_el:
                price_text = price_el.get_text(strip=True)
                match = re.search(r'[\d,.]+', price_text.replace(',', ''))
                if match:
                    product.price = float(match.group())
            
            # Original price (if on sale)
            orig_el = soup.select_one('.a-text-price .a-offscreen')
            if orig_el:
                text = orig_el.get_text()
                match = re.search(r'[\d,.]+', text.replace(',', ''))
                if match:
                    product.original_price = float(match.group())
            
            # Rating
            rating_el = soup.select_one('#acrPopover')
            if rating_el:
                label = rating_el.get('title', '')
                match = re.search(r'([\d.]+)', label)
                if match:
                    product.rating = float(match.group(1))
            
            # Review count
            review_el = soup.select_one('#acrCustomerReviewText')
            if review_el:
                text = review_el.get_text()
                match = re.search(r'[\d,]+', text)
                if match:
                    product.review_count = int(match.group().replace(',', ''))
            
            # Brand
            brand_el = soup.select_one('#bylineInfo') or soup.select_one('a#brand')
            if brand_el:
                product.brand = brand_el.get_text(strip=True).replace('Visit the ', '').replace(' Store', '')
            
            # Availability
            avail_el = soup.select_one('#availability span')
            if avail_el:
                product.availability = avail_el.get_text(strip=True)
            
            # Features (bullet points)
            feature_els = soup.select('#feature-bullets li span')
            product.features = [f.get_text(strip=True) for f in feature_els if f.get_text(strip=True)]
            
            # Description
            desc_el = soup.select_one('#productDescription p')
            if desc_el:
                product.description = desc_el.get_text(strip=True)
            
            # Images
            img_scripts = soup.select('script:-soup-contains("ImageBlockATF")')
            for script in img_scripts:
                text = script.string or ''
                urls = re.findall(r'"hiRes":"(https://[^"]+)"', text)
                if urls:
                    product.images = urls[:10]
                    break
            
            # Fallback for main image
            if not product.images:
                main_img = soup.select_one('#landingImage')
                if main_img:
                    product.images = [main_img.get('src') or main_img.get('data-old-hires')]
            
            # Categories (breadcrumb)
            breadcrumb_els = soup.select('#wayfinding-breadcrumbs_container li a')
            product.categories = [b.get_text(strip=True) for b in breadcrumb_els]
            
            from datetime import datetime
            product.scraped_at = datetime.now().isoformat()
            
            return product
            
        except Exception as e:
            print(f"Error parsing product page: {e}")
            return None


def search_amazon(query: str, max_results: int = 20) -> List[Dict]:
    """Search Amazon for products."""
    ant = AmazonAnt()
    results = ant.search(query, max_results)
    return [r.to_dict() for r in results]


def get_amazon_product(asin: str) -> Optional[Dict]:
    """Get Amazon product by ASIN."""
    ant = AmazonAnt()
    product = ant.get_product(asin)
    return product.to_dict() if product else None


if __name__ == '__main__':
    print("⚠️ Amazon scraping will likely trigger CAPTCHA")
    print("   Use official APIs for production")
    print()
    
    # Example - may not work due to anti-bot
    results = search_amazon("wireless headphones", max_results=5)
    for p in results:
        print(f"{p['title'][:50]}... - ${p['price']}")
