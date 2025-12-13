"""
Better Business Bureau Scraper

For educational purposes.
"""

import re
import time
import random
from typing import Optional, List, Dict
from dataclasses import dataclass, field, asdict
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import requests


@dataclass
class BBBBusiness:
    """Data model for a BBB business."""
    business_id: Optional[str] = None
    url: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[str] = None  # A+, A, B, etc.
    accredited: bool = False
    years_in_business: Optional[int] = None
    categories: List[str] = field(default_factory=list)
    
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class BBBAnt:
    """BBB business scraper."""
    
    BASE_URL = "https://www.bbb.org"
    
    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        })
    
    def _request(self, url: str) -> Optional[BeautifulSoup]:
        time.sleep(self.delay + random.random())
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'lxml')
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def search(self, query: str, location: str = "",
               max_results: int = 20) -> List[BBBBusiness]:
        """Search for businesses."""
        url = f"{self.BASE_URL}/search?find_text={quote_plus(query)}&find_loc={quote_plus(location)}"
        soup = self._request(url)
        
        if not soup:
            return []
        
        results = []
        cards = soup.select('.search-results .result-item') or soup.select('[data-testid="search-result"]')
        
        for card in cards[:max_results]:
            biz = self._parse_business_card(card)
            if biz and biz.name:
                results.append(biz)
                print(f"  Found: {biz.name} - {biz.rating}")
        
        return results
    
    def _parse_business_card(self, card) -> Optional[BBBBusiness]:
        try:
            biz = BBBBusiness()
            
            # Name and URL
            name_el = card.select_one('.business-name a') or card.select_one('h3 a')
            if name_el:
                biz.name = name_el.get_text(strip=True)
                href = name_el.get('href', '')
                biz.url = self.BASE_URL + href if href.startswith('/') else href
            
            # Rating
            rating_el = card.select_one('.bbb-rating') or card.select_one('[class*="rating"]')
            if rating_el:
                biz.rating = rating_el.get_text(strip=True)
            
            # Accredited
            accred_el = card.select_one('.accredited') or card.select_one('[class*="accredited"]')
            biz.accredited = bool(accred_el)
            
            # Address
            addr_el = card.select_one('.address') or card.select_one('[class*="address"]')
            if addr_el:
                biz.address = addr_el.get_text(strip=True)
            
            # Phone
            phone_el = card.select_one('.phone') or card.select_one('[class*="phone"]')
            if phone_el:
                biz.phone = phone_el.get_text(strip=True)
            
            # Categories
            cat_els = card.select('.category') or card.select('[class*="category"]')
            biz.categories = [c.get_text(strip=True) for c in cat_els]
            
            from datetime import datetime
            biz.scraped_at = datetime.now().isoformat()
            
            return biz
        except:
            return None


def search_bbb(query: str, location: str = "", max_results: int = 20) -> List[Dict]:
    ant = BBBAnt()
    results = ant.search(query, location, max_results)
    return [r.to_dict() for r in results]


if __name__ == '__main__':
    results = search_bbb("plumber", "Denver, CO", max_results=10)
    for biz in results:
        accred = "Accredited" if biz['accredited'] else "Not Accredited"
        print(f"{biz['name']} - {biz['rating']} ({accred})")
