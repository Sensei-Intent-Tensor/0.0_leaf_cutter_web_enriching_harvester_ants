"""
SEC EDGAR Scraper

This scrapes PUBLIC DOMAIN government data from the SEC.
Completely legal, but please respect rate limits.

SEC Guidelines:
- Max 10 requests per second
- Include email in User-Agent header
- Use bulk downloads for large data needs
"""

import re
import json
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import requests


@dataclass
class SECFiling:
    """Data model for an SEC filing."""
    accession_number: Optional[str] = None
    cik: Optional[str] = None
    company_name: Optional[str] = None
    form_type: Optional[str] = None
    filed_date: Optional[str] = None
    accepted_date: Optional[str] = None
    document_url: Optional[str] = None
    filing_url: Optional[str] = None
    description: Optional[str] = None
    file_number: Optional[str] = None
    
    # Metadata
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SECCompany:
    """Data model for an SEC-registered company."""
    cik: Optional[str] = None
    name: Optional[str] = None
    tickers: List[str] = field(default_factory=list)
    exchanges: List[str] = field(default_factory=list)
    sic: Optional[str] = None
    sic_description: Optional[str] = None
    state: Optional[str] = None
    state_of_incorporation: Optional[str] = None
    fiscal_year_end: Optional[str] = None
    filings: List[SECFiling] = field(default_factory=list)
    
    # Metadata
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d['filings'] = [f.to_dict() if isinstance(f, SECFiling) else f for f in self.filings]
        return d


class EDGARAnt:
    """
    SEC EDGAR scraper for public company filings.
    
    This accesses PUBLIC DOMAIN data. Legal to use.
    
    Usage:
        ant = EDGARAnt(email="your@email.com")
        company = ant.get_company_filings("0000320193")  # Apple
        filings = ant.search_filings("10-K", ticker="AAPL")
    """
    
    # SEC endpoints
    BASE_URL = "https://www.sec.gov"
    DATA_URL = "https://data.sec.gov"
    SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
    
    def __init__(self, email: str = "anonymous@example.com", 
                 delay: float = 0.1):
        """
        Args:
            email: Your email for User-Agent (SEC requests this)
            delay: Delay between requests (min 0.1s for 10 req/s limit)
        """
        self.email = email
        self.delay = max(delay, 0.1)  # Enforce minimum delay
        self.session = requests.Session()
        self._update_headers()
    
    def _update_headers(self):
        """Set headers per SEC requirements."""
        self.session.headers.update({
            'User-Agent': f'DataScraper/1.0 ({self.email})',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
        })
    
    def _request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Make request with rate limiting."""
        time.sleep(self.delay)
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.JSONDecodeError:
            # Some endpoints return HTML
            return {'html': response.text}
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def _request_text(self, url: str) -> Optional[str]:
        """Get text content."""
        time.sleep(self.delay)
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def lookup_cik(self, ticker: str) -> Optional[str]:
        """
        Look up CIK by ticker symbol.
        
        Args:
            ticker: Stock ticker (e.g., "AAPL")
            
        Returns:
            CIK number or None
        """
        # Use SEC's company tickers JSON
        url = f"{self.DATA_URL}/submissions/CIK0000000000.json"
        
        # Alternative: search the tickers file
        tickers_url = "https://www.sec.gov/files/company_tickers.json"
        data = self._request(tickers_url)
        
        if data and isinstance(data, dict):
            ticker = ticker.upper()
            for key, company in data.items():
                if company.get('ticker') == ticker:
                    return str(company.get('cik_str', '')).zfill(10)
        
        return None
    
    def get_company_info(self, cik: str) -> Optional[SECCompany]:
        """
        Get company information and recent filings.
        
        Args:
            cik: Central Index Key (with or without leading zeros)
            
        Returns:
            SECCompany with filings
        """
        # Normalize CIK
        cik = str(cik).zfill(10)
        
        url = f"{self.DATA_URL}/submissions/CIK{cik}.json"
        data = self._request(url)
        
        if not data:
            return None
        
        return self._parse_company_data(data, cik)
    
    def _parse_company_data(self, data: Dict, cik: str) -> SECCompany:
        """Parse company submissions JSON."""
        company = SECCompany(cik=cik)
        
        company.name = data.get('name')
        company.tickers = data.get('tickers', [])
        company.exchanges = data.get('exchanges', [])
        company.sic = data.get('sic')
        company.sic_description = data.get('sicDescription')
        company.state = data.get('stateOfIncorporation')
        company.fiscal_year_end = data.get('fiscalYearEnd')
        
        # Parse recent filings
        filings_data = data.get('filings', {}).get('recent', {})
        
        if filings_data:
            accessions = filings_data.get('accessionNumber', [])
            forms = filings_data.get('form', [])
            dates = filings_data.get('filingDate', [])
            docs = filings_data.get('primaryDocument', [])
            descs = filings_data.get('primaryDocDescription', [])
            
            for i in range(min(len(accessions), 100)):  # Limit to 100
                filing = SECFiling(
                    accession_number=accessions[i] if i < len(accessions) else None,
                    cik=cik,
                    company_name=company.name,
                    form_type=forms[i] if i < len(forms) else None,
                    filed_date=dates[i] if i < len(dates) else None,
                    description=descs[i] if i < len(descs) else None,
                )
                
                # Build document URL
                if filing.accession_number and i < len(docs):
                    acc_no_dashes = filing.accession_number.replace('-', '')
                    doc_name = docs[i]
                    filing.document_url = (
                        f"{self.BASE_URL}/Archives/edgar/data/{cik}/"
                        f"{acc_no_dashes}/{doc_name}"
                    )
                    filing.filing_url = (
                        f"{self.BASE_URL}/cgi-bin/browse-edgar?action=getcompany"
                        f"&CIK={cik}&type={filing.form_type}&dateb=&owner=include&count=40"
                    )
                
                company.filings.append(filing)
        
        company.scraped_at = datetime.now().isoformat()
        return company
    
    def get_filing_document(self, document_url: str) -> Optional[str]:
        """
        Get the text content of a filing document.
        
        Args:
            document_url: URL to the filing document
            
        Returns:
            Document text content
        """
        return self._request_text(document_url)
    
    def search_filings(self, form_type: str = None, 
                       ticker: str = None,
                       company_name: str = None,
                       date_from: str = None,
                       date_to: str = None,
                       max_results: int = 100) -> List[SECFiling]:
        """
        Search SEC filings.
        
        Args:
            form_type: Filing type (e.g., "10-K", "10-Q", "8-K")
            ticker: Stock ticker
            company_name: Company name search
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            max_results: Maximum results
            
        Returns:
            List of SECFiling objects
        """
        # If ticker provided, get CIK first
        cik = None
        if ticker:
            cik = self.lookup_cik(ticker)
            if cik:
                # Get company filings directly
                company = self.get_company_info(cik)
                if company:
                    filings = company.filings
                    if form_type:
                        filings = [f for f in filings if f.form_type == form_type]
                    return filings[:max_results]
        
        # Use full-text search
        params = {
            'q': company_name or '*',
            'dateRange': 'custom',
            'startdt': date_from or '2020-01-01',
            'enddt': date_to or datetime.now().strftime('%Y-%m-%d'),
        }
        
        if form_type:
            params['forms'] = form_type
        
        data = self._request(self.SEARCH_URL, params)
        
        if not data or 'hits' not in data:
            return []
        
        results = []
        for hit in data.get('hits', {}).get('hits', [])[:max_results]:
            source = hit.get('_source', {})
            
            filing = SECFiling(
                accession_number=source.get('adsh'),
                cik=source.get('ciks', [''])[0] if source.get('ciks') else None,
                company_name=source.get('display_names', [''])[0] if source.get('display_names') else None,
                form_type=source.get('form'),
                filed_date=source.get('file_date'),
            )
            filing.scraped_at = datetime.now().isoformat()
            results.append(filing)
        
        return results
    
    def get_insider_transactions(self, cik: str, 
                                 max_results: int = 50) -> List[Dict]:
        """
        Get insider trading (Form 4) filings for a company.
        
        Args:
            cik: Company CIK
            max_results: Maximum results
            
        Returns:
            List of insider transaction dictionaries
        """
        company = self.get_company_info(cik)
        if not company:
            return []
        
        form4_filings = [
            f for f in company.filings 
            if f.form_type == '4'
        ][:max_results]
        
        return [f.to_dict() for f in form4_filings]
    
    def get_institutional_holdings(self, cik: str) -> List[Dict]:
        """
        Get 13F institutional holdings filings.
        
        Args:
            cik: Company CIK
            
        Returns:
            List of 13F filings
        """
        company = self.get_company_info(cik)
        if not company:
            return []
        
        form13f_filings = [
            f for f in company.filings 
            if '13F' in (f.form_type or '')
        ]
        
        return [f.to_dict() for f in form13f_filings]


def get_company_filings(ticker_or_cik: str, 
                        form_type: str = None) -> Optional[Dict]:
    """
    Get SEC filings for a company.
    
    Args:
        ticker_or_cik: Stock ticker (AAPL) or CIK number
        form_type: Optional filter by form type
        
    Returns:
        Company data with filings
    """
    ant = EDGARAnt()
    
    # Check if it's a ticker or CIK
    if ticker_or_cik.isdigit():
        cik = ticker_or_cik
    else:
        cik = ant.lookup_cik(ticker_or_cik)
        if not cik:
            print(f"Could not find CIK for ticker: {ticker_or_cik}")
            return None
    
    company = ant.get_company_info(cik)
    if not company:
        return None
    
    result = company.to_dict()
    
    if form_type:
        result['filings'] = [
            f for f in result['filings'] 
            if f.get('form_type') == form_type
        ]
    
    return result


if __name__ == '__main__':
    # Example: Get Apple's recent 10-K filings
    print("Fetching Apple (AAPL) SEC filings...")
    
    result = get_company_filings("AAPL", form_type="10-K")
    
    if result:
        print(f"\nCompany: {result['name']}")
        print(f"CIK: {result['cik']}")
        print(f"Tickers: {result['tickers']}")
        print(f"\nRecent 10-K Filings:")
        
        for filing in result['filings'][:5]:
            print(f"  {filing['filed_date']}: {filing['form_type']} - {filing['description']}")
