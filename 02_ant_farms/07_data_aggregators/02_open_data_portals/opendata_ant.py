"""
Open Data Portal Scraper

FREE and LEGAL to use!
Many portals use CKAN or Socrata APIs.
"""

import time
from typing import Optional, List, Dict
from dataclasses import dataclass, field, asdict
from datetime import datetime
import requests


@dataclass
class OpenDataset:
    """Data model for an open dataset."""
    dataset_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    organization: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    resources: List[Dict] = field(default_factory=list)
    license: Optional[str] = None
    created: Optional[str] = None
    modified: Optional[str] = None
    
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class CKANClient:
    """
    Client for CKAN-based open data portals.
    
    Many government portals use CKAN:
    - data.gov
    - data.gov.uk
    - Many city/state portals
    
    Usage:
        client = CKANClient("https://catalog.data.gov")
        datasets = client.search("climate")
    """
    
    def __init__(self, base_url: str, delay: float = 0.5):
        """
        Args:
            base_url: Portal base URL (e.g., "https://catalog.data.gov")
            delay: Delay between requests
        """
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/3"
        self.delay = delay
        self.session = requests.Session()
    
    def _request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        time.sleep(self.delay)
        
        try:
            url = f"{self.api_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                return data.get('result')
            return None
            
        except Exception as e:
            print(f"API request failed: {e}")
            return None
    
    def search(self, query: str, rows: int = 20) -> List[OpenDataset]:
        """
        Search for datasets.
        
        Args:
            query: Search query
            rows: Maximum results
            
        Returns:
            List of OpenDataset objects
        """
        result = self._request('/action/package_search', {
            'q': query,
            'rows': rows
        })
        
        if not result:
            return []
        
        datasets = []
        for item in result.get('results', []):
            dataset = self._parse_dataset(item)
            datasets.append(dataset)
        
        return datasets
    
    def get_dataset(self, dataset_id: str) -> Optional[OpenDataset]:
        """Get dataset by ID."""
        result = self._request('/action/package_show', {'id': dataset_id})
        
        if not result:
            return None
        
        return self._parse_dataset(result)
    
    def _parse_dataset(self, data: Dict) -> OpenDataset:
        dataset = OpenDataset()
        
        dataset.dataset_id = data.get('id') or data.get('name')
        dataset.title = data.get('title')
        dataset.description = data.get('notes')
        dataset.url = f"{self.base_url}/dataset/{dataset.dataset_id}"
        
        org = data.get('organization', {})
        dataset.organization = org.get('title') if org else None
        
        dataset.tags = [t.get('name') for t in data.get('tags', [])]
        dataset.license = data.get('license_title')
        dataset.created = data.get('metadata_created')
        dataset.modified = data.get('metadata_modified')
        
        # Resources (downloadable files)
        for res in data.get('resources', []):
            dataset.resources.append({
                'name': res.get('name'),
                'format': res.get('format'),
                'url': res.get('url'),
                'size': res.get('size')
            })
        
        dataset.scraped_at = datetime.now().isoformat()
        
        return dataset
    
    def list_organizations(self) -> List[Dict]:
        """List all organizations."""
        result = self._request('/action/organization_list', {'all_fields': True})
        return result or []
    
    def list_tags(self) -> List[str]:
        """List all tags."""
        result = self._request('/action/tag_list')
        return result or []


class SocrataClient:
    """
    Client for Socrata-based open data portals.
    
    Many city portals use Socrata:
    - NYC Open Data
    - Chicago Data Portal
    - Many others
    """
    
    def __init__(self, domain: str, app_token: str = None, delay: float = 0.5):
        """
        Args:
            domain: Portal domain (e.g., "data.cityofnewyork.us")
            app_token: Optional Socrata app token for higher rate limits
        """
        self.domain = domain
        self.app_token = app_token
        self.delay = delay
        self.session = requests.Session()
        
        if app_token:
            self.session.headers['X-App-Token'] = app_token
    
    def _request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        time.sleep(self.delay)
        
        try:
            url = f"https://{self.domain}{endpoint}"
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def search(self, query: str, limit: int = 20) -> List[Dict]:
        """Search for datasets."""
        # Use discovery API
        params = {
            'q': query,
            'limit': limit
        }
        
        result = self._request('/api/catalog/v1', params)
        
        if not result:
            return []
        
        return result.get('results', [])
    
    def get_dataset(self, dataset_id: str, limit: int = 1000) -> List[Dict]:
        """
        Get dataset records.
        
        Args:
            dataset_id: 4x4 dataset ID (e.g., "abc1-defg")
            limit: Max records
        """
        endpoint = f"/resource/{dataset_id}.json"
        return self._request(endpoint, {'$limit': limit}) or []


# Convenience functions
def search_data_gov(query: str, max_results: int = 20) -> List[Dict]:
    """Search US Data.gov."""
    client = CKANClient("https://catalog.data.gov")
    datasets = client.search(query, max_results)
    return [d.to_dict() for d in datasets]


def search_nyc_opendata(query: str, max_results: int = 20) -> List[Dict]:
    """Search NYC Open Data."""
    client = SocrataClient("data.cityofnewyork.us")
    return client.search(query, max_results)


if __name__ == '__main__':
    print("Searching Data.gov for climate datasets...")
    datasets = search_data_gov("climate", max_results=5)
    
    for ds in datasets:
        print(f"\n{ds['title']}")
        print(f"  Org: {ds['organization']}")
        print(f"  Resources: {len(ds['resources'])} files")
