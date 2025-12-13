"""
Paginated Ant Template
======================

Scraper for multi-page results with pagination.

Usage:
    class SearchAnt(PaginatedAnt):
        name = "search_scraper"
        item_selector = ".search-result"
        next_page_selector = "a.next"
        
        def extract_item(self, element):
            return {
                'title': element.select_one('h3').text,
                'url': element.select_one('a')['href'],
            }
    
    ant = SearchAnt()
    results = ant.scrape_all_pages('https://example.com/search?q=test')
"""

from simple_ant import SimpleAnt, ScrapeResult
from typing import Dict, Any, List
from urllib.parse import urljoin
from bs4 import BeautifulSoup


class PaginatedAnt(SimpleAnt):
    """
    Ant for scraping paginated results.
    
    Customize:
        - item_selector: CSS selector for items on page
        - next_page_selector: CSS selector for next page link
        - max_pages: Maximum pages to scrape
    """
    
    name: str = "paginated_ant"
    
    # Override in subclass
    item_selector: str = ".item"
    next_page_selector: str = "a.next"
    
    # Limits
    max_pages: int = 100
    
    def extract_item(self, element: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract data from a single item.
        Override this in your subclass.
        """
        return {
            'text': element.get_text(strip=True)
        }
    
    def extract(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract all items and pagination info."""
        items = []
        
        for element in soup.select(self.item_selector):
            item = self.extract_item(element)
            if item:
                items.append(item)
        
        # Find next page
        next_link = soup.select_one(self.next_page_selector)
        next_url = next_link['href'] if next_link and next_link.get('href') else None
        
        return {
            'items': items,
            'count': len(items),
            'next_page': next_url
        }
    
    def scrape_all_pages(self, start_url: str) -> List[Dict[str, Any]]:
        """Scrape all pages starting from the given URL."""
        all_items = []
        current_url = start_url
        page = 1
        
        while current_url and page <= self.max_pages:
            self.logger.info(f"Scraping page {page}: {current_url}")
            
            result = self.scrape(current_url)
            
            if not result.success:
                self.logger.error(f"Failed on page {page}: {result.error}")
                break
            
            items = result.data.get('items', [])
            all_items.extend(items)
            
            self.logger.info(f"Found {len(items)} items on page {page}")
            
            # Get next page URL
            next_url = result.data.get('next_page')
            
            if next_url:
                current_url = urljoin(current_url, next_url)
                page += 1
            else:
                break
        
        self.logger.info(f"Total items collected: {len(all_items)}")
        return all_items


# Example usage
if __name__ == "__main__":
    class ExampleSearchAnt(PaginatedAnt):
        name = "example_search"
        item_selector = ".result"
        next_page_selector = "a.next-page"
        max_pages = 5
        
        def extract_item(self, element):
            return {
                'title': element.select_one('h3').get_text(strip=True) if element.select_one('h3') else None,
                'snippet': element.select_one('p').get_text(strip=True) if element.select_one('p') else None,
            }
    
    ant = ExampleSearchAnt()
    # results = ant.scrape_all_pages('https://example.com/search?q=test')
