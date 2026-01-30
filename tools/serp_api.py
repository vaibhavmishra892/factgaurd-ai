import requests
from typing import List, Dict, Optional
from config import config

class SerpAPITool:
    """Tool for Google search results via SerpAPI"""
    
    def __init__(self):
        self.api_key = config.SERP_API_KEY
        self.base_url = config.SERP_API_BASE_URL
    
    def google_search(
        self, 
        query: str, 
        num_results: int = 5,
        time_period: Optional[str] = None
    ) -> List[Dict]:
        """
        Perform Google search and return results
        
        Args:
            query: Search query
            num_results: Number of results to return
            time_period: Time filter ('d' for day, 'w' for week, 'm' for month, 'y' for year)
        
        Returns:
            List of search result dictionaries
        """
        if not self.api_key:
            return [{"error": "SerpAPI key not configured"}]
        
        params = {
            "q": query,
            "api_key": self.api_key,
            "num": num_results,
            "engine": "google"
        }
        
        if time_period:
            params["tbs"] = f"qdr:{time_period}"
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "organic_results" in data:
                results = []
                for result in data["organic_results"][:num_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "source": result.get("source", "Unknown"),
                        "position": result.get("position", 0)
                    })
                return results if results else [{"error": "No search results found"}]
            else:
                error_msg = data.get("error", "Unknown error")
                return [{"error": f"SerpAPI error: {error_msg}"}]
        
        except Exception as e:
            return [{"error": f"SerpAPI request failed: {str(e)}"}]
    
    def search_news(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search Google News specifically
        
        Args:
            query: Search query
            num_results: Number of results to return
        
        Returns:
            List of news search results
        """
        if not self.api_key:
            return [{"error": "SerpAPI key not configured"}]
        
        params = {
            "q": query,
            "api_key": self.api_key,
            "num": num_results,
            "engine": "google",
            "tbm": "nws"  # News search
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "news_results" in data:
                results = []
                for result in data["news_results"][:num_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "source": result.get("source", "Unknown"),
                        "date": result.get("date", "Unknown"),
                        "thumbnail": result.get("thumbnail", "")
                    })
                return results if results else [{"error": "No news results found"}]
            else:
                # Fallback to organic results if news_results not available
                return self.google_search(query, num_results)
        
        except Exception as e:
            return [{"error": f"SerpAPI news search failed: {str(e)}"}]
    
    def verify_claim_with_search(self, claim: str) -> Dict:
        """
        Verify a claim using Google search results
        
        Args:
            claim: Factual claim to verify
        
        Returns:
            Dictionary with verification evidence from search
        """
        # Perform search
        results = self.google_search(claim, num_results=5)
        
        if not results or (len(results) == 1 and "error" in results[0]):
            return {
                "found_evidence": False,
                "results": [],
                "summary": "No search results found to verify this claim"
            }
        
        # Filter out error responses
        valid_results = [r for r in results if "error" not in r]
        
        # Identify trusted sources
        trusted_sources = [
            "reuters.com", "bbc.com", "apnews.com", "bloomberg.com",
            "nytimes.com", "wsj.com", "ft.com", "economist.com",
            "wikipedia.org", "gov", "edu"
        ]
        
        trusted_count = 0
        for result in valid_results:
            link = result.get("link", "").lower()
            if any(source in link for source in trusted_sources):
                trusted_count += 1
                result["trusted"] = True
            else:
                result["trusted"] = False
        
        return {
            "found_evidence": len(valid_results) > 0,
            "results": valid_results,
            "trusted_source_count": trusted_count,
            "summary": f"Found {len(valid_results)} search results ({trusted_count} from trusted sources)"
        }
