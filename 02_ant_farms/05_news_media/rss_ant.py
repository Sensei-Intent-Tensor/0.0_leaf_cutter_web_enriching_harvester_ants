"""
RSS Ant
=======

RSS/Atom feed parser for content aggregation.

Usage:
    ant = RSSAnt()
    
    # Parse a feed
    result = ant.scrape('https://example.com/feed.xml')
    
    for item in result.data['items']:
        print(item['title'])
"""

import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime

import requests


@dataclass
class ScrapeResult:
    success: bool
    url: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    scraped_at: datetime = None
    
    def __post_init__(self):
        if self.scraped_at is None:
            self.scraped_at = datetime.utcnow()


class RSSAnt:
    """
    RSS/Atom feed parser.
    
    Supports:
    - RSS 2.0
    - RSS 1.0
    - Atom
    """
    
    name = "rss_ant"
    
    # XML namespaces
    NAMESPACES = {
        'atom': 'http://www.w3.org/2005/Atom',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'content': 'http://purl.org/rss/1.0/modules/content/',
        'media': 'http://search.yahoo.com/mrss/',
    }
    
    def __init__(self, **kwargs):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'RSSAnt/1.0',
            'Accept': 'application/rss+xml, application/atom+xml, application/xml, text/xml',
        })
    
    def scrape(self, url: str) -> ScrapeResult:
        """Fetch and parse RSS/Atom feed."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            return ScrapeResult(success=False, url=url, error=str(e))
        
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError as e:
            return ScrapeResult(success=False, url=url, error=f"XML parse error: {e}")
        
        # Detect feed type and parse
        if root.tag == 'rss':
            feed_data = self._parse_rss(root)
        elif root.tag == '{http://www.w3.org/2005/Atom}feed':
            feed_data = self._parse_atom(root)
        elif root.tag == 'feed':
            feed_data = self._parse_atom(root)
        else:
            return ScrapeResult(success=False, url=url, error=f"Unknown feed format: {root.tag}")
        
        feed_data['url'] = url
        
        return ScrapeResult(success=True, url=url, data=feed_data)
    
    def _parse_rss(self, root: ET.Element) -> dict:
        """Parse RSS 2.0 feed."""
        channel = root.find('channel')
        
        if channel is None:
            return {'items': [], 'error': 'No channel element found'}
        
        feed = {
            'format': 'rss',
            'title': self._get_text(channel, 'title'),
            'description': self._get_text(channel, 'description'),
            'link': self._get_text(channel, 'link'),
            'language': self._get_text(channel, 'language'),
            'last_build': self._get_text(channel, 'lastBuildDate'),
            'items': [],
        }
        
        for item in channel.findall('item'):
            feed['items'].append({
                'title': self._get_text(item, 'title'),
                'link': self._get_text(item, 'link'),
                'description': self._get_text(item, 'description'),
                'content': self._get_text(item, 'content:encoded', self.NAMESPACES),
                'author': self._get_text(item, 'author') or self._get_text(item, 'dc:creator', self.NAMESPACES),
                'pub_date': self._parse_date(self._get_text(item, 'pubDate')),
                'guid': self._get_text(item, 'guid'),
                'categories': [cat.text for cat in item.findall('category') if cat.text],
                'enclosure': self._get_enclosure(item),
            })
        
        return feed
    
    def _parse_atom(self, root: ET.Element) -> dict:
        """Parse Atom feed."""
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        # Handle namespaced and non-namespaced
        def find(el, tag):
            result = el.find(f'atom:{tag}', ns)
            if result is None:
                result = el.find(tag)
            return result
        
        def findall(el, tag):
            result = el.findall(f'atom:{tag}', ns)
            if not result:
                result = el.findall(tag)
            return result
        
        title_el = find(root, 'title')
        subtitle_el = find(root, 'subtitle')
        
        feed = {
            'format': 'atom',
            'title': title_el.text if title_el is not None else None,
            'description': subtitle_el.text if subtitle_el is not None else None,
            'link': self._get_atom_link(root, ns),
            'updated': self._get_text_ns(root, 'updated', ns),
            'items': [],
        }
        
        for entry in findall(root, 'entry'):
            title_el = find(entry, 'title')
            content_el = find(entry, 'content')
            summary_el = find(entry, 'summary')
            published_el = find(entry, 'published')
            updated_el = find(entry, 'updated')
            author_el = find(entry, 'author')
            id_el = find(entry, 'id')
            
            author = None
            if author_el is not None:
                name_el = find(author_el, 'name')
                author = name_el.text if name_el is not None else None
            
            feed['items'].append({
                'title': title_el.text if title_el is not None else None,
                'link': self._get_atom_link(entry, ns),
                'description': summary_el.text if summary_el is not None else None,
                'content': content_el.text if content_el is not None else None,
                'author': author,
                'pub_date': self._parse_date(
                    published_el.text if published_el is not None else 
                    (updated_el.text if updated_el is not None else None)
                ),
                'guid': id_el.text if id_el is not None else None,
                'categories': [cat.get('term') for cat in findall(entry, 'category') if cat.get('term')],
            })
        
        return feed
    
    def _get_text(self, element: ET.Element, tag: str, namespaces: dict = None) -> Optional[str]:
        """Get text content of child element."""
        if namespaces and ':' in tag:
            prefix, local = tag.split(':')
            ns = namespaces.get(prefix, '')
            child = element.find(f'{{{ns}}}{local}')
        else:
            child = element.find(tag)
        
        return child.text if child is not None else None
    
    def _get_text_ns(self, element: ET.Element, tag: str, ns: dict) -> Optional[str]:
        """Get text with namespace handling."""
        child = element.find(f'atom:{tag}', ns)
        if child is None:
            child = element.find(tag)
        return child.text if child is not None else None
    
    def _get_atom_link(self, element: ET.Element, ns: dict) -> Optional[str]:
        """Get link from Atom element."""
        # Try with namespace
        for link in element.findall('atom:link', ns):
            if link.get('rel', 'alternate') == 'alternate':
                return link.get('href')
        
        # Try without namespace
        for link in element.findall('link'):
            if link.get('rel', 'alternate') == 'alternate':
                return link.get('href')
            if link.text:
                return link.text
        
        return None
    
    def _get_enclosure(self, item: ET.Element) -> Optional[dict]:
        """Get enclosure (media attachment) from RSS item."""
        enclosure = item.find('enclosure')
        
        if enclosure is not None:
            return {
                'url': enclosure.get('url'),
                'type': enclosure.get('type'),
                'length': enclosure.get('length'),
            }
        
        return None
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[str]:
        """Parse date string to ISO format."""
        if not date_str:
            return None
        
        try:
            # Try RFC 2822 (RSS)
            dt = parsedate_to_datetime(date_str)
            return dt.isoformat()
        except (ValueError, TypeError):
            pass
        
        try:
            # Try ISO 8601 (Atom)
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.isoformat()
        except (ValueError, TypeError):
            pass
        
        return date_str


if __name__ == "__main__":
    ant = RSSAnt()
    
    # Test with a feed
    result = ant.scrape('https://example.com/feed')
    
    if result.success:
        feed = result.data
        print(f"Feed: {feed['title']}")
        print(f"Items: {len(feed['items'])}")
        
        for item in feed['items'][:5]:
            print(f"  - {item['title']}")
