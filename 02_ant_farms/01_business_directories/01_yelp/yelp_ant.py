"""
Yelp Scraper

WARNING: For educational purposes. Use Yelp Fusion API for production.
https://www.yelp.com/developers/documentation/v3
"""

import re
import json
import time
import random
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
import requests


@dataclass
class YelpBusiness:
    """Data model for a Yelp business."""
    business_id: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    price_range: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    hours: Dict[str, str] = field(default_factory=dict)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photos: List[str] = field(default_factory=list)
    
    # Metadata
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class YelpAnt:
    """
    Yelp scraper using requests + BeautifulSoup.
    
    Usage:
        ant = YelpAnt()
        results = ant.search("pizza", "New York, NY", max_results=20)
    """
    
    BASE_URL = "https://www.yelp.com"
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    ]
    
    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.session = requests.Session()
        self._update_headers()
    
    def _update_headers(self):
        """Set random user agent."""
        self.session.headers.update({
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        })
    
    def _request(self, url: str) -> Optional[BeautifulSoup]:
        """Make request with rate limiting."""
        time.sleep(self.delay + random.random())
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'lxml')
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def search(self, query: str, location: str, 
               max_results: int = 20) -> List[YelpBusiness]:
        """
        Search Yelp for businesses.
        
        Args:
            query: Search term (e.g., "pizza")
            location: Location (e.g., "New York, NY")
            max_results: Maximum results to return
            
        Returns:
            List of YelpBusiness objects
        """
        results = []
        start = 0
        
        while len(results) < max_results:
            url = (f"{self.BASE_URL}/search?"
                   f"find_desc={quote_plus(query)}&"
                   f"find_loc={quote_plus(location)}&"
                   f"start={start}")
            
            print(f"Fetching page {start // 10 + 1}...")
            soup = self._request(url)
            
            if not soup:
                break
            
            # Find business cards
            cards = soup.select('[data-testid="serp-ia-card"]')
            
            if not cards:
                # Try alternative selector
                cards = soup.select('.container__09f24__FeTO6')
            
            if not cards:
                print("No results found or page structure changed")
                break
            
            for card in cards:
                if len(results) >= max_results:
                    break
                
                business = self._parse_search_card(card)
                if business and business.name:
                    results.append(business)
                    print(f"  Found: {business.name}")
            
            # Check for more pages
            if len(cards) < 10:
                break
                
            start += 10
        
        return results
    
    def _parse_search_card(self, card) -> Optional[YelpBusiness]:
        """Parse a search result card."""
        try:
            business = YelpBusiness()
            
            # Name and URL
            name_link = card.select_one('a[href*="/biz/"]')
            if name_link:
                business.name = name_link.get_text(strip=True)
                href = name_link.get('href', '')
                business.url = urljoin(self.BASE_URL, href)
                # Extract business ID from URL
                if '/biz/' in href:
                    business.business_id = href.split('/biz/')[-1].split('?')[0]
            
            # Rating
            rating_el = card.select_one('[aria-label*="star rating"]')
            if rating_el:
                label = rating_el.get('aria-label', '')
                rating_match = re.search(r'(\d+\.?\d*)', label)
                if rating_match:
                    business.rating = float(rating_match.group(1))
            
            # Review count
            review_el = card.select_one('span:-soup-contains("reviews")')
            if not review_el:
                review_el = card.select_one('[class*="reviewCount"]')
            if review_el:
                text = review_el.get_text()
                count_match = re.search(r'(\d+)', text)
                if count_match:
                    business.review_count = int(count_match.group(1))
            
            # Price range
            price_el = card.select_one('span:-soup-contains("$")')
            if price_el:
                price_text = price_el.get_text(strip=True)
                if re.match(r'^\$+$', price_text):
                    business.price_range = price_text
            
            # Categories
            cat_links = card.select('a[href*="/search?cflt="]')
            business.categories = [c.get_text(strip=True) for c in cat_links]
            
            # Address
            addr_el = card.select_one('[class*="secondaryAttributes"]')
            if addr_el:
                business.address = addr_el.get_text(strip=True)
            
            from datetime import datetime
            business.scraped_at = datetime.now().isoformat()
            
            return business
            
        except Exception as e:
            print(f"Error parsing card: {e}")
            return None
    
    def get_business_details(self, business_url: str) -> Optional[YelpBusiness]:
        """Get detailed information for a business."""
        soup = self._request(business_url)
        if not soup:
            return None
        
        return self._parse_business_page(soup, business_url)
    
    def _parse_business_page(self, soup: BeautifulSoup, 
                             url: str) -> Optional[YelpBusiness]:
        """Parse a business detail page."""
        try:
            business = YelpBusiness(url=url)
            
            # Name
            name_el = soup.select_one('h1')
            if name_el:
                business.name = name_el.get_text(strip=True)
            
            # Rating
            rating_el = soup.select_one('[aria-label*="star rating"]')
            if rating_el:
                label = rating_el.get('aria-label', '')
                match = re.search(r'(\d+\.?\d*)', label)
                if match:
                    business.rating = float(match.group(1))
            
            # Review count  
            review_el = soup.select_one('a[href*="#reviews"]')
            if review_el:
                match = re.search(r'(\d+)', review_el.get_text())
                if match:
                    business.review_count = int(match.group(1))
            
            # Address
            addr_el = soup.select_one('[class*="address"]')
            if addr_el:
                business.address = addr_el.get_text(strip=True)
            
            # Phone
            phone_el = soup.select_one('p:-soup-contains("Phone number")')
            if phone_el:
                phone_text = phone_el.find_next('p')
                if phone_text:
                    business.phone = phone_text.get_text(strip=True)
            
            # Website
            web_link = soup.select_one('a[href*="/biz_redir"]')
            if web_link:
                business.website = web_link.get('href')
            
            # Categories
            cat_links = soup.select('a[href*="/search?cflt="]')
            business.categories = list(set(
                c.get_text(strip=True) for c in cat_links if c.get_text(strip=True)
            ))
            
            # Photos
            photo_els = soup.select('img[src*="bphoto"]')
            business.photos = [img.get('src') for img in photo_els[:10] if img.get('src')]
            
            # Extract JSON-LD if available
            script = soup.select_one('script[type="application/ld+json"]')
            if script:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        if 'aggregateRating' in data:
                            business.rating = float(data['aggregateRating'].get('ratingValue', business.rating))
                            business.review_count = int(data['aggregateRating'].get('reviewCount', business.review_count or 0))
                        if 'address' in data:
                            addr = data['address']
                            business.city = addr.get('addressLocality')
                            business.state = addr.get('addressRegion')
                            business.zip_code = addr.get('postalCode')
                        if 'geo' in data:
                            business.latitude = float(data['geo'].get('latitude', 0))
                            business.longitude = float(data['geo'].get('longitude', 0))
                except:
                    pass
            
            from datetime import datetime
            business.scraped_at = datetime.now().isoformat()
            
            return business
            
        except Exception as e:
            print(f"Error parsing business page: {e}")
            return None


def search_yelp(query: str, location: str, max_results: int = 20) -> List[Dict]:
    """
    Search Yelp and return results.
    
    Args:
        query: What to search for
        location: Where to search
        max_results: Maximum results
        
    Returns:
        List of business dictionaries
    """
    ant = YelpAnt()
    results = ant.search(query, location, max_results)
    return [r.to_dict() for r in results]


if __name__ == '__main__':
    # Example usage
    results = search_yelp(
        query="pizza",
        location="New York, NY",
        max_results=10
    )
    
    for biz in results:
        print(f"{biz['name']} - {biz['rating']} stars ({biz['review_count']} reviews)")
