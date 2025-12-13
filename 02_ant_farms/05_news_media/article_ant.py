"""
Article Ant
===========

Generic article/news content extractor.

Uses multiple strategies to extract article content:
1. Schema.org Article/NewsArticle markup
2. Open Graph metadata
3. Common article selectors
4. Readability-style extraction

Usage:
    ant = ArticleAnt()
    result = ant.scrape('https://example.com/news/article')
    
    print(result.data['title'])
    print(result.data['content'][:500])
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


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


class ArticleAnt:
    """
    Generic article content extractor.
    
    Attempts multiple extraction strategies:
    1. Schema.org structured data
    2. Open Graph metadata
    3. HTML content extraction
    """
    
    name = "article_ant"
    
    # Content selectors (in order of preference)
    content_selectors = [
        'article',
        '[role="article"]',
        '.article-content',
        '.article-body',
        '.post-content',
        '.entry-content',
        '.story-body',
        '#article-body',
        '.content-body',
        'main',
    ]
    
    # Elements to remove from content
    remove_selectors = [
        'script', 'style', 'nav', 'header', 'footer',
        '.advertisement', '.ad', '.social-share',
        '.related-articles', '.comments', '.sidebar',
        '[data-ad]', '.newsletter-signup',
    ]
    
    def __init__(self, **kwargs):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml',
        })
    
    def scrape(self, url: str) -> ScrapeResult:
        """Extract article content from URL."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            return ScrapeResult(success=False, url=url, error=str(e))
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Extract using multiple strategies
        article = {
            'url': url,
            'source': urlparse(url).netloc,
        }
        
        # 1. Try Schema.org
        schema = self._extract_schema(soup)
        if schema:
            article.update(schema)
            article['_extraction_method'] = 'schema'
        
        # 2. Add/supplement with Open Graph
        og_data = self._extract_opengraph(soup)
        for key, value in og_data.items():
            if not article.get(key):
                article[key] = value
        
        # 3. Add/supplement with HTML extraction
        html_data = self._extract_from_html(soup)
        for key, value in html_data.items():
            if not article.get(key):
                article[key] = value
        
        # 4. Extract main content if not found
        if not article.get('content'):
            article['content'] = self._extract_content(soup)
        
        # Calculate word count
        if article.get('content'):
            article['word_count'] = len(article['content'].split())
        
        return ScrapeResult(success=True, url=url, data=article)
    
    def _extract_schema(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract Schema.org Article data."""
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                
                if isinstance(data, list):
                    for item in data:
                        if self._is_article_schema(item):
                            return self._normalize_schema(item)
                elif self._is_article_schema(data):
                    return self._normalize_schema(data)
                elif isinstance(data.get('@graph'), list):
                    for item in data['@graph']:
                        if self._is_article_schema(item):
                            return self._normalize_schema(item)
                            
            except (json.JSONDecodeError, TypeError):
                continue
        
        return None
    
    def _is_article_schema(self, data: dict) -> bool:
        """Check if data is an Article schema."""
        schema_type = data.get('@type', '')
        article_types = ['Article', 'NewsArticle', 'BlogPosting', 'WebPage']
        
        if isinstance(schema_type, list):
            return any(t in article_types for t in schema_type)
        return schema_type in article_types
    
    def _normalize_schema(self, schema: dict) -> dict:
        """Normalize Article schema."""
        author = schema.get('author', {})
        if isinstance(author, list):
            author = author[0] if author else {}
        if isinstance(author, dict):
            author = author.get('name', '')
        
        publisher = schema.get('publisher', {})
        if isinstance(publisher, dict):
            publisher = publisher.get('name', '')
        
        return {
            'title': schema.get('headline') or schema.get('name'),
            'author': author,
            'publisher': publisher,
            'published_date': schema.get('datePublished'),
            'modified_date': schema.get('dateModified'),
            'description': schema.get('description'),
            'content': schema.get('articleBody'),
            'images': self._extract_schema_images(schema),
        }
    
    def _extract_schema_images(self, schema: dict) -> List[str]:
        """Extract images from schema."""
        images = schema.get('image', [])
        
        if isinstance(images, str):
            return [images]
        elif isinstance(images, dict):
            return [images.get('url', '')]
        elif isinstance(images, list):
            result = []
            for img in images:
                if isinstance(img, str):
                    result.append(img)
                elif isinstance(img, dict):
                    result.append(img.get('url', ''))
            return result
        
        return []
    
    def _extract_opengraph(self, soup: BeautifulSoup) -> dict:
        """Extract Open Graph metadata."""
        og_data = {}
        
        mappings = {
            'og:title': 'title',
            'og:description': 'description',
            'og:image': 'og_image',
            'article:author': 'author',
            'article:published_time': 'published_date',
            'article:modified_time': 'modified_date',
        }
        
        for og_prop, field in mappings.items():
            meta = soup.find('meta', property=og_prop)
            if meta and meta.get('content'):
                og_data[field] = meta['content']
        
        return og_data
    
    def _extract_from_html(self, soup: BeautifulSoup) -> dict:
        """Extract article data from HTML."""
        data = {}
        
        # Title
        title_el = soup.find('h1') or soup.find('title')
        if title_el:
            data['title'] = title_el.get_text(strip=True)
        
        # Author
        author_selectors = ['.author', '.byline', '[rel="author"]', '.writer']
        for selector in author_selectors:
            el = soup.select_one(selector)
            if el:
                data['author'] = el.get_text(strip=True)
                break
        
        # Published date
        time_el = soup.find('time')
        if time_el:
            data['published_date'] = time_el.get('datetime') or time_el.get_text(strip=True)
        
        return data
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main article content."""
        # Remove unwanted elements
        for selector in self.remove_selectors:
            for el in soup.select(selector):
                el.decompose()
        
        # Try content selectors
        for selector in self.content_selectors:
            content_el = soup.select_one(selector)
            if content_el:
                # Get text from paragraphs
                paragraphs = content_el.find_all('p')
                if paragraphs:
                    text = '\n\n'.join(p.get_text(strip=True) for p in paragraphs)
                    if len(text) > 200:  # Minimum content length
                        return text
        
        # Fallback: find largest text block
        all_p = soup.find_all('p')
        if all_p:
            return '\n\n'.join(p.get_text(strip=True) for p in all_p if len(p.get_text()) > 50)
        
        return ""
    
    def is_paywalled(self, soup: BeautifulSoup) -> bool:
        """Check if article is behind paywall."""
        paywall_indicators = [
            '.paywall',
            '.subscription-required',
            '#paywall',
            '[data-paywall]',
        ]
        
        for selector in paywall_indicators:
            if soup.select_one(selector):
                return True
        
        text = soup.get_text().lower()
        paywall_phrases = [
            'subscribe to continue reading',
            'this article is for subscribers',
            'become a member',
            'premium content',
        ]
        
        return any(phrase in text for phrase in paywall_phrases)


if __name__ == "__main__":
    ant = ArticleAnt()
    
    result = ant.scrape('https://example.com/article')
    
    if result.success:
        article = result.data
        print(f"Title: {article.get('title')}")
        print(f"Author: {article.get('author')}")
        print(f"Words: {article.get('word_count')}")
        print(f"Content preview: {article.get('content', '')[:200]}...")
