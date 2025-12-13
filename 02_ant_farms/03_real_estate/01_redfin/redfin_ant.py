"""
Redfin Property Scraper

For educational purposes. Consider Redfin data partnerships for production.
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
class RedfinProperty:
    """Data model for a Redfin property."""
    property_id: Optional[str] = None
    url: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None
    price: Optional[int] = None
    beds: Optional[int] = None
    baths: Optional[float] = None
    sqft: Optional[int] = None
    lot_sqft: Optional[int] = None
    year_built: Optional[int] = None
    property_type: Optional[str] = None
    status: Optional[str] = None
    hoa_fee: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photos: List[str] = field(default_factory=list)
    
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class RedfinAnt:
    """Redfin property scraper."""
    
    BASE_URL = "https://www.redfin.com"
    
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
        })
    
    def _request(self, url: str) -> Optional[str]:
        time.sleep(self.delay + random.random() * 2)
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def search(self, location: str, max_results: int = 20) -> List[RedfinProperty]:
        """Search for properties in a location."""
        # Redfin uses location-based URLs
        location_slug = location.lower().replace(', ', '-').replace(' ', '-')
        url = f"{self.BASE_URL}/city/12345/{location_slug}"
        
        # Try the stingray API endpoint
        api_url = f"{self.BASE_URL}/stingray/api/gis?al=1&num_homes=50&sf=1,2,3,5,6,7&status=9&v=8"
        
        html = self._request(url)
        if not html:
            return []
        
        return self._parse_search_results(html, max_results)
    
    def _parse_search_results(self, html: str, max_results: int) -> List[RedfinProperty]:
        results = []
        soup = BeautifulSoup(html, 'lxml')
        
        # Find JSON data in scripts
        for script in soup.select('script'):
            text = script.string or ''
            if 'reactServerState' in text or 'homes' in text:
                try:
                    # Extract JSON
                    match = re.search(r'window\.__PRELOADED_STATE__\s*=\s*({.+?});', text, re.DOTALL)
                    if match:
                        data = json.loads(match.group(1))
                        homes = self._find_homes_in_json(data)
                        for home in homes[:max_results]:
                            prop = self._parse_json_home(home)
                            if prop:
                                results.append(prop)
                        break
                except:
                    continue
        
        # Fallback to HTML parsing
        if not results:
            cards = soup.select('.HomeCardContainer')
            for card in cards[:max_results]:
                prop = self._parse_property_card(card)
                if prop:
                    results.append(prop)
        
        return results
    
    def _find_homes_in_json(self, data, depth=0) -> List[Dict]:
        if depth > 10:
            return []
        
        homes = []
        
        if isinstance(data, dict):
            if 'propertyId' in data and 'price' in data:
                homes.append(data)
            for v in data.values():
                homes.extend(self._find_homes_in_json(v, depth + 1))
        elif isinstance(data, list):
            for item in data:
                homes.extend(self._find_homes_in_json(item, depth + 1))
        
        return homes
    
    def _parse_json_home(self, home: Dict) -> Optional[RedfinProperty]:
        try:
            prop = RedfinProperty()
            
            prop.property_id = str(home.get('propertyId', ''))
            prop.url = self.BASE_URL + home.get('url', '')
            prop.price = home.get('price', {}).get('value') or home.get('price')
            prop.beds = home.get('beds')
            prop.baths = home.get('baths')
            prop.sqft = home.get('sqFt', {}).get('value') or home.get('sqFt')
            prop.status = home.get('listingType')
            
            # Address
            addr = home.get('streetLine', {})
            if isinstance(addr, dict):
                prop.address = addr.get('value')
            else:
                prop.address = home.get('streetAddress')
            
            prop.city = home.get('city')
            prop.state = home.get('state')
            prop.zipcode = home.get('zip')
            
            # Coordinates
            prop.latitude = home.get('latLong', {}).get('latitude') or home.get('latitude')
            prop.longitude = home.get('latLong', {}).get('longitude') or home.get('longitude')
            
            from datetime import datetime
            prop.scraped_at = datetime.now().isoformat()
            
            return prop
        except:
            return None
    
    def _parse_property_card(self, card) -> Optional[RedfinProperty]:
        try:
            prop = RedfinProperty()
            
            link = card.select_one('a[href*="/home/"]')
            if link:
                prop.url = self.BASE_URL + link.get('href', '')
                match = re.search(r'/(\d+)$', prop.url)
                if match:
                    prop.property_id = match.group(1)
            
            addr_el = card.select_one('.homeAddressV2')
            if addr_el:
                prop.address = addr_el.get_text(strip=True)
            
            price_el = card.select_one('.homePriceV2')
            if price_el:
                match = re.search(r'[\d,]+', price_el.get_text().replace(',', ''))
                if match:
                    prop.price = int(match.group())
            
            stats = card.select('.HomeStatsV2 .stats')
            for stat in stats:
                text = stat.get_text(strip=True).lower()
                val = re.search(r'([\d.]+)', text)
                if val:
                    if 'bed' in text:
                        prop.beds = int(float(val.group(1)))
                    elif 'bath' in text:
                        prop.baths = float(val.group(1))
                    elif 'sq' in text:
                        prop.sqft = int(val.group(1).replace(',', ''))
            
            from datetime import datetime
            prop.scraped_at = datetime.now().isoformat()
            
            return prop
        except:
            return None


def search_redfin(location: str, max_results: int = 20) -> List[Dict]:
    ant = RedfinAnt()
    results = ant.search(location, max_results)
    return [r.to_dict() for r in results]


if __name__ == '__main__':
    results = search_redfin("Seattle, WA", max_results=10)
    for p in results:
        print(f"{p['address']} - ${p['price']:,} - {p['beds']}bd/{p['baths']}ba")
