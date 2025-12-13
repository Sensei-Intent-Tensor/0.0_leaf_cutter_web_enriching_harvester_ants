"""
LinkedIn Public Profile Scraper

⚠️ CRITICAL WARNING ⚠️
LinkedIn aggressively protects their data and has sued scrapers.
This code is for EDUCATIONAL PURPOSES ONLY.

For production use:
- Use LinkedIn Official APIs (with partnership)
- Use licensed data providers (People Data Labs, Clearbit, etc.)
- Respect ToS and legal requirements
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
class LinkedInProfile:
    """Data model for a LinkedIn profile (public data only)."""
    public_id: Optional[str] = None
    url: Optional[str] = None
    name: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    current_company: Optional[str] = None
    current_title: Optional[str] = None
    connections: Optional[str] = None
    profile_picture: Optional[str] = None
    
    # Metadata
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class LinkedInCompany:
    """Data model for a LinkedIn company page."""
    company_id: Optional[str] = None
    url: Optional[str] = None
    name: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    headquarters: Optional[str] = None
    founded: Optional[str] = None
    specialties: List[str] = field(default_factory=list)
    logo_url: Optional[str] = None
    follower_count: Optional[int] = None
    employee_count_on_linkedin: Optional[int] = None
    
    # Metadata
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class LinkedInPublicAnt:
    """
    LinkedIn scraper for PUBLIC data only.
    
    ⚠️ WARNING: Use at your own risk. LinkedIn prohibits scraping.
    
    This scraper only accesses publicly available data without login.
    Even so, LinkedIn may block requests and this may violate ToS.
    
    For production, use:
    - LinkedIn Official APIs
    - Licensed data providers (PDL, Clearbit, ZoomInfo)
    """
    
    BASE_URL = "https://www.linkedin.com"
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    ]
    
    def __init__(self, delay: float = 5.0):
        """
        Args:
            delay: Minimum delay between requests (be respectful!)
        """
        self.delay = delay
        self.session = requests.Session()
        self._update_headers()
        
        print("⚠️ WARNING: LinkedIn scraping may violate ToS.")
        print("   Use official APIs or licensed data for production.")
    
    def _update_headers(self):
        self.session.headers.update({
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
        })
    
    def _request(self, url: str) -> Optional[BeautifulSoup]:
        """Make request with generous rate limiting."""
        # Be very respectful with LinkedIn
        time.sleep(self.delay + random.random() * 3)
        
        try:
            response = self.session.get(url, timeout=30, allow_redirects=True)
            
            # Check for auth wall
            if 'authwall' in response.url or 'login' in response.url:
                print("Hit auth wall - content requires login")
                return None
            
            response.raise_for_status()
            return BeautifulSoup(response.text, 'lxml')
            
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def get_public_profile(self, profile_id: str) -> Optional[LinkedInProfile]:
        """
        Get publicly available profile information.
        
        Args:
            profile_id: LinkedIn public profile ID (from URL)
            
        Returns:
            LinkedInProfile with public data only, or None
        """
        url = f"{self.BASE_URL}/in/{profile_id}"
        soup = self._request(url)
        
        if not soup:
            return None
        
        return self._parse_public_profile(soup, profile_id, url)
    
    def _parse_public_profile(self, soup: BeautifulSoup,
                              profile_id: str, url: str) -> Optional[LinkedInProfile]:
        """Parse public profile page."""
        try:
            profile = LinkedInProfile(
                public_id=profile_id,
                url=url
            )
            
            # Try JSON-LD first (most reliable for public data)
            for script in soup.select('script[type="application/ld+json"]'):
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        if data.get('@type') == 'Person':
                            profile.name = data.get('name')
                            if 'address' in data:
                                profile.location = data['address'].get('addressLocality')
                            if 'worksFor' in data:
                                works_for = data['worksFor']
                                if isinstance(works_for, list) and works_for:
                                    profile.current_company = works_for[0].get('name')
                                elif isinstance(works_for, dict):
                                    profile.current_company = works_for.get('name')
                except:
                    continue
            
            # Fallback to HTML parsing
            if not profile.name:
                name_el = soup.select_one('h1')
                if name_el:
                    profile.name = name_el.get_text(strip=True)
            
            # Headline
            headline_el = soup.select_one('[data-section="headline"]') or \
                         soup.select_one('.top-card-layout__headline')
            if headline_el:
                profile.headline = headline_el.get_text(strip=True)
            
            # Location  
            if not profile.location:
                loc_el = soup.select_one('[data-section="location"]') or \
                        soup.select_one('.top-card-layout__first-subline')
                if loc_el:
                    profile.location = loc_el.get_text(strip=True)
            
            # Profile picture
            img_el = soup.select_one('img[data-delayed-url*="profile"]') or \
                    soup.select_one('.top-card-layout__entity-image')
            if img_el:
                profile.profile_picture = img_el.get('src') or img_el.get('data-delayed-url')
            
            from datetime import datetime
            profile.scraped_at = datetime.now().isoformat()
            
            return profile
            
        except Exception as e:
            print(f"Error parsing profile: {e}")
            return None
    
    def get_company(self, company_id: str) -> Optional[LinkedInCompany]:
        """
        Get company page information.
        
        Args:
            company_id: LinkedIn company ID or slug
            
        Returns:
            LinkedInCompany or None
        """
        url = f"{self.BASE_URL}/company/{company_id}"
        soup = self._request(url)
        
        if not soup:
            return None
        
        return self._parse_company_page(soup, company_id, url)
    
    def _parse_company_page(self, soup: BeautifulSoup,
                           company_id: str, url: str) -> Optional[LinkedInCompany]:
        """Parse company page."""
        try:
            company = LinkedInCompany(
                company_id=company_id,
                url=url
            )
            
            # Try JSON-LD
            for script in soup.select('script[type="application/ld+json"]'):
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get('@type') == 'Organization':
                        company.name = data.get('name')
                        company.description = data.get('description')
                        company.website = data.get('url')
                        company.logo_url = data.get('logo')
                        
                        if 'address' in data:
                            addr = data['address']
                            parts = [addr.get('addressLocality'), 
                                    addr.get('addressRegion'),
                                    addr.get('addressCountry')]
                            company.headquarters = ', '.join(p for p in parts if p)
                except:
                    continue
            
            # Fallback to HTML
            if not company.name:
                name_el = soup.select_one('h1')
                if name_el:
                    company.name = name_el.get_text(strip=True)
            
            # Tagline
            tagline_el = soup.select_one('[data-test-id="about-us__tagline"]')
            if tagline_el:
                company.tagline = tagline_el.get_text(strip=True)
            
            # Industry
            industry_el = soup.select_one('[data-test-id="about-us__industry"]')
            if industry_el:
                company.industry = industry_el.get_text(strip=True)
            
            # Company size
            size_el = soup.select_one('[data-test-id="about-us__size"]')
            if size_el:
                company.company_size = size_el.get_text(strip=True)
            
            # Followers
            followers_el = soup.select_one('[data-test-id="about-us__followers-count"]')
            if followers_el:
                text = followers_el.get_text()
                match = re.search(r'([\d,]+)', text)
                if match:
                    company.follower_count = int(match.group(1).replace(',', ''))
            
            from datetime import datetime
            company.scraped_at = datetime.now().isoformat()
            
            return company
            
        except Exception as e:
            print(f"Error parsing company: {e}")
            return None


# Note: These functions are for educational purposes only
def get_linkedin_profile(profile_id: str) -> Optional[Dict]:
    """Get LinkedIn public profile (educational only)."""
    ant = LinkedInPublicAnt()
    profile = ant.get_public_profile(profile_id)
    return profile.to_dict() if profile else None


def get_linkedin_company(company_id: str) -> Optional[Dict]:
    """Get LinkedIn company page (educational only)."""
    ant = LinkedInPublicAnt()
    company = ant.get_company(company_id)
    return company.to_dict() if company else None


if __name__ == '__main__':
    print("="*60)
    print("LinkedIn Scraper - EDUCATIONAL USE ONLY")
    print("Use official APIs for production!")
    print("="*60)
    
    # Example (will likely hit auth wall for most profiles)
    company = get_linkedin_company("microsoft")
    if company:
        print(f"\nCompany: {company['name']}")
        print(f"Industry: {company['industry']}")
