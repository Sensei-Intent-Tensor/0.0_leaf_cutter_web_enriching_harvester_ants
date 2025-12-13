"""
Crunchbase Scraper

WARNING: For educational purposes. Crunchbase has strict anti-scraping.
Use official API for production: https://data.crunchbase.com/docs
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
class CrunchbaseCompany:
    """Data model for a Crunchbase company."""
    permalink: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    founded_date: Optional[str] = None
    location: Optional[str] = None
    headquarters: Optional[str] = None
    employee_count: Optional[str] = None
    industries: List[str] = field(default_factory=list)
    funding_total: Optional[str] = None
    funding_rounds: Optional[int] = None
    last_funding_type: Optional[str] = None
    ipo_status: Optional[str] = None
    stock_symbol: Optional[str] = None
    
    # Social links
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    facebook: Optional[str] = None
    
    # Metadata
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class CrunchbaseAnt:
    """
    Crunchbase scraper.
    
    Note: Crunchbase heavily protects their data. This scraper
    may not work reliably. Use official API for production.
    
    Usage:
        ant = CrunchbaseAnt()
        company = ant.get_company("facebook")
    """
    
    BASE_URL = "https://www.crunchbase.com"
    
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
    
    def _request(self, url: str) -> Optional[BeautifulSoup]:
        """Make request with rate limiting."""
        time.sleep(self.delay + random.random() * 2)
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'lxml')
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def search(self, query: str, max_results: int = 10) -> List[CrunchbaseCompany]:
        """
        Search for companies.
        
        Note: Search may be heavily rate-limited.
        """
        url = f"{self.BASE_URL}/textsearch?q={quote_plus(query)}"
        soup = self._request(url)
        
        if not soup:
            return []
        
        results = []
        
        # Try to find company links
        links = soup.select('a[href*="/organization/"]')
        
        seen = set()
        for link in links:
            if len(results) >= max_results:
                break
                
            href = link.get('href', '')
            if '/organization/' in href:
                permalink = href.split('/organization/')[-1].split('/')[0].split('?')[0]
                
                if permalink and permalink not in seen:
                    seen.add(permalink)
                    
                    company = CrunchbaseCompany(
                        permalink=permalink,
                        name=link.get_text(strip=True) or permalink,
                        url=f"{self.BASE_URL}/organization/{permalink}"
                    )
                    results.append(company)
        
        return results
    
    def get_company(self, permalink: str) -> Optional[CrunchbaseCompany]:
        """
        Get company details by permalink.
        
        Args:
            permalink: Company's Crunchbase permalink (e.g., "facebook")
            
        Returns:
            CrunchbaseCompany or None
        """
        url = f"{self.BASE_URL}/organization/{permalink}"
        soup = self._request(url)
        
        if not soup:
            return None
        
        return self._parse_company_page(soup, permalink, url)
    
    def _parse_company_page(self, soup: BeautifulSoup, 
                           permalink: str, url: str) -> Optional[CrunchbaseCompany]:
        """Parse company detail page."""
        try:
            company = CrunchbaseCompany(
                permalink=permalink,
                url=url
            )
            
            # Try to extract JSON-LD data
            script = soup.select_one('script[type="application/ld+json"]')
            if script:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        company.name = data.get('name')
                        company.description = data.get('description')
                        company.website = data.get('url')
                        
                        if 'address' in data:
                            addr = data['address']
                            parts = [
                                addr.get('addressLocality', ''),
                                addr.get('addressRegion', ''),
                                addr.get('addressCountry', '')
                            ]
                            company.headquarters = ', '.join(p for p in parts if p)
                except:
                    pass
            
            # Fallback to HTML parsing
            if not company.name:
                name_el = soup.select_one('h1')
                if name_el:
                    company.name = name_el.get_text(strip=True)
            
            # Description
            if not company.description:
                desc_el = soup.select_one('[class*="description"]')
                if desc_el:
                    company.description = desc_el.get_text(strip=True)
            
            # Look for profile sections
            sections = soup.select('[class*="profile-section"]')
            
            for section in sections:
                text = section.get_text()
                
                # Founded
                if 'founded' in text.lower():
                    match = re.search(r'\b(19|20)\d{2}\b', text)
                    if match:
                        company.founded_date = match.group()
                
                # Employees
                if 'employee' in text.lower():
                    match = re.search(r'(\d+[\-–]\d+|\d+\+?)\s*employee', text, re.I)
                    if match:
                        company.employee_count = match.group(1)
                
                # Funding
                if 'funding' in text.lower():
                    match = re.search(r'\$[\d.]+[BMK]?', text)
                    if match:
                        company.funding_total = match.group()
            
            # Social links
            for link in soup.select('a[href]'):
                href = link.get('href', '')
                if 'linkedin.com/company' in href:
                    company.linkedin = href
                elif 'twitter.com/' in href:
                    company.twitter = href
                elif 'facebook.com/' in href and 'crunchbase' not in href:
                    company.facebook = href
            
            # Industries/categories
            cat_links = soup.select('a[href*="/hub/"]')
            company.industries = list(set(
                c.get_text(strip=True) for c in cat_links if c.get_text(strip=True)
            ))[:10]
            
            from datetime import datetime
            company.scraped_at = datetime.now().isoformat()
            
            return company
            
        except Exception as e:
            print(f"Error parsing company page: {e}")
            return None


def get_crunchbase_company(permalink: str) -> Optional[Dict]:
    """
    Get Crunchbase company data.
    
    Args:
        permalink: Company permalink (e.g., "facebook", "stripe")
        
    Returns:
        Company data dictionary or None
    """
    ant = CrunchbaseAnt()
    company = ant.get_company(permalink)
    return company.to_dict() if company else None


if __name__ == '__main__':
    # Example usage
    company = get_crunchbase_company("stripe")
    if company:
        print(f"Name: {company['name']}")
        print(f"Description: {company['description'][:100]}...")
        print(f"Founded: {company['founded_date']}")
        print(f"Funding: {company['funding_total']}")
