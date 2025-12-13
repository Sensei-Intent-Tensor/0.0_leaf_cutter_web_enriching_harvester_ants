"""
Google Maps Scraper

WARNING: This is for educational purposes only. 
Google's ToS prohibits scraping. Use the official Places API for production.
"""

import re
import json
import time
import random
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from urllib.parse import quote_plus, urlencode

# For browser automation
try:
    from playwright.sync_api import sync_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


@dataclass
class GoogleMapsPlace:
    """Data model for a Google Maps place."""
    place_id: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    price_level: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    hours: Dict[str, str] = field(default_factory=dict)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photos: List[str] = field(default_factory=list)
    
    # Metadata
    url: Optional[str] = None
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class GoogleMapsAnt:
    """
    Google Maps scraper using Playwright.
    
    Usage:
        ant = GoogleMapsAnt()
        results = ant.search("coffee shops", "San Francisco, CA", max_results=20)
        ant.close()
    """
    
    BASE_URL = "https://www.google.com/maps"
    
    def __init__(self, headless: bool = True, proxy: Optional[str] = None):
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("playwright required: pip install playwright && playwright install")
        
        self.headless = headless
        self.proxy = proxy
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
    def _init_browser(self):
        """Initialize browser if not already running."""
        if self.browser is not None:
            return
            
        self.playwright = sync_playwright().start()
        
        launch_options = {
            'headless': self.headless,
        }
        
        if self.proxy:
            launch_options['proxy'] = {'server': self.proxy}
        
        self.browser = self.playwright.chromium.launch(**launch_options)
        
        # Create context with realistic viewport
        context = self.browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
        )
        
        self.page = context.new_page()
        
    def search(self, query: str, location: str = "", 
               max_results: int = 20) -> List[GoogleMapsPlace]:
        """
        Search Google Maps for businesses.
        
        Args:
            query: Search query (e.g., "coffee shops")
            location: Location to search (e.g., "San Francisco, CA")
            max_results: Maximum results to return
            
        Returns:
            List of GoogleMapsPlace objects
        """
        self._init_browser()
        
        # Build search URL
        search_term = f"{query} {location}".strip()
        url = f"{self.BASE_URL}/search/{quote_plus(search_term)}"
        
        print(f"Searching: {search_term}")
        self.page.goto(url, wait_until='networkidle')
        
        # Wait for results to load
        time.sleep(2 + random.random() * 2)
        
        # Accept cookies if prompted
        self._handle_consent()
        
        results = []
        seen_names = set()
        
        # Scroll and collect results
        scroll_attempts = 0
        max_scroll_attempts = max_results // 5 + 5
        
        while len(results) < max_results and scroll_attempts < max_scroll_attempts:
            # Find result elements
            items = self.page.query_selector_all('[role="feed"] > div > div > a')
            
            for item in items:
                if len(results) >= max_results:
                    break
                    
                try:
                    name = item.get_attribute('aria-label')
                    if not name or name in seen_names:
                        continue
                    
                    seen_names.add(name)
                    
                    # Click to get details
                    place = self._extract_from_list_item(item, name)
                    if place:
                        results.append(place)
                        print(f"  Found: {place.name}")
                        
                except Exception as e:
                    print(f"  Error extracting item: {e}")
                    continue
            
            # Scroll for more results
            self._scroll_results()
            scroll_attempts += 1
            time.sleep(1 + random.random())
        
        return results
    
    def get_place_details(self, place_url: str) -> Optional[GoogleMapsPlace]:
        """Get detailed information for a specific place."""
        self._init_browser()
        
        self.page.goto(place_url, wait_until='networkidle')
        time.sleep(2 + random.random())
        
        self._handle_consent()
        
        return self._extract_place_details()
    
    def _handle_consent(self):
        """Handle cookie consent dialog."""
        try:
            consent_btn = self.page.query_selector('button:has-text("Accept all")')
            if consent_btn:
                consent_btn.click()
                time.sleep(1)
        except:
            pass
    
    def _scroll_results(self):
        """Scroll the results panel."""
        try:
            feed = self.page.query_selector('[role="feed"]')
            if feed:
                feed.evaluate('el => el.scrollTop += 500')
        except:
            pass
    
    def _extract_from_list_item(self, item, name: str) -> Optional[GoogleMapsPlace]:
        """Extract basic info from search result item."""
        try:
            place = GoogleMapsPlace(name=name)
            
            # Get URL which contains place_id
            href = item.get_attribute('href')
            place.url = href
            
            # Extract place_id from URL
            if href and 'place/' in href:
                # URL format: /maps/place/Name/data=...
                place_match = re.search(r'!1s([^!]+)', href)
                if place_match:
                    place.place_id = place_match.group(1)
            
            # Get parent container for more details
            container = item.evaluate_handle('el => el.closest("div")').as_element()
            if container:
                text = container.inner_text()
                
                # Extract rating
                rating_match = re.search(r'(\d+\.?\d*)\s*stars?', text, re.IGNORECASE)
                if not rating_match:
                    rating_match = re.search(r'(\d+\.?\d*)\s*\(', text)
                if rating_match:
                    place.rating = float(rating_match.group(1))
                
                # Extract review count
                review_match = re.search(r'\((\d+(?:,\d+)*)\)', text)
                if review_match:
                    place.review_count = int(review_match.group(1).replace(',', ''))
                
                # Extract price level
                price_match = re.search(r'(\${1,4})', text)
                if price_match:
                    place.price_level = price_match.group(1)
            
            from datetime import datetime
            place.scraped_at = datetime.now().isoformat()
            
            return place
            
        except Exception as e:
            print(f"Error extracting: {e}")
            return None
    
    def _extract_place_details(self) -> Optional[GoogleMapsPlace]:
        """Extract full details from place page."""
        try:
            place = GoogleMapsPlace()
            place.url = self.page.url
            
            # Name
            name_el = self.page.query_selector('h1')
            if name_el:
                place.name = name_el.inner_text()
            
            # Rating
            rating_el = self.page.query_selector('[role="img"][aria-label*="stars"]')
            if rating_el:
                label = rating_el.get_attribute('aria-label')
                rating_match = re.search(r'(\d+\.?\d*)', label)
                if rating_match:
                    place.rating = float(rating_match.group(1))
            
            # Review count
            review_el = self.page.query_selector('button[aria-label*="reviews"]')
            if review_el:
                label = review_el.get_attribute('aria-label')
                count_match = re.search(r'(\d+(?:,\d+)*)', label)
                if count_match:
                    place.review_count = int(count_match.group(1).replace(',', ''))
            
            # Address
            addr_el = self.page.query_selector('[data-item-id="address"]')
            if addr_el:
                place.address = addr_el.inner_text()
            
            # Phone
            phone_el = self.page.query_selector('[data-item-id^="phone"]')
            if phone_el:
                place.phone = phone_el.inner_text()
            
            # Website
            web_el = self.page.query_selector('[data-item-id="authority"]')
            if web_el:
                place.website = web_el.get_attribute('href')
            
            # Categories
            cat_els = self.page.query_selector_all('button[jsaction*="category"]')
            place.categories = [el.inner_text() for el in cat_els if el.inner_text()]
            
            from datetime import datetime
            place.scraped_at = datetime.now().isoformat()
            
            return place
            
        except Exception as e:
            print(f"Error extracting details: {e}")
            return None
    
    def close(self):
        """Close browser and cleanup."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()


# Convenience function
def search_google_maps(query: str, location: str = "", 
                       max_results: int = 20) -> List[Dict]:
    """
    Search Google Maps and return results.
    
    Args:
        query: What to search for
        location: Where to search
        max_results: Maximum results
        
    Returns:
        List of place dictionaries
    """
    ant = GoogleMapsAnt(headless=True)
    try:
        results = ant.search(query, location, max_results)
        return [r.to_dict() for r in results]
    finally:
        ant.close()


if __name__ == '__main__':
    # Example usage
    results = search_google_maps(
        query="coffee shops",
        location="San Francisco, CA",
        max_results=10
    )
    
    for place in results:
        print(f"{place['name']} - {place['rating']} stars")
