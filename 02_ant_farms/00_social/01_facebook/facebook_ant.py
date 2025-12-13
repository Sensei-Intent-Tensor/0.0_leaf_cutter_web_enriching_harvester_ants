"""
Facebook API Wrapper

⚠️ CRITICAL: Facebook/Meta prohibits scraping.
This wrapper uses the OFFICIAL Graph API only.

Requires:
- Facebook Developer App
- Access Token
- Proper permissions

pip install facebook-sdk
"""

import os
from typing import Optional, List, Dict
from dataclasses import dataclass, field, asdict
from datetime import datetime

try:
    import facebook
    FACEBOOK_SDK_AVAILABLE = True
except ImportError:
    FACEBOOK_SDK_AVAILABLE = False


@dataclass
class FacebookPage:
    """Data model for a Facebook page."""
    page_id: Optional[str] = None
    name: Optional[str] = None
    username: Optional[str] = None
    about: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    fan_count: Optional[int] = None
    category: Optional[str] = None
    link: Optional[str] = None
    
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class FacebookPost:
    """Data model for a Facebook post."""
    post_id: Optional[str] = None
    message: Optional[str] = None
    created_time: Optional[str] = None
    permalink_url: Optional[str] = None
    shares: int = 0
    reactions: int = 0
    comments: int = 0
    
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class FacebookAnt:
    """
    Facebook Graph API wrapper.
    
    This uses the OFFICIAL API - NOT scraping.
    Requires proper authentication and permissions.
    
    Usage:
        ant = FacebookAnt(access_token="YOUR_TOKEN")
        page = ant.get_page("facebook")
    """
    
    def __init__(self, access_token: str = None):
        """
        Args:
            access_token: Facebook access token
        """
        if not FACEBOOK_SDK_AVAILABLE:
            raise ImportError("facebook-sdk required: pip install facebook-sdk")
        
        self.access_token = access_token or os.getenv('FACEBOOK_ACCESS_TOKEN')
        
        if not self.access_token:
            raise ValueError("Facebook access token required")
        
        self.graph = facebook.GraphAPI(
            access_token=self.access_token,
            version="18.0"
        )
    
    def get_page(self, page_id: str) -> Optional[FacebookPage]:
        """
        Get Facebook page info.
        
        Args:
            page_id: Page ID or username
            
        Returns:
            FacebookPage or None
        """
        try:
            fields = 'id,name,username,about,description,website,fan_count,category,link'
            data = self.graph.get_object(id=page_id, fields=fields)
            
            page = FacebookPage()
            page.page_id = data.get('id')
            page.name = data.get('name')
            page.username = data.get('username')
            page.about = data.get('about')
            page.description = data.get('description')
            page.website = data.get('website')
            page.fan_count = data.get('fan_count')
            page.category = data.get('category')
            page.link = data.get('link')
            page.scraped_at = datetime.now().isoformat()
            
            return page
            
        except facebook.GraphAPIError as e:
            print(f"API error: {e}")
            return None
    
    def get_page_posts(self, page_id: str, limit: int = 25) -> List[FacebookPost]:
        """
        Get posts from a page.
        
        Args:
            page_id: Page ID
            limit: Maximum posts
            
        Returns:
            List of FacebookPost
        """
        try:
            fields = 'id,message,created_time,permalink_url,shares'
            data = self.graph.get_connections(
                id=page_id,
                connection_name='posts',
                fields=fields,
                limit=limit
            )
            
            posts = []
            for item in data.get('data', []):
                post = FacebookPost()
                post.post_id = item.get('id')
                post.message = item.get('message')
                post.created_time = item.get('created_time')
                post.permalink_url = item.get('permalink_url')
                post.shares = item.get('shares', {}).get('count', 0)
                post.scraped_at = datetime.now().isoformat()
                posts.append(post)
            
            return posts
            
        except facebook.GraphAPIError as e:
            print(f"API error: {e}")
            return []


def get_facebook_page(page_id: str, access_token: str) -> Optional[Dict]:
    """Get Facebook page info."""
    ant = FacebookAnt(access_token=access_token)
    page = ant.get_page(page_id)
    return page.to_dict() if page else None


if __name__ == '__main__':
    print("Facebook API requires:")
    print("1. Create app at developers.facebook.com")
    print("2. Generate access token")
    print("3. Set FACEBOOK_ACCESS_TOKEN environment variable")
    print()
    print("Example:")
    print('  ant = FacebookAnt(access_token="YOUR_TOKEN")')
    print('  page = ant.get_page("meta")')
