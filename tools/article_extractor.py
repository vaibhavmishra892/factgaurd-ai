"""
Article Extractor Tool
Fetches and extracts clean text content from article URLs
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import re
from urllib.parse import urlparse
from schemas.response_messages import (
    network_issue, 
    timeout_issue,
    classify_url_issue
)


class ArticleExtractorTool:
    """Tool for extracting readable text from article URLs"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def is_valid_url(self, url: str) -> bool:
        """Validate if string is a proper URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def extract_article(self, url: str) -> Dict[str, str]:
        """
        Extract article content from URL
        
        Args:
            url: Article URL to extract
            
        Returns:
            Dictionary with extracted text and metadata
        """
        # Validate URL
        if not self.is_valid_url(url):
            return {"error": f"Invalid URL format: {url}"}
        
        try:
            # Fetch HTML
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'aside', 
                                'header', 'iframe', 'noscript', 'form']):
                element.decompose()
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No title"
            
            # Extract main content - try common article containers
            article_text = ""
            
            # Try semantic HTML5 tags first
            article = soup.find('article')
            if article:
                article_text = article.get_text(separator=' ', strip=True)
            else:
                # Try common content class names
                content_selectors = [
                    'main', '[role="main"]', '.article-content', '.post-content',
                    '.entry-content', '.content', '#content', '.article-body'
                ]
                
                for selector in content_selectors:
                    content = soup.select_one(selector)
                    if content:
                        article_text = content.get_text(separator=' ', strip=True)
                        break
                
                # Fallback: get all paragraphs
                if not article_text:
                    paragraphs = soup.find_all('p')
                    article_text = ' '.join([p.get_text(strip=True) for p in paragraphs])
            
            # Clean extracted text
            article_text = self._clean_text(article_text)
            
            # Check if we got meaningful content
            if len(article_text) < 100:
                # Use smart classification - likely a social media link or restricted content
                return {"error": classify_url_issue(url)}
            
            return {
                "url": url,
                "title": title_text,
                "content": article_text,
                "word_count": len(article_text.split()),
                "source": "Article Extractor"
            }
            
        except requests.exceptions.Timeout:
            return {"error": timeout_issue()}
        except requests.exceptions.ConnectionError:
            return {"error": network_issue()}
        except requests.exceptions.HTTPError as e:
            # Use smart classification for HTTP errors
            status_code = e.response.status_code if e.response else None
            return {"error": classify_url_issue(url, status_code=status_code)}
        except Exception as e:
            # Generic error - try to classify based on URL
            return {"error": classify_url_issue(url, error_type=str(e))}
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common noise patterns
        text = re.sub(r'Share\s+this\s+article', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Subscribe\s+to\s+our\s+newsletter', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Cookie\s+policy', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Privacy\s+policy', '', text, flags=re.IGNORECASE)
        
        return text.strip()

