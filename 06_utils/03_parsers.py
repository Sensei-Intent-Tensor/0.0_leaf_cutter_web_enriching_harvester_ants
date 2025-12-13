"""
HTML and JSON parsing utilities.
"""

import re
import json
from typing import Optional, List, Dict, Any, Union
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


class HtmlParser:
    """HTML parsing utilities using BeautifulSoup."""
    
    def __init__(self, html: str, base_url: Optional[str] = None):
        self.soup = BeautifulSoup(html, 'lxml')
        self.base_url = base_url
    
    @classmethod
    def from_response(cls, response, parser: str = 'lxml') -> 'HtmlParser':
        """Create parser from requests Response."""
        return cls(response.text, base_url=response.url)
    
    def select(self, selector: str) -> List:
        """Select elements using CSS selector."""
        return self.soup.select(selector)
    
    def select_one(self, selector: str) -> Optional:
        """Select single element."""
        return self.soup.select_one(selector)
    
    def get_text(self, selector: str, default: str = '') -> str:
        """Get text content from selector."""
        element = self.select_one(selector)
        if element:
            return element.get_text(strip=True)
        return default
    
    def get_attr(self, selector: str, attr: str, default: str = '') -> str:
        """Get attribute value from selector."""
        element = self.select_one(selector)
        if element:
            return element.get(attr, default)
        return default
    
    def get_all_text(self, selector: str) -> List[str]:
        """Get text from all matching elements."""
        return [el.get_text(strip=True) for el in self.select(selector)]
    
    def get_link(self, selector: str) -> Optional[str]:
        """Get absolute URL from link."""
        href = self.get_attr(selector, 'href')
        if href and self.base_url:
            return urljoin(self.base_url, href)
        return href or None
    
    def get_all_links(self, selector: str = 'a[href]') -> List[str]:
        """Get all links matching selector."""
        links = []
        for element in self.select(selector):
            href = element.get('href')
            if href:
                if self.base_url:
                    href = urljoin(self.base_url, href)
                links.append(href)
        return links
    
    def get_image(self, selector: str) -> Optional[str]:
        """Get absolute image URL."""
        src = self.get_attr(selector, 'src') or self.get_attr(selector, 'data-src')
        if src and self.base_url:
            return urljoin(self.base_url, src)
        return src or None
    
    def extract_json_ld(self) -> List[Dict]:
        """Extract JSON-LD structured data."""
        scripts = self.select('script[type="application/ld+json"]')
        data = []
        for script in scripts:
            try:
                parsed = json.loads(script.string)
                if isinstance(parsed, list):
                    data.extend(parsed)
                else:
                    data.append(parsed)
            except (json.JSONDecodeError, TypeError):
                pass
        return data
    
    def extract_meta(self, name: str = None, property: str = None) -> Optional[str]:
        """Extract meta tag content."""
        if name:
            meta = self.select_one(f'meta[name="{name}"]')
        elif property:
            meta = self.select_one(f'meta[property="{property}"]')
        else:
            return None
        
        return meta.get('content') if meta else None
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


class JsonParser:
    """JSON parsing and extraction utilities."""
    
    def __init__(self, data: Union[str, Dict, List]):
        if isinstance(data, str):
            self.data = json.loads(data)
        else:
            self.data = data
    
    @classmethod
    def from_response(cls, response) -> 'JsonParser':
        """Create parser from requests Response."""
        return cls(response.json())
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get value using dot notation path."""
        keys = path.split('.')
        value = self.data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            elif isinstance(value, list) and key.isdigit():
                idx = int(key)
                value = value[idx] if idx < len(value) else None
            else:
                return default
            
            if value is None:
                return default
        
        return value
    
    def get_list(self, path: str) -> List:
        """Get list at path, always returns list."""
        value = self.get(path, [])
        if isinstance(value, list):
            return value
        return [value] if value else []
    
    def find_all(self, key: str) -> List:
        """Find all values for a key recursively."""
        results = []
        self._find_recursive(self.data, key, results)
        return results
    
    def _find_recursive(self, obj: Any, key: str, results: List):
        """Recursively search for key."""
        if isinstance(obj, dict):
            if key in obj:
                results.append(obj[key])
            for v in obj.values():
                self._find_recursive(v, key, results)
        elif isinstance(obj, list):
            for item in obj:
                self._find_recursive(item, key, results)
    
    def flatten(self, separator: str = '_') -> Dict:
        """Flatten nested structure."""
        result = {}
        self._flatten_recursive(self.data, '', separator, result)
        return result
    
    def _flatten_recursive(self, obj: Any, prefix: str, sep: str, result: Dict):
        """Recursively flatten."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_key = f"{prefix}{sep}{k}" if prefix else k
                self._flatten_recursive(v, new_key, sep, result)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                new_key = f"{prefix}{sep}{i}" if prefix else str(i)
                self._flatten_recursive(v, new_key, sep, result)
        else:
            result[prefix] = obj
