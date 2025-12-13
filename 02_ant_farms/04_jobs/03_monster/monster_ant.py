"""
Monster Job Board Scraper

For educational purposes.
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
class MonsterJob:
    """Data model for a Monster job listing."""
    job_id: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    job_type: Optional[str] = None
    posted_date: Optional[str] = None
    description: Optional[str] = None
    
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class MonsterAnt:
    """Monster job board scraper."""
    
    BASE_URL = "https://www.monster.com"
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    ]
    
    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random.choice(self.USER_AGENTS),
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
    
    def search(self, query: str, location: str = "",
               max_results: int = 25) -> List[MonsterJob]:
        """Search for jobs."""
        url = f"{self.BASE_URL}/jobs/search?q={quote_plus(query)}&where={quote_plus(location)}"
        soup = self._request(url)
        
        if not soup:
            return []
        
        results = []
        cards = soup.select('[data-testid="svx-job-result-card"]') or soup.select('.job-cardstyle__JobCardWrapper')
        
        for card in cards[:max_results]:
            job = self._parse_job_card(card)
            if job and job.title:
                results.append(job)
                print(f"  Found: {job.title} at {job.company}")
        
        return results
    
    def _parse_job_card(self, card) -> Optional[MonsterJob]:
        try:
            job = MonsterJob()
            
            # Title and URL
            title_el = card.select_one('[data-testid="jobTitle"]') or card.select_one('.job-cardstyle__JobTitle')
            if title_el:
                job.title = title_el.get_text(strip=True)
                link = title_el.select_one('a') or title_el
                if link.name == 'a':
                    job.url = link.get('href', '')
            
            # Company
            company_el = card.select_one('[data-testid="company"]') or card.select_one('.job-cardstyle__CompanyName')
            if company_el:
                job.company = company_el.get_text(strip=True)
            
            # Location
            loc_el = card.select_one('[data-testid="location"]') or card.select_one('.job-cardstyle__JobLocation')
            if loc_el:
                job.location = loc_el.get_text(strip=True)
            
            # Posted date
            date_el = card.select_one('[data-testid="posted-date"]')
            if date_el:
                job.posted_date = date_el.get_text(strip=True)
            
            from datetime import datetime
            job.scraped_at = datetime.now().isoformat()
            
            return job
        except:
            return None


def search_monster(query: str, location: str = "", max_results: int = 25) -> List[Dict]:
    ant = MonsterAnt()
    results = ant.search(query, location, max_results)
    return [r.to_dict() for r in results]


if __name__ == '__main__':
    results = search_monster("data analyst", "Chicago, IL", max_results=10)
    for job in results:
        print(f"{job['title']} at {job['company']} - {job['location']}")
