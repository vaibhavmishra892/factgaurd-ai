import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from config import config

class NewsAPITool:
    """Tool for fetching news articles from NewsAPI"""
    
    def __init__(self):
        self.api_key = config.NEWS_API_KEY
        self.base_url = config.NEWS_API_BASE_URL
    
    def search_news(
        self, 
        query: str, 
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        language: str = "en",
        sort_by: str = "relevancy",
        page_size: int = 5
    ) -> List[Dict]:
        """
        Search for news articles matching a query
        
        Args:
            query: Search query
            from_date: Start date (YYYY-MM-DD format)
            to_date: End date (YYYY-MM-DD format)
            language: Article language code
            sort_by: Sort order ('relevancy', 'popularity', 'publishedAt')
            page_size: Number of results to return (max 100)
        
        Returns:
            List of article dictionaries
        """
        if not self.api_key:
            return [{"error": "NewsAPI key not configured"}]
        
        # Default to last 7 days if no date specified
        if not from_date:
            from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
        
        params = {
            "q": query,
            "from": from_date,
            "to": to_date,
            "language": language,
            "sortBy": sort_by,
            "pageSize": page_size,
            "apiKey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok" and "articles" in data:
                articles = []
                for article in data["articles"]:
                    articles.append({
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "source": article.get("source", {}).get("name", "Unknown"),
                        "author": article.get("author", "Unknown"),
                        "url": article.get("url", ""),
                        "published_at": article.get("publishedAt", ""),
                        "content": article.get("content", "")[:300],  # Truncate long content
                    })
                return articles if articles else [{"error": "No articles found for query"}]
            else:
                error_msg = data.get("message", "Unknown error")
                return [{"error": f"NewsAPI error: {error_msg}"}]
        
        except Exception as e:
            return [{"error": f"NewsAPI request failed: {str(e)}"}]
    
    def verify_claim_with_news(self, claim: str) -> Dict:
        """
        Verify a claim by searching for relevant news articles
        
        Args:
            claim: Factual claim to verify
        
        Returns:
            Dictionary with verification evidence from news sources
        """
        # Search for articles
        articles = self.search_news(claim, page_size=3)
        
        if not articles or (len(articles) == 1 and "error" in articles[0]):
            return {
                "found_evidence": False,
                "articles": [],
                "summary": "No news articles found to verify this claim"
            }
        
        # Filter out error responses
        valid_articles = [a for a in articles if "error" not in a]
        
        return {
            "found_evidence": len(valid_articles) > 0,
            "articles": valid_articles,
            "summary": f"Found {len(valid_articles)} relevant news article(s)",
            "source_types": list(set([a.get("source", "Unknown") for a in valid_articles]))
        }
    
    def get_recent_headlines(self, topic: str, page_size: int = 5) -> List[Dict]:
        """
        Get recent headlines about a specific topic
        
        Args:
            topic: Topic to search for
            page_size: Number of headlines to return
        
        Returns:
            List of recent headlines
        """
        return self.search_news(
            query=topic,
            sort_by="publishedAt",
            page_size=page_size
        )
