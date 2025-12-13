"""
Glassdoor Company & Jobs Scraper

WARNING: Glassdoor heavily protects data. Most requires login.
For production, use Glassdoor API for partners.
"""

import re
import json
import time
import random
from typing import Optional, List, Dict
from dataclasses import dataclass, field, asdict
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import requests


@dataclass
class GlassdoorCompany:
    """Data model for a Glassdoor company."""
    company_id: Optional[str] = None
    url: Optional[str] = None
    name: Optional[str] = None
    overall_rating: Optional[float] = None
    review_count: Optional[int] = None
    ceo_name: Optional[str] = None
    ceo_approval: Optional[float] = None
    recommend_to_friend: Optional[float] = None
    size: Optional[str] = None
    industry: Optional[str] = None
    headquarters: Optional[str] = None
    founded: Optional[int] = None
    website: Optional[str] = None
    
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class GlassdoorJob:
    """Data model for a Glassdoor job."""
    job_id: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    salary_estimate: Optional[str] = None
    posted_date: Optional[str] = None
    easy_apply: bool = False
    
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class GlassdoorAnt:
    """
    Glassdoor scraper for public company and job data.
    
    Note: Most detailed data requires login.
    """
    
    BASE_URL = "https://www.glassdoor.com"
    
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
        time.sleep(self.delay + random.random() * 2)
        try:
            response = self.session.get(url, timeout=30)
            if 'login' in response.url.lower() or 'signup' in response.url.lower():
                print("⚠️ Login wall detected")
                return None
            response.raise_for_status()
            return BeautifulSoup(response.text, 'lxml')
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def search_companies(self, query: str, max_results: int = 20) -> List[GlassdoorCompany]:
        """Search for companies."""
        url = f"{self.BASE_URL}/Search/results.htm?keyword={quote_plus(query)}"
        soup = self._request(url)
        
        if not soup:
            return []
        
        results = []
        
        # Try to find company cards
        cards = soup.select('[data-test="employer-card"]') or soup.select('.single-company-result')
        
        for card in cards[:max_results]:
            company = self._parse_company_card(card)
            if company and company.name:
                results.append(company)
                print(f"  Found: {company.name} - {company.overall_rating} rating")
        
        return results
    
    def _parse_company_card(self, card) -> Optional[GlassdoorCompany]:
        try:
            company = GlassdoorCompany()
            
            # Name and URL
            name_el = card.select_one('h2 a') or card.select_one('.employer-name')
            if name_el:
                company.name = name_el.get_text(strip=True)
                href = name_el.get('href', '')
                if href:
                    company.url = self.BASE_URL + href if href.startswith('/') else href
                    # Extract company ID
                    match = re.search(r'E[I]?(\d+)', href)
                    if match:
                        company.company_id = match.group(1)
            
            # Rating
            rating_el = card.select_one('[data-test="rating"]') or card.select_one('.rating')
            if rating_el:
                match = re.search(r'([\d.]+)', rating_el.get_text())
                if match:
                    company.overall_rating = float(match.group(1))
            
            # Review count
            review_el = card.select_one('[data-test="reviews"]')
            if review_el:
                match = re.search(r'([\d,]+)', review_el.get_text())
                if match:
                    company.review_count = int(match.group(1).replace(',', ''))
            
            # Industry
            industry_el = card.select_one('[data-test="industry"]')
            if industry_el:
                company.industry = industry_el.get_text(strip=True)
            
            # Size
            size_el = card.select_one('[data-test="employer-size"]')
            if size_el:
                company.size = size_el.get_text(strip=True)
            
            from datetime import datetime
            company.scraped_at = datetime.now().isoformat()
            
            return company
        except Exception as e:
            return None
    
    def search_jobs(self, query: str, location: str = "",
                   max_results: int = 25) -> List[GlassdoorJob]:
        """Search for jobs."""
        url = f"{self.BASE_URL}/Job/jobs.htm?sc.keyword={quote_plus(query)}"
        if location:
            url += f"&locT=C&locKeyword={quote_plus(location)}"
        
        soup = self._request(url)
        
        if not soup:
            return []
        
        results = []
        cards = soup.select('[data-test="jobListing"]') or soup.select('.react-job-listing')
        
        for card in cards[:max_results]:
            job = self._parse_job_card(card)
            if job and job.title:
                results.append(job)
                print(f"  Found: {job.title} at {job.company}")
        
        return results
    
    def _parse_job_card(self, card) -> Optional[GlassdoorJob]:
        try:
            job = GlassdoorJob()
            
            job.job_id = card.get('data-id') or card.get('data-job-id')
            
            # Title
            title_el = card.select_one('[data-test="job-title"]') or card.select_one('.jobTitle')
            if title_el:
                job.title = title_el.get_text(strip=True)
                href = title_el.get('href') if title_el.name == 'a' else None
                if not href:
                    link = title_el.select_one('a')
                    if link:
                        href = link.get('href')
                if href:
                    job.url = self.BASE_URL + href if href.startswith('/') else href
            
            # Company
            company_el = card.select_one('[data-test="employer-name"]') or card.select_one('.employer-name')
            if company_el:
                job.company = company_el.get_text(strip=True)
            
            # Location
            loc_el = card.select_one('[data-test="emp-location"]') or card.select_one('.job-location')
            if loc_el:
                job.location = loc_el.get_text(strip=True)
            
            # Salary
            salary_el = card.select_one('[data-test="salary"]') or card.select_one('.salary-estimate')
            if salary_el:
                job.salary_estimate = salary_el.get_text(strip=True)
            
            # Easy Apply
            easy_el = card.select_one('[data-test="easy-apply"]')
            job.easy_apply = bool(easy_el)
            
            from datetime import datetime
            job.scraped_at = datetime.now().isoformat()
            
            return job
        except Exception as e:
            return None


def search_glassdoor_companies(query: str, max_results: int = 20) -> List[Dict]:
    ant = GlassdoorAnt()
    results = ant.search_companies(query, max_results)
    return [r.to_dict() for r in results]


def search_glassdoor_jobs(query: str, location: str = "", max_results: int = 25) -> List[Dict]:
    ant = GlassdoorAnt()
    results = ant.search_jobs(query, location, max_results)
    return [r.to_dict() for r in results]


if __name__ == '__main__':
    print("Searching companies...")
    companies = search_glassdoor_companies("Google", max_results=5)
    for c in companies:
        print(f"  {c['name']} - {c['overall_rating']} stars")
