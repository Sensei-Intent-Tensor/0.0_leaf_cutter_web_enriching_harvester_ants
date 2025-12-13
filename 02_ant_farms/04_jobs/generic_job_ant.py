"""
Generic Job Ant
===============

Extracts job posting data from Schema.org JobPosting markup.

Many job sites include Schema.org structured data for SEO.
This ant extracts that data for clean, reliable job extraction.

Usage:
    ant = GenericJobAnt()
    result = ant.scrape('https://example.com/job/123')
    
    if result.success:
        print(result.data['title'])
        print(result.data['company'])
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


class GenericJobAnt:
    """
    Generic job scraper using Schema.org JobPosting.
    
    Works with any site implementing JobPosting schema.
    Falls back to HTML extraction if schema not found.
    """
    
    name = "generic_job_ant"
    
    # Common selectors for fallback extraction
    selectors = {
        'title': [
            'h1.job-title',
            'h1[data-job-title]',
            '.job-title h1',
            'h1',
        ],
        'company': [
            '.company-name',
            '[data-company]',
            '.employer-name',
            '.hiring-company',
        ],
        'location': [
            '.job-location',
            '[data-location]',
            '.location',
        ],
        'salary': [
            '.salary',
            '.compensation',
            '[data-salary]',
        ],
        'description': [
            '.job-description',
            '.description',
            '[data-description]',
            '#job-description',
        ],
    }
    
    def __init__(self, **kwargs):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml',
        })
    
    def scrape(self, url: str) -> ScrapeResult:
        """Scrape job posting from URL."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            return ScrapeResult(success=False, url=url, error=str(e))
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Try Schema.org first
        schema_data = self._extract_job_schema(soup)
        
        if schema_data:
            job = self._normalize_schema(schema_data)
            job['source'] = urlparse(url).netloc
            job['url'] = url
            job['_extraction_method'] = 'schema'
            
            return ScrapeResult(success=True, url=url, data=job)
        
        # Fallback to HTML extraction
        job = self._extract_from_html(soup, url)
        job['_extraction_method'] = 'html_fallback'
        
        return ScrapeResult(success=True, url=url, data=job)
    
    def _extract_job_schema(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract Schema.org JobPosting data."""
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                
                # Handle different structures
                if isinstance(data, list):
                    for item in data:
                        if self._is_job_posting(item):
                            return item
                elif self._is_job_posting(data):
                    return data
                elif isinstance(data.get('@graph'), list):
                    for item in data['@graph']:
                        if self._is_job_posting(item):
                            return item
                            
            except (json.JSONDecodeError, TypeError):
                continue
        
        return None
    
    def _is_job_posting(self, data: dict) -> bool:
        """Check if data is a JobPosting schema."""
        schema_type = data.get('@type', '')
        if isinstance(schema_type, list):
            return 'JobPosting' in schema_type
        return schema_type == 'JobPosting'
    
    def _normalize_schema(self, schema: dict) -> dict:
        """Normalize JobPosting schema to standard format."""
        
        # Hiring organization
        org = schema.get('hiringOrganization', {})
        if isinstance(org, str):
            company = org
        else:
            company = org.get('name', '')
        
        # Location
        location = schema.get('jobLocation', {})
        if isinstance(location, list):
            location = location[0] if location else {}
        
        address = location.get('address', {})
        if isinstance(address, str):
            address = {'addressLocality': address}
        
        # Salary
        salary = schema.get('baseSalary', {})
        salary_value = salary.get('value', {})
        
        if isinstance(salary_value, dict):
            min_salary = salary_value.get('minValue')
            max_salary = salary_value.get('maxValue')
        else:
            min_salary = max_salary = salary_value
        
        # Employment type
        emp_type = schema.get('employmentType', '')
        if isinstance(emp_type, list):
            emp_type = ', '.join(emp_type)
        
        return {
            'title': schema.get('title', ''),
            'company': company,
            'company_url': org.get('url') if isinstance(org, dict) else None,
            
            'location': {
                'city': address.get('addressLocality', ''),
                'state': address.get('addressRegion', ''),
                'country': address.get('addressCountry', ''),
                'postal_code': address.get('postalCode', ''),
                'remote': 'remote' in str(location).lower(),
            },
            
            'salary': {
                'min': float(min_salary) if min_salary else None,
                'max': float(max_salary) if max_salary else None,
                'currency': salary.get('currency', 'USD'),
                'period': salary_value.get('unitText', 'YEAR') if isinstance(salary_value, dict) else 'YEAR',
            },
            
            'description': schema.get('description', ''),
            'employment_type': emp_type,
            'posted_date': schema.get('datePosted', ''),
            'valid_through': schema.get('validThrough', ''),
            'apply_url': schema.get('directApply') or schema.get('url', ''),
        }
    
    def _extract_from_html(self, soup: BeautifulSoup, url: str) -> dict:
        """Fallback HTML extraction."""
        
        def try_selectors(selector_list: List[str]) -> Optional[str]:
            for selector in selector_list:
                el = soup.select_one(selector)
                if el:
                    return el.get_text(strip=True)
            return None
        
        title = try_selectors(self.selectors['title'])
        company = try_selectors(self.selectors['company'])
        location = try_selectors(self.selectors['location'])
        salary_text = try_selectors(self.selectors['salary'])
        description = try_selectors(self.selectors['description'])
        
        # Parse salary if found
        salary = {'min': None, 'max': None, 'currency': 'USD', 'period': 'YEAR'}
        if salary_text:
            numbers = re.findall(r'[\d,]+', salary_text.replace(',', ''))
            if len(numbers) >= 2:
                salary['min'] = float(numbers[0])
                salary['max'] = float(numbers[1])
            elif len(numbers) == 1:
                salary['min'] = salary['max'] = float(numbers[0])
        
        return {
            'title': title,
            'company': company,
            'location': {
                'raw': location,
                'city': None,
                'state': None,
                'country': None,
                'remote': 'remote' in (location or '').lower(),
            },
            'salary': salary,
            'description': description,
            'employment_type': None,
            'posted_date': None,
            'apply_url': url,
            'source': urlparse(url).netloc,
            'url': url,
        }
    
    def scrape_many(self, urls: List[str]) -> List[ScrapeResult]:
        """Scrape multiple job URLs."""
        import time
        
        results = []
        for i, url in enumerate(urls):
            print(f"Scraping {i+1}/{len(urls)}: {url}")
            result = self.scrape(url)
            results.append(result)
            time.sleep(1)  # Rate limiting
        
        return results


if __name__ == "__main__":
    ant = GenericJobAnt()
    
    # Test URL
    result = ant.scrape('https://example.com/job/123')
    
    if result.success:
        job = result.data
        print(f"Title: {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Method: {job['_extraction_method']}")
