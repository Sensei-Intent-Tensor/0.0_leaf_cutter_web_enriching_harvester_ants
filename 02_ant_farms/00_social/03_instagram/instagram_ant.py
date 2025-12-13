"""
Instagram API Wrapper

Uses Instagram Graph API (via Facebook Graph API).
Requires business/creator account connected to Facebook Page.

Direct scraping is PROHIBITED by Instagram ToS.
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
class InstagramProfile:
    """Data model for an Instagram business profile."""
    ig_id: Optional[str] = None
    username: Optional[str] = None
    name: Optional[str] = None
    biography: Optional[str] = None
    followers_count: int = 0
    follows_count: int = 0
    media_count: int = 0
    profile_picture_url: Optional[str] = None
    website: Optional[str] = None
    
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class InstagramMedia:
    """Data model for Instagram media."""
    media_id: Optional[str] = None
    media_type: Optional[str] = None  # IMAGE, VIDEO, CAROUSEL_ALBUM
    caption: Optional[str] = None
    permalink: Optional[str] = None
    timestamp: Optional[str] = None
    like_count: int = 0
    comments_count: int = 0
    thumbnail_url: Optional[str] = None
    
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class InstagramAnt:
    """
    Instagram Graph API wrapper.
    
    Requires:
    - Facebook Developer App
    - Instagram Business/Creator Account
    - Account connected to Facebook Page
    - instagram_basic, instagram_manage_insights permissions
    
    Usage:
        ant = InstagramAnt(access_token="YOUR_TOKEN")
        profile = ant.get_profile(ig_user_id)
    """
    
    def __init__(self, access_token: str = None):
        if not FACEBOOK_SDK_AVAILABLE:
            raise ImportError("facebook-sdk required: pip install facebook-sdk")
        
        self.access_token = access_token or os.getenv('INSTAGRAM_ACCESS_TOKEN')
        
        if not self.access_token:
            raise ValueError("Instagram access token required")
        
        self.graph = facebook.GraphAPI(
            access_token=self.access_token,
            version="18.0"
        )
    
    def get_profile(self, ig_user_id: str) -> Optional[InstagramProfile]:
        """
        Get Instagram business profile.
        
        Args:
            ig_user_id: Instagram business account ID
            
        Returns:
            InstagramProfile or None
        """
        try:
            fields = 'id,username,name,biography,followers_count,follows_count,media_count,profile_picture_url,website'
            data = self.graph.get_object(id=ig_user_id, fields=fields)
            
            profile = InstagramProfile()
            profile.ig_id = data.get('id')
            profile.username = data.get('username')
            profile.name = data.get('name')
            profile.biography = data.get('biography')
            profile.followers_count = data.get('followers_count', 0)
            profile.follows_count = data.get('follows_count', 0)
            profile.media_count = data.get('media_count', 0)
            profile.profile_picture_url = data.get('profile_picture_url')
            profile.website = data.get('website')
            profile.scraped_at = datetime.now().isoformat()
            
            return profile
            
        except facebook.GraphAPIError as e:
            print(f"API error: {e}")
            return None
    
    def get_media(self, ig_user_id: str, limit: int = 25) -> List[InstagramMedia]:
        """
        Get media from business account.
        
        Args:
            ig_user_id: Instagram business account ID
            limit: Maximum media items
            
        Returns:
            List of InstagramMedia
        """
        try:
            fields = 'id,media_type,caption,permalink,timestamp,like_count,comments_count,thumbnail_url'
            data = self.graph.get_connections(
                id=ig_user_id,
                connection_name='media',
                fields=fields,
                limit=limit
            )
            
            media_list = []
            for item in data.get('data', []):
                media = InstagramMedia()
                media.media_id = item.get('id')
                media.media_type = item.get('media_type')
                media.caption = item.get('caption')
                media.permalink = item.get('permalink')
                media.timestamp = item.get('timestamp')
                media.like_count = item.get('like_count', 0)
                media.comments_count = item.get('comments_count', 0)
                media.thumbnail_url = item.get('thumbnail_url')
                media.scraped_at = datetime.now().isoformat()
                media_list.append(media)
            
            return media_list
            
        except facebook.GraphAPIError as e:
            print(f"API error: {e}")
            return []


if __name__ == '__main__':
    print("Instagram Graph API requires:")
    print("1. Facebook Developer App")
    print("2. Instagram Business/Creator Account")
    print("3. Account linked to Facebook Page")
    print("4. Proper API permissions")
