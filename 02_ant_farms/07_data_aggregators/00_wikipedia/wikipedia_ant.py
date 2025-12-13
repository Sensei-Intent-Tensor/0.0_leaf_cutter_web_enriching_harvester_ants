"""
Wikipedia Scraper

Wikipedia is FREE to scrape! Content is CC BY-SA licensed.
Uses the official MediaWiki API.

Be respectful with rate limits.
"""

import re
import json
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup


@dataclass
class WikipediaArticle:
    """Data model for a Wikipedia article."""
    title: Optional[str] = None
    page_id: Optional[int] = None
    url: Optional[str] = None
    extract: Optional[str] = None  # Plain text summary
    content: Optional[str] = None  # Full HTML content
    categories: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    infobox: Dict[str, str] = field(default_factory=dict)
    coordinates: Optional[Dict] = None
    last_modified: Optional[str] = None
    
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class WikipediaAnt:
    """
    Wikipedia scraper using MediaWiki API.
    
    Wikipedia is FREE to access. Be respectful with rate limits.
    
    Usage:
        ant = WikipediaAnt()
        article = ant.get_article("Python (programming language)")
        results = ant.search("machine learning")
    """
    
    API_URL = "https://en.wikipedia.org/w/api.php"
    
    def __init__(self, language: str = "en", delay: float = 0.1):
        """
        Args:
            language: Wikipedia language code (en, es, de, etc.)
            delay: Delay between requests (be respectful!)
        """
        self.language = language
        self.api_url = f"https://{language}.wikipedia.org/w/api.php"
        self.base_url = f"https://{language}.wikipedia.org/wiki/"
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HarvesterAnts/1.0 (Educational scraper; Contact: example@email.com)'
        })
    
    def _api_request(self, params: Dict) -> Optional[Dict]:
        """Make API request."""
        time.sleep(self.delay)
        
        params['format'] = 'json'
        
        try:
            response = self.session.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API request failed: {e}")
            return None
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search Wikipedia articles.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of search results with title, snippet, page_id
        """
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': query,
            'srlimit': limit,
            'srprop': 'snippet|titlesnippet|wordcount'
        }
        
        data = self._api_request(params)
        
        if not data or 'query' not in data:
            return []
        
        results = []
        for item in data['query'].get('search', []):
            results.append({
                'title': item.get('title'),
                'page_id': item.get('pageid'),
                'snippet': BeautifulSoup(item.get('snippet', ''), 'html.parser').get_text(),
                'word_count': item.get('wordcount'),
                'url': self.base_url + quote(item.get('title', '').replace(' ', '_'))
            })
        
        return results
    
    def get_article(self, title: str, include_content: bool = False) -> Optional[WikipediaArticle]:
        """
        Get Wikipedia article by title.
        
        Args:
            title: Article title
            include_content: Include full HTML content
            
        Returns:
            WikipediaArticle or None
        """
        article = WikipediaArticle(title=title)
        article.url = self.base_url + quote(title.replace(' ', '_'))
        
        # Get basic info and extract
        params = {
            'action': 'query',
            'titles': title,
            'prop': 'extracts|info|categories|pageimages',
            'exintro': True,
            'explaintext': True,
            'inprop': 'url',
            'cllimit': 50,
            'piprop': 'original'
        }
        
        data = self._api_request(params)
        
        if not data or 'query' not in data:
            return None
        
        pages = data['query'].get('pages', {})
        
        for page_id, page_data in pages.items():
            if page_id == '-1':
                return None  # Page not found
            
            article.page_id = int(page_id)
            article.title = page_data.get('title')
            article.extract = page_data.get('extract')
            article.last_modified = page_data.get('touched')
            
            # Categories
            if 'categories' in page_data:
                article.categories = [
                    cat['title'].replace('Category:', '')
                    for cat in page_data['categories']
                ]
            
            # Main image
            if 'original' in page_data.get('pageimage', {}):
                article.images.append(page_data['original']['source'])
            
            break
        
        # Get links
        article.links = self._get_links(title)
        
        # Get images
        article.images.extend(self._get_images(title))
        
        # Get infobox
        article.infobox = self._get_infobox(title)
        
        # Get full content if requested
        if include_content:
            article.content = self._get_content(title)
        
        # Get coordinates if available
        article.coordinates = self._get_coordinates(title)
        
        from datetime import datetime
        article.scraped_at = datetime.now().isoformat()
        
        return article
    
    def _get_links(self, title: str, limit: int = 100) -> List[str]:
        """Get links from article."""
        params = {
            'action': 'query',
            'titles': title,
            'prop': 'links',
            'pllimit': limit
        }
        
        data = self._api_request(params)
        
        if not data or 'query' not in data:
            return []
        
        links = []
        for page in data['query'].get('pages', {}).values():
            for link in page.get('links', []):
                links.append(link['title'])
        
        return links
    
    def _get_images(self, title: str) -> List[str]:
        """Get image URLs from article."""
        params = {
            'action': 'query',
            'titles': title,
            'prop': 'images',
            'imlimit': 20
        }
        
        data = self._api_request(params)
        
        if not data or 'query' not in data:
            return []
        
        image_titles = []
        for page in data['query'].get('pages', {}).values():
            for img in page.get('images', []):
                image_titles.append(img['title'])
        
        # Get actual URLs
        if not image_titles:
            return []
        
        params = {
            'action': 'query',
            'titles': '|'.join(image_titles[:10]),
            'prop': 'imageinfo',
            'iiprop': 'url'
        }
        
        data = self._api_request(params)
        
        urls = []
        if data and 'query' in data:
            for page in data['query'].get('pages', {}).values():
                for info in page.get('imageinfo', []):
                    urls.append(info['url'])
        
        return urls
    
    def _get_infobox(self, title: str) -> Dict[str, str]:
        """Extract infobox data from article."""
        params = {
            'action': 'parse',
            'page': title,
            'prop': 'text',
            'section': 0
        }
        
        data = self._api_request(params)
        
        if not data or 'parse' not in data:
            return {}
        
        html = data['parse'].get('text', {}).get('*', '')
        soup = BeautifulSoup(html, 'lxml')
        
        infobox = {}
        
        # Find infobox table
        table = soup.select_one('.infobox')
        if table:
            rows = table.select('tr')
            for row in rows:
                header = row.select_one('th')
                value = row.select_one('td')
                if header and value:
                    key = header.get_text(strip=True)
                    val = value.get_text(strip=True)
                    if key and val:
                        infobox[key] = val
        
        return infobox
    
    def _get_content(self, title: str) -> Optional[str]:
        """Get full article HTML content."""
        params = {
            'action': 'parse',
            'page': title,
            'prop': 'text'
        }
        
        data = self._api_request(params)
        
        if data and 'parse' in data:
            return data['parse'].get('text', {}).get('*')
        
        return None
    
    def _get_coordinates(self, title: str) -> Optional[Dict]:
        """Get geographic coordinates if available."""
        params = {
            'action': 'query',
            'titles': title,
            'prop': 'coordinates'
        }
        
        data = self._api_request(params)
        
        if not data or 'query' not in data:
            return None
        
        for page in data['query'].get('pages', {}).values():
            coords = page.get('coordinates', [])
            if coords:
                return {
                    'latitude': coords[0].get('lat'),
                    'longitude': coords[0].get('lon')
                }
        
        return None
    
    def get_random_articles(self, count: int = 5) -> List[str]:
        """Get random article titles."""
        params = {
            'action': 'query',
            'list': 'random',
            'rnlimit': count,
            'rnnamespace': 0
        }
        
        data = self._api_request(params)
        
        if not data or 'query' not in data:
            return []
        
        return [item['title'] for item in data['query'].get('random', [])]


def get_wikipedia_article(title: str) -> Optional[Dict]:
    """Get Wikipedia article by title."""
    ant = WikipediaAnt()
    article = ant.get_article(title)
    return article.to_dict() if article else None


def search_wikipedia(query: str, limit: int = 10) -> List[Dict]:
    """Search Wikipedia."""
    ant = WikipediaAnt()
    return ant.search(query, limit)


if __name__ == '__main__':
    # Example usage
    print("Getting article: Python (programming language)")
    article = get_wikipedia_article("Python (programming language)")
    
    if article:
        print(f"\nTitle: {article['title']}")
        print(f"Categories: {article['categories'][:5]}")
        print(f"\nExtract:\n{article['extract'][:500]}...")
        print(f"\nInfobox keys: {list(article['infobox'].keys())[:5]}")
