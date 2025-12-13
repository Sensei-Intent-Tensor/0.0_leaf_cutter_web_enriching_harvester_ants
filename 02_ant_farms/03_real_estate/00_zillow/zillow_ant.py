"""
Zillow Property Scraper

WARNING: For educational purposes only. 
Zillow prohibits scraping. Use official APIs or licensed data for production.
"""

import re
import json
import time
import random
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from urllib.parse import quote_plus, urlencode
from bs4 import BeautifulSoup
import requests


@dataclass
class ZillowProperty:
    """Data model for a Zillow property listing."""
    zpid: Optional[str] = None
    url: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None
    price: Optional[int] = None
    zestimate: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    sqft: Optional[int] = None
    lot_sqft: Optional[int] = None
    year_built: Optional[int] = None
    property_type: Optional[str] = None
    listing_status: Optional[str] = None
    days_on_zillow: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photos: List[str] = field(default_factory=list)
    
    # Metadata
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ZillowAnt:
    """
    Zillow property scraper.
    
    Note: Zillow has strong anti-scraping measures. This may not work
    reliably. For production, use official data sources.
    
    Usage:
        ant = ZillowAnt()
        results = ant.search_for_sale("San Francisco, CA", max_results=20)
    """
    
    BASE_URL = "https://www.zillow.com"
    
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
    
    def _request(self, url: str) -> Optional[str]:
        """Make request with rate limiting."""
        time.sleep(self.delay + random.random() * 2)
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def search_for_sale(self, location: str, 
                        max_results: int = 20) -> List[ZillowProperty]:
        """
        Search for properties for sale.
        
        Args:
            location: City, State or ZIP code
            max_results: Maximum results to return
            
        Returns:
            List of ZillowProperty objects
        """
        # Zillow uses location slugs in URLs
        location_slug = location.lower().replace(', ', '-').replace(' ', '-')
        url = f"{self.BASE_URL}/{location_slug}/"
        
        print(f"Searching: {location}")
        html = self._request(url)
        
        if not html:
            return []
        
        return self._parse_search_results(html, max_results)
    
    def _parse_search_results(self, html: str, 
                              max_results: int) -> List[ZillowProperty]:
        """Parse search results page."""
        results = []
        
        try:
            # Zillow embeds data in a script tag
            # Look for the preloaded state
            soup = BeautifulSoup(html, 'lxml')
            
            # Try to find JSON data
            for script in soup.select('script'):
                text = script.string or ''
                
                # Look for search results data
                if 'listResults' in text or 'searchResults' in text:
                    # Extract JSON from script
                    json_match = re.search(r'(\{.+\})', text, re.DOTALL)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            results.extend(self._extract_from_json(data, max_results))
                            break
                        except:
                            continue
            
            # Fallback: parse HTML cards
            if not results:
                cards = soup.select('[data-test="property-card"]')
                for card in cards[:max_results]:
                    prop = self._parse_property_card(card)
                    if prop:
                        results.append(prop)
            
        except Exception as e:
            print(f"Error parsing results: {e}")
        
        return results[:max_results]
    
    def _extract_from_json(self, data: Dict, 
                           max_results: int) -> List[ZillowProperty]:
        """Extract properties from JSON data."""
        results = []
        
        # Navigate to results (structure varies)
        list_results = None
        
        if 'cat1' in data:
            list_results = data['cat1'].get('searchResults', {}).get('listResults', [])
        elif 'searchResults' in data:
            list_results = data['searchResults'].get('listResults', [])
        elif 'listResults' in data:
            list_results = data['listResults']
        
        if not list_results:
            return results
        
        for item in list_results[:max_results]:
            try:
                prop = ZillowProperty()
                
                prop.zpid = str(item.get('zpid', ''))
                prop.url = item.get('detailUrl', '')
                if prop.url and not prop.url.startswith('http'):
                    prop.url = self.BASE_URL + prop.url
                
                prop.address = item.get('address', '')
                
                # Parse address components
                addr_parts = prop.address.split(', ') if prop.address else []
                if len(addr_parts) >= 2:
                    state_zip = addr_parts[-1].split(' ')
                    if len(state_zip) >= 2:
                        prop.state = state_zip[0]
                        prop.zipcode = state_zip[-1]
                    prop.city = addr_parts[-2] if len(addr_parts) >= 2 else None
                
                # Price
                price_str = item.get('price', '')
                if isinstance(price_str, str):
                    price_match = re.search(r'[\d,]+', price_str.replace(',', ''))
                    if price_match:
                        prop.price = int(price_match.group().replace(',', ''))
                elif isinstance(price_str, (int, float)):
                    prop.price = int(price_str)
                
                # Zestimate
                zest = item.get('zestimate')
                if zest:
                    prop.zestimate = int(zest) if isinstance(zest, (int, float)) else None
                
                # Beds/Baths
                prop.bedrooms = item.get('beds')
                prop.bathrooms = item.get('baths')
                
                # Square footage
                prop.sqft = item.get('area')
                
                # Coordinates
                if 'latLong' in item:
                    prop.latitude = item['latLong'].get('latitude')
                    prop.longitude = item['latLong'].get('longitude')
                
                # Status
                prop.listing_status = item.get('statusType', '').upper()
                
                # Photos
                if 'carouselPhotos' in item:
                    prop.photos = [p.get('url') for p in item['carouselPhotos'][:5] if p.get('url')]
                
                from datetime import datetime
                prop.scraped_at = datetime.now().isoformat()
                
                results.append(prop)
                
            except Exception as e:
                print(f"Error parsing property: {e}")
                continue
        
        return results
    
    def _parse_property_card(self, card) -> Optional[ZillowProperty]:
        """Parse HTML property card (fallback)."""
        try:
            prop = ZillowProperty()
            
            # Link and ZPID
            link = card.select_one('a[href*="/homedetails/"]')
            if link:
                prop.url = link.get('href', '')
                zpid_match = re.search(r'/(\d+)_zpid', prop.url)
                if zpid_match:
                    prop.zpid = zpid_match.group(1)
            
            # Address
            addr_el = card.select_one('[data-test="property-card-addr"]')
            if addr_el:
                prop.address = addr_el.get_text(strip=True)
            
            # Price
            price_el = card.select_one('[data-test="property-card-price"]')
            if price_el:
                price_text = price_el.get_text()
                match = re.search(r'\$([\d,]+)', price_text)
                if match:
                    prop.price = int(match.group(1).replace(',', ''))
            
            # Beds/baths/sqft
            details_el = card.select_one('[data-test="property-card-details"]')
            if details_el:
                text = details_el.get_text()
                
                beds_match = re.search(r'(\d+)\s*bd', text, re.I)
                if beds_match:
                    prop.bedrooms = int(beds_match.group(1))
                
                baths_match = re.search(r'([\d.]+)\s*ba', text, re.I)
                if baths_match:
                    prop.bathrooms = float(baths_match.group(1))
                
                sqft_match = re.search(r'([\d,]+)\s*sqft', text, re.I)
                if sqft_match:
                    prop.sqft = int(sqft_match.group(1).replace(',', ''))
            
            from datetime import datetime
            prop.scraped_at = datetime.now().isoformat()
            
            return prop if prop.address else None
            
        except Exception as e:
            print(f"Error parsing card: {e}")
            return None
    
    def get_property_details(self, zpid: str) -> Optional[ZillowProperty]:
        """Get detailed property information by ZPID."""
        url = f"{self.BASE_URL}/homedetails/{zpid}_zpid/"
        html = self._request(url)
        
        if not html:
            return None
        
        return self._parse_property_page(html, zpid)
    
    def _parse_property_page(self, html: str, zpid: str) -> Optional[ZillowProperty]:
        """Parse property detail page."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            prop = ZillowProperty(zpid=zpid)
            
            # Try to find JSON-LD
            for script in soup.select('script[type="application/ld+json"]'):
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and '@type' in data:
                        if 'Residence' in data.get('@type', '') or 'Product' in data.get('@type', ''):
                            prop.address = data.get('name')
                            if 'offers' in data:
                                offer = data['offers']
                                prop.price = int(float(offer.get('price', 0)))
                            if 'geo' in data:
                                prop.latitude = data['geo'].get('latitude')
                                prop.longitude = data['geo'].get('longitude')
                except:
                    continue
            
            from datetime import datetime
            prop.scraped_at = datetime.now().isoformat()
            
            return prop
            
        except Exception as e:
            print(f"Error parsing property page: {e}")
            return None


def search_zillow(location: str, max_results: int = 20) -> List[Dict]:
    """
    Search Zillow for properties.
    
    Args:
        location: City, State or ZIP
        max_results: Maximum results
        
    Returns:
        List of property dictionaries
    """
    ant = ZillowAnt()
    results = ant.search_for_sale(location, max_results)
    return [r.to_dict() for r in results]


if __name__ == '__main__':
    results = search_zillow("Austin, TX", max_results=10)
    
    for prop in results:
        print(f"{prop['address']} - ${prop['price']:,} - {prop['bedrooms']}bd/{prop['bathrooms']}ba")
