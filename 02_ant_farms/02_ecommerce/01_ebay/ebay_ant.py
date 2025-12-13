"""
eBay Listings Scraper

WARNING: For educational purposes. Use eBay APIs for production.
https://developer.ebay.com/api-docs
"""

import re
import json
import time
import random
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import requests


@dataclass
class EbayListing:
    """Data model for an eBay listing."""
    item_id: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    price: Optional[float] = None
    currency: str = "USD"
    shipping_cost: Optional[float] = None
    condition: Optional[str] = None
    listing_type: Optional[str] = None  # auction, buy_it_now
    bids: Optional[int] = None
    time_left: Optional[str] = None
    seller: Optional[str] = None
    seller_feedback: Optional[float] = None
    location: Optional[str] = None
    images: List[str] = field(default_factory=list)
    item_specifics: Dict[str, str] = field(default_factory=dict)
    
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class EbayAnt:
    """
    eBay listings scraper.
    
    Usage:
        ant = EbayAnt()
        results = ant.search("vintage watch", max_results=20)
    """
    
    BASE_URL = "https://www.ebay.com"
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    ]
    
    def __init__(self, delay: float = 2.0):
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
        time.sleep(self.delay + random.random())
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'lxml')
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def search(self, query: str, max_results: int = 20, 
               listing_type: str = None) -> List[EbayListing]:
        """
        Search eBay listings.
        
        Args:
            query: Search query
            max_results: Maximum results
            listing_type: 'auction' or 'buy_it_now' (optional)
        """
        url = f"{self.BASE_URL}/sch/i.html?_nkw={quote_plus(query)}"
        
        if listing_type == 'auction':
            url += "&LH_Auction=1"
        elif listing_type == 'buy_it_now':
            url += "&LH_BIN=1"
        
        soup = self._request(url)
        if not soup:
            return []
        
        results = []
        cards = soup.select('.s-item')
        
        for card in cards[:max_results]:
            listing = self._parse_search_card(card)
            if listing and listing.title and 'Shop on eBay' not in listing.title:
                results.append(listing)
                print(f"  Found: {listing.title[:50]}...")
        
        return results
    
    def _parse_search_card(self, card) -> Optional[EbayListing]:
        try:
            listing = EbayListing()
            
            # URL and Item ID
            link = card.select_one('.s-item__link')
            if link:
                listing.url = link.get('href', '').split('?')[0]
                match = re.search(r'/itm/(\d+)', listing.url)
                if match:
                    listing.item_id = match.group(1)
            
            # Title
            title_el = card.select_one('.s-item__title span')
            if title_el:
                listing.title = title_el.get_text(strip=True)
            
            # Price
            price_el = card.select_one('.s-item__price')
            if price_el:
                text = price_el.get_text()
                match = re.search(r'[\d,.]+', text.replace(',', ''))
                if match:
                    listing.price = float(match.group())
            
            # Shipping
            ship_el = card.select_one('.s-item__shipping')
            if ship_el:
                text = ship_el.get_text()
                if 'free' in text.lower():
                    listing.shipping_cost = 0
                else:
                    match = re.search(r'[\d,.]+', text.replace(',', ''))
                    if match:
                        listing.shipping_cost = float(match.group())
            
            # Condition
            cond_el = card.select_one('.SECONDARY_INFO')
            if cond_el:
                listing.condition = cond_el.get_text(strip=True)
            
            # Bids (for auctions)
            bids_el = card.select_one('.s-item__bids')
            if bids_el:
                text = bids_el.get_text()
                match = re.search(r'(\d+)', text)
                if match:
                    listing.bids = int(match.group(1))
                    listing.listing_type = 'auction'
            else:
                listing.listing_type = 'buy_it_now'
            
            # Image
            img_el = card.select_one('.s-item__image-img')
            if img_el:
                src = img_el.get('src') or img_el.get('data-src')
                if src:
                    listing.images = [src]
            
            from datetime import datetime
            listing.scraped_at = datetime.now().isoformat()
            
            return listing
        except Exception as e:
            return None
    
    def get_listing(self, item_id: str) -> Optional[EbayListing]:
        """Get detailed listing by item ID."""
        url = f"{self.BASE_URL}/itm/{item_id}"
        soup = self._request(url)
        
        if not soup:
            return None
        
        return self._parse_listing_page(soup, item_id, url)
    
    def _parse_listing_page(self, soup: BeautifulSoup,
                           item_id: str, url: str) -> Optional[EbayListing]:
        try:
            listing = EbayListing(item_id=item_id, url=url)
            
            # Title
            title_el = soup.select_one('h1.x-item-title__mainTitle span')
            if title_el:
                listing.title = title_el.get_text(strip=True)
            
            # Price
            price_el = soup.select_one('.x-price-primary span')
            if price_el:
                text = price_el.get_text()
                match = re.search(r'[\d,.]+', text.replace(',', ''))
                if match:
                    listing.price = float(match.group())
            
            # Condition
            cond_el = soup.select_one('.x-item-condition-text span')
            if cond_el:
                listing.condition = cond_el.get_text(strip=True)
            
            # Seller
            seller_el = soup.select_one('.x-sellercard-atf__info__about-seller a span')
            if seller_el:
                listing.seller = seller_el.get_text(strip=True)
            
            # Seller feedback
            feedback_el = soup.select_one('.x-sellercard-atf__data-item span')
            if feedback_el:
                text = feedback_el.get_text()
                match = re.search(r'([\d.]+)%', text)
                if match:
                    listing.seller_feedback = float(match.group(1))
            
            # Location
            loc_el = soup.select_one('.ux-labels-values--shipping .ux-textspans--SECONDARY')
            if loc_el:
                listing.location = loc_el.get_text(strip=True)
            
            # Images
            img_els = soup.select('.ux-image-carousel-item img')
            listing.images = [img.get('src') for img in img_els if img.get('src')][:10]
            
            # Item specifics
            specifics = soup.select('.ux-labels-values--labelsvalue')
            for spec in specifics:
                label = spec.select_one('.ux-labels-values__labels')
                value = spec.select_one('.ux-labels-values__values')
                if label and value:
                    listing.item_specifics[label.get_text(strip=True)] = value.get_text(strip=True)
            
            from datetime import datetime
            listing.scraped_at = datetime.now().isoformat()
            
            return listing
        except Exception as e:
            print(f"Error parsing listing: {e}")
            return None


def search_ebay(query: str, max_results: int = 20) -> List[Dict]:
    ant = EbayAnt()
    results = ant.search(query, max_results)
    return [r.to_dict() for r in results]


if __name__ == '__main__':
    results = search_ebay("vintage camera", max_results=10)
    for item in results:
        print(f"{item['title'][:50]}... - ${item['price']} ({item['listing_type']})")
