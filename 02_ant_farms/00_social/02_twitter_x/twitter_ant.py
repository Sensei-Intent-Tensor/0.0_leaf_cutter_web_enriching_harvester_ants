"""
Twitter/X API Wrapper

This uses the official X API. Direct scraping is not recommended
as X actively blocks scrapers and it violates ToS.

Requires: pip install tweepy
API Keys: https://developer.twitter.com/
"""

import os
from typing import Optional, List, Dict
from dataclasses import dataclass, field, asdict
from datetime import datetime

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False


@dataclass
class Tweet:
    """Data model for a Tweet."""
    tweet_id: Optional[str] = None
    text: Optional[str] = None
    author_id: Optional[str] = None
    author_username: Optional[str] = None
    created_at: Optional[str] = None
    retweet_count: int = 0
    like_count: int = 0
    reply_count: int = 0
    quote_count: int = 0
    language: Optional[str] = None
    source: Optional[str] = None
    urls: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TwitterUser:
    """Data model for a Twitter user."""
    user_id: Optional[str] = None
    username: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    url: Optional[str] = None
    profile_image: Optional[str] = None
    verified: bool = False
    followers_count: int = 0
    following_count: int = 0
    tweet_count: int = 0
    created_at: Optional[str] = None
    
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class TwitterAnt:
    """
    Twitter/X API wrapper using Tweepy.
    
    This uses the OFFICIAL API - not scraping.
    Requires API credentials from developer.twitter.com
    
    Usage:
        ant = TwitterAnt(bearer_token="YOUR_TOKEN")
        tweets = ant.search_tweets("python programming", max_results=50)
    """
    
    def __init__(self, bearer_token: str = None,
                 consumer_key: str = None,
                 consumer_secret: str = None,
                 access_token: str = None,
                 access_token_secret: str = None):
        """
        Initialize with API credentials.
        
        Args:
            bearer_token: For app-only authentication (read-only)
            consumer_key: API key for OAuth
            consumer_secret: API secret
            access_token: User access token
            access_token_secret: User access secret
        """
        if not TWEEPY_AVAILABLE:
            raise ImportError("tweepy required: pip install tweepy")
        
        # Try environment variables if not provided
        self.bearer_token = bearer_token or os.getenv('TWITTER_BEARER_TOKEN')
        self.consumer_key = consumer_key or os.getenv('TWITTER_API_KEY')
        self.consumer_secret = consumer_secret or os.getenv('TWITTER_API_SECRET')
        self.access_token = access_token or os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = access_token_secret or os.getenv('TWITTER_ACCESS_SECRET')
        
        if not any([self.bearer_token, self.consumer_key]):
            raise ValueError("Twitter API credentials required")
        
        self.client = tweepy.Client(
            bearer_token=self.bearer_token,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            wait_on_rate_limit=True
        )
    
    def search_tweets(self, query: str, max_results: int = 100) -> List[Tweet]:
        """
        Search recent tweets (last 7 days).
        
        Args:
            query: Search query (supports operators)
            max_results: Max tweets to return (10-100 per request)
            
        Returns:
            List of Tweet objects
        """
        results = []
        
        try:
            response = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'public_metrics', 'lang', 'source', 'entities'],
                expansions=['author_id'],
                user_fields=['username']
            )
            
            if not response.data:
                return results
            
            # Map author IDs to usernames
            users = {u.id: u.username for u in (response.includes.get('users', []) or [])}
            
            for tweet_data in response.data:
                tweet = self._parse_tweet(tweet_data, users)
                results.append(tweet)
                
        except tweepy.TweepyException as e:
            print(f"API error: {e}")
        
        return results
    
    def _parse_tweet(self, tweet_data, users: Dict) -> Tweet:
        """Parse tweet from API response."""
        tweet = Tweet()
        
        tweet.tweet_id = str(tweet_data.id)
        tweet.text = tweet_data.text
        tweet.author_id = str(tweet_data.author_id)
        tweet.author_username = users.get(tweet_data.author_id)
        tweet.created_at = tweet_data.created_at.isoformat() if tweet_data.created_at else None
        tweet.language = tweet_data.lang
        tweet.source = tweet_data.source
        
        # Metrics
        metrics = tweet_data.public_metrics or {}
        tweet.retweet_count = metrics.get('retweet_count', 0)
        tweet.like_count = metrics.get('like_count', 0)
        tweet.reply_count = metrics.get('reply_count', 0)
        tweet.quote_count = metrics.get('quote_count', 0)
        
        # Entities
        entities = tweet_data.entities or {}
        
        if 'urls' in entities:
            tweet.urls = [u['expanded_url'] for u in entities['urls'] if 'expanded_url' in u]
        
        if 'hashtags' in entities:
            tweet.hashtags = [h['tag'] for h in entities['hashtags']]
        
        if 'mentions' in entities:
            tweet.mentions = [m['username'] for m in entities['mentions']]
        
        tweet.scraped_at = datetime.now().isoformat()
        
        return tweet
    
    def get_user(self, username: str) -> Optional[TwitterUser]:
        """
        Get user profile by username.
        
        Args:
            username: Twitter username (without @)
            
        Returns:
            TwitterUser or None
        """
        try:
            response = self.client.get_user(
                username=username,
                user_fields=['description', 'location', 'url', 'profile_image_url',
                            'verified', 'public_metrics', 'created_at']
            )
            
            if not response.data:
                return None
            
            return self._parse_user(response.data)
            
        except tweepy.TweepyException as e:
            print(f"API error: {e}")
            return None
    
    def _parse_user(self, user_data) -> TwitterUser:
        """Parse user from API response."""
        user = TwitterUser()
        
        user.user_id = str(user_data.id)
        user.username = user_data.username
        user.name = user_data.name
        user.description = user_data.description
        user.location = user_data.location
        user.url = user_data.url
        user.profile_image = user_data.profile_image_url
        user.verified = user_data.verified or False
        user.created_at = user_data.created_at.isoformat() if user_data.created_at else None
        
        metrics = user_data.public_metrics or {}
        user.followers_count = metrics.get('followers_count', 0)
        user.following_count = metrics.get('following_count', 0)
        user.tweet_count = metrics.get('tweet_count', 0)
        
        user.scraped_at = datetime.now().isoformat()
        
        return user
    
    def get_user_tweets(self, username: str, max_results: int = 100) -> List[Tweet]:
        """
        Get recent tweets from a user.
        
        Args:
            username: Twitter username
            max_results: Maximum tweets
            
        Returns:
            List of Tweet objects
        """
        # First get user ID
        user = self.get_user(username)
        if not user:
            return []
        
        results = []
        
        try:
            response = self.client.get_users_tweets(
                id=user.user_id,
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'public_metrics', 'lang', 'entities']
            )
            
            if response.data:
                users = {user.user_id: username}
                for tweet_data in response.data:
                    tweet = self._parse_tweet(tweet_data, users)
                    results.append(tweet)
                    
        except tweepy.TweepyException as e:
            print(f"API error: {e}")
        
        return results


def search_twitter(query: str, bearer_token: str, max_results: int = 100) -> List[Dict]:
    """Search Twitter for tweets."""
    ant = TwitterAnt(bearer_token=bearer_token)
    results = ant.search_tweets(query, max_results)
    return [r.to_dict() for r in results]


def get_twitter_user(username: str, bearer_token: str) -> Optional[Dict]:
    """Get Twitter user profile."""
    ant = TwitterAnt(bearer_token=bearer_token)
    user = ant.get_user(username)
    return user.to_dict() if user else None


if __name__ == '__main__':
    print("Twitter API requires credentials from developer.twitter.com")
    print("Set TWITTER_BEARER_TOKEN environment variable")
    print()
    print("Example usage:")
    print('  ant = TwitterAnt(bearer_token="YOUR_TOKEN")')
    print('  tweets = ant.search_tweets("python programming")')
