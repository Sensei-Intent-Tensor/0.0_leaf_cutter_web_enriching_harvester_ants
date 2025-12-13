"""
IMDB Movie/TV Scraper

For non-commercial use. Consider using:
- IMDB Datasets: https://datasets.imdbws.com/
- OMDB API: http://www.omdbapi.com/
- TMDB API: https://www.themoviedb.org/documentation/api
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
class IMDBTitle:
    """Data model for an IMDB title (movie/show)."""
    imdb_id: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    original_title: Optional[str] = None
    year: Optional[int] = None
    end_year: Optional[int] = None  # For TV series
    title_type: Optional[str] = None  # movie, tvSeries, etc.
    rating: Optional[float] = None
    vote_count: Optional[int] = None
    runtime_minutes: Optional[int] = None
    genres: List[str] = field(default_factory=list)
    directors: List[str] = field(default_factory=list)
    writers: List[str] = field(default_factory=list)
    cast: List[Dict] = field(default_factory=list)  # [{name, character}]
    plot: Optional[str] = None
    poster_url: Optional[str] = None
    release_date: Optional[str] = None
    countries: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class IMDBAnt:
    """
    IMDB scraper for movie and TV show data.
    
    Usage:
        ant = IMDBAnt()
        movie = ant.get_title("tt0111161")  # Shawshank Redemption
        results = ant.search("inception")
    """
    
    BASE_URL = "https://www.imdb.com"
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    ]
    
    def __init__(self, delay: float = 2.0):
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
        time.sleep(self.delay + random.random())
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'lxml')
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search IMDB for titles.
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            List of search results
        """
        url = f"{self.BASE_URL}/find/?q={quote_plus(query)}&s=tt"
        soup = self._request(url)
        
        if not soup:
            return []
        
        results = []
        
        # Find result items
        items = soup.select('.ipc-metadata-list-summary-item')
        
        for item in items[:max_results]:
            result = {}
            
            # Title and URL
            link = item.select_one('a[href*="/title/tt"]')
            if link:
                result['title'] = link.get_text(strip=True)
                href = link.get('href', '')
                result['url'] = self.BASE_URL + href.split('?')[0]
                match = re.search(r'(tt\d+)', href)
                if match:
                    result['imdb_id'] = match.group(1)
            
            # Year
            year_el = item.select_one('.ipc-metadata-list-summary-item__li')
            if year_el:
                match = re.search(r'(\d{4})', year_el.get_text())
                if match:
                    result['year'] = int(match.group(1))
            
            # Type and additional info
            meta_items = item.select('.ipc-metadata-list-summary-item__li')
            for meta in meta_items:
                text = meta.get_text(strip=True)
                if text in ['Movie', 'TV Series', 'TV Mini Series', 'Short', 'Video']:
                    result['type'] = text
            
            if result.get('imdb_id'):
                results.append(result)
        
        return results
    
    def get_title(self, imdb_id: str) -> Optional[IMDBTitle]:
        """
        Get full details for a title.
        
        Args:
            imdb_id: IMDB ID (e.g., "tt0111161")
            
        Returns:
            IMDBTitle or None
        """
        url = f"{self.BASE_URL}/title/{imdb_id}/"
        soup = self._request(url)
        
        if not soup:
            return None
        
        return self._parse_title_page(soup, imdb_id, url)
    
    def _parse_title_page(self, soup: BeautifulSoup,
                         imdb_id: str, url: str) -> Optional[IMDBTitle]:
        try:
            title = IMDBTitle(imdb_id=imdb_id, url=url)
            
            # Try to get JSON-LD data first (most reliable)
            script = soup.select_one('script[type="application/ld+json"]')
            if script:
                try:
                    data = json.loads(script.string)
                    title.title = data.get('name')
                    title.plot = data.get('description')
                    title.poster_url = data.get('image')
                    
                    # Rating
                    agg_rating = data.get('aggregateRating', {})
                    if agg_rating:
                        title.rating = float(agg_rating.get('ratingValue', 0))
                        title.vote_count = int(agg_rating.get('ratingCount', 0))
                    
                    # Genres
                    genre = data.get('genre', [])
                    if isinstance(genre, list):
                        title.genres = genre
                    elif isinstance(genre, str):
                        title.genres = [genre]
                    
                    # Directors
                    directors = data.get('director', [])
                    if not isinstance(directors, list):
                        directors = [directors]
                    title.directors = [d.get('name') for d in directors if isinstance(d, dict)]
                    
                    # Cast
                    actors = data.get('actor', [])
                    if not isinstance(actors, list):
                        actors = [actors]
                    title.cast = [{'name': a.get('name')} for a in actors if isinstance(a, dict)]
                    
                    # Duration
                    duration = data.get('duration', '')
                    if duration:
                        match = re.search(r'PT(\d+)H?(\d*)M?', duration)
                        if match:
                            hours = int(match.group(1) or 0)
                            mins = int(match.group(2) or 0)
                            title.runtime_minutes = hours * 60 + mins
                    
                    # Release date
                    title.release_date = data.get('datePublished')
                    
                except json.JSONDecodeError:
                    pass
            
            # Fallback/supplement with HTML parsing
            if not title.title:
                title_el = soup.select_one('h1[data-testid="hero__pageTitle"]')
                if title_el:
                    title.title = title_el.get_text(strip=True)
            
            # Year
            year_el = soup.select_one('[data-testid="hero-title-block__metadata"] a')
            if year_el:
                match = re.search(r'(\d{4})', year_el.get_text())
                if match:
                    title.year = int(match.group(1))
            
            # Type
            type_el = soup.select_one('[data-testid="hero-title-block__metadata"] li')
            if type_el:
                text = type_el.get_text(strip=True)
                if 'TV' in text or 'Series' in text:
                    title.title_type = 'tvSeries'
                else:
                    title.title_type = 'movie'
            
            from datetime import datetime
            title.scraped_at = datetime.now().isoformat()
            
            return title
            
        except Exception as e:
            print(f"Error parsing title: {e}")
            return None
    
    def get_top_movies(self, limit: int = 50) -> List[Dict]:
        """Get IMDB Top 250 movies."""
        url = f"{self.BASE_URL}/chart/top/"
        soup = self._request(url)
        
        if not soup:
            return []
        
        results = []
        
        rows = soup.select('.ipc-metadata-list-summary-item')
        
        for i, row in enumerate(rows[:limit], 1):
            movie = {'rank': i}
            
            link = row.select_one('a[href*="/title/tt"]')
            if link:
                movie['title'] = link.get_text(strip=True)
                href = link.get('href', '')
                match = re.search(r'(tt\d+)', href)
                if match:
                    movie['imdb_id'] = match.group(1)
            
            rating_el = row.select_one('.ipc-rating-star--rating')
            if rating_el:
                movie['rating'] = float(rating_el.get_text(strip=True))
            
            year_el = row.select_one('.cli-title-metadata-item')
            if year_el:
                match = re.search(r'(\d{4})', year_el.get_text())
                if match:
                    movie['year'] = int(match.group(1))
            
            if movie.get('imdb_id'):
                results.append(movie)
        
        return results


def search_imdb(query: str, max_results: int = 10) -> List[Dict]:
    """Search IMDB for titles."""
    ant = IMDBAnt()
    return ant.search(query, max_results)


def get_imdb_title(imdb_id: str) -> Optional[Dict]:
    """Get IMDB title by ID."""
    ant = IMDBAnt()
    title = ant.get_title(imdb_id)
    return title.to_dict() if title else None


if __name__ == '__main__':
    # Example: Get Shawshank Redemption
    print("Fetching: The Shawshank Redemption")
    movie = get_imdb_title("tt0111161")
    
    if movie:
        print(f"\nTitle: {movie['title']} ({movie['year']})")
        print(f"Rating: {movie['rating']}/10 ({movie['vote_count']} votes)")
        print(f"Genres: {', '.join(movie['genres'])}")
        print(f"Directors: {', '.join(movie['directors'])}")
        print(f"\nPlot: {movie['plot'][:200]}...")
