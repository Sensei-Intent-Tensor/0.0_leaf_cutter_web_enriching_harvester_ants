"""
Indeed Job Listings Scraper

WARNING: For educational purposes. Indeed has anti-scraping measures.
Consider Indeed Publisher API for production.
"""

import re
import json
import time
import random
from typing import Optional, List, Dict
from dataclasses import dataclass, field, asdict
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
import requests


@dataclass
class IndeedJob:
    """Data model for an Indeed job listing."""
    job_id: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    job_type: Optional[str] = None
    description: Optional[str] = None
    posted_date: Optional[str] = None
    remote: Optional[str] = None
    benefits: List[str] = field(default_factory=list)
    
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class IndeedAnt:
    """
    Indeed job listings scraper.
    
    Usage:
        ant = IndeedAnt()
        jobs = ant.search("software engineer", "San Francisco, CA")
    """
    
    BASE_URL = "https://www.indeed.com"
    
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
            response.raise_for_status()
            return BeautifulSoup(response.text, 'lxml')
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def search(self, query: str, location: str = "",
               max_results: int = 25) -> List[IndeedJob]:
        """
        Search Indeed for jobs.
        
        Args:
            query: Job title or keywords
            location: City, state, or zip
            max_results: Maximum results
        """
        results = []
        start = 0
        
        while len(results) < max_results:
            url = f"{self.BASE_URL}/jobs?q={quote_plus(query)}&l={quote_plus(location)}&start={start}"
            soup = self._request(url)
            
            if not soup:
                break
            
            # Find job cards
            cards = soup.select('.job_seen_beacon') or soup.select('.jobsearch-ResultsList > li')
            
            if not cards:
                break
            
            for card in cards:
                if len(results) >= max_results:
                    break
                job = self._parse_job_card(card)
                if job and job.title:
                    results.append(job)
                    print(f"  Found: {job.title} at {job.company}")
            
            start += 10
            if len(cards) < 10:
                break
        
        return results
    
    def _parse_job_card(self, card) -> Optional[IndeedJob]:
        try:
            job = IndeedJob()
            
            # Title and URL
            title_el = card.select_one('h2.jobTitle a') or card.select_one('.jobTitle a')
            if title_el:
                job.title = title_el.get_text(strip=True)
                href = title_el.get('href', '')
                job.url = urljoin(self.BASE_URL, href)
                # Extract job ID
                match = re.search(r'jk=([a-f0-9]+)', href)
                if match:
                    job.job_id = match.group(1)
            
            # Company
            company_el = card.select_one('[data-testid="company-name"]') or card.select_one('.companyName')
            if company_el:
                job.company = company_el.get_text(strip=True)
            
            # Location
            loc_el = card.select_one('[data-testid="text-location"]') or card.select_one('.companyLocation')
            if loc_el:
                job.location = loc_el.get_text(strip=True)
                if 'remote' in job.location.lower():
                    job.remote = 'remote'
            
            # Salary
            salary_el = card.select_one('[data-testid="attribute_snippet_testid"]') or card.select_one('.salary-snippet-container')
            if salary_el:
                job.salary = salary_el.get_text(strip=True)
                self._parse_salary(job)
            
            # Job type
            for tag in card.select('.metadata'):
                text = tag.get_text(strip=True).lower()
                if any(t in text for t in ['full-time', 'part-time', 'contract', 'temporary']):
                    job.job_type = text
                    break
            
            # Description snippet
            desc_el = card.select_one('.job-snippet') or card.select_one('[data-testid="job-snippet"]')
            if desc_el:
                job.description = desc_el.get_text(strip=True)
            
            # Posted date
            date_el = card.select_one('.date') or card.select_one('[data-testid="myJobsStateDate"]')
            if date_el:
                job.posted_date = date_el.get_text(strip=True)
            
            from datetime import datetime
            job.scraped_at = datetime.now().isoformat()
            
            return job
        except Exception as e:
            return None
    
    def _parse_salary(self, job: IndeedJob):
        """Parse salary range from string."""
        if not job.salary:
            return
        
        text = job.salary.lower()
        
        # Find all numbers
        numbers = re.findall(r'[\d,]+(?:\.\d+)?', text.replace(',', ''))
        numbers = [float(n) for n in numbers if n]
        
        # Determine if hourly/yearly
        multiplier = 1
        if 'hour' in text:
            multiplier = 2080  # Approximate annual
        elif 'month' in text:
            multiplier = 12
        elif 'week' in text:
            multiplier = 52
        
        if len(numbers) >= 2:
            job.salary_min = numbers[0] * multiplier
            job.salary_max = numbers[1] * multiplier
        elif len(numbers) == 1:
            job.salary_min = numbers[0] * multiplier
            job.salary_max = job.salary_min
    
    def get_job_details(self, job_id: str) -> Optional[IndeedJob]:
        """Get full job details."""
        url = f"{self.BASE_URL}/viewjob?jk={job_id}"
        soup = self._request(url)
        
        if not soup:
            return None
        
        return self._parse_job_page(soup, job_id, url)
    
    def _parse_job_page(self, soup: BeautifulSoup,
                       job_id: str, url: str) -> Optional[IndeedJob]:
        try:
            job = IndeedJob(job_id=job_id, url=url)
            
            # Title
            title_el = soup.select_one('.jobsearch-JobInfoHeader-title')
            if title_el:
                job.title = title_el.get_text(strip=True)
            
            # Company
            company_el = soup.select_one('[data-company-name]') or soup.select_one('.jobsearch-CompanyInfoContainer a')
            if company_el:
                job.company = company_el.get_text(strip=True)
            
            # Location
            loc_el = soup.select_one('[data-testid="job-location"]') or soup.select_one('.jobsearch-JobInfoHeader-subtitle > div:nth-child(2)')
            if loc_el:
                job.location = loc_el.get_text(strip=True)
            
            # Full description
            desc_el = soup.select_one('#jobDescriptionText')
            if desc_el:
                job.description = desc_el.get_text(strip=True)
            
            # Benefits
            benefits_els = soup.select('[data-testid="benefits-list"] li')
            job.benefits = [b.get_text(strip=True) for b in benefits_els]
            
            from datetime import datetime
            job.scraped_at = datetime.now().isoformat()
            
            return job
        except Exception as e:
            return None


def search_indeed(query: str, location: str = "", max_results: int = 25) -> List[Dict]:
    ant = IndeedAnt()
    results = ant.search(query, location, max_results)
    return [r.to_dict() for r in results]


if __name__ == '__main__':
    results = search_indeed("python developer", "New York, NY", max_results=10)
    for job in results:
        print(f"{job['title']} at {job['company']} - {job['salary'] or 'No salary listed'}")
