"""
User-Facing Response Messages
Friendly, clear responses that make users feel informed, not rejected
"""
from typing import Optional
from enum import Enum


class OutcomeCategory(Enum):
    """Classification of verification outcomes"""
    NO_FACTUAL_CLAIM = "no_factual_claim"
    TIME_SENSITIVE = "time_sensitive"
    OPINION_PREDICTIVE = "opinion_predictive"
    INSUFFICIENT_CONTEXT = "insufficient_context"
    SOURCE_DEPENDENT = "source_dependent"
    TECHNICAL_ISSUE = "technical_issue"


def format_friendly_response(
    category: OutcomeCategory,
    source_type: str = "content"
) -> str:
    """
    Generate friendly response for different verification outcomes
    
    Args:
        category: The outcome category
        source_type: 'image', 'article', 'content'
        
    Returns:
        User-friendly response message
    """
    
    templates = {
        OutcomeCategory.NO_FACTUAL_CLAIM: f"""ℹ️  The {source_type} was analyzed successfully.

We couldn't find a clear factual statement that can be independently verified.

The content appears to be informational or structured data, which is currently outside the scope of factual claim verification.""",
        
        OutcomeCategory.TIME_SENSITIVE: f"""ℹ️  The {source_type} was reviewed successfully.

It appears to contain time-sensitive information that changes frequently.

Verifying this type of data requires real-time authoritative sources, which are not currently used.""",
        
        OutcomeCategory.OPINION_PREDICTIVE: """ℹ️  The content was processed successfully.

The statement appears to express an opinion or future prediction rather than a factual claim that can be verified.""",
        
        OutcomeCategory.INSUFFICIENT_CONTEXT: """ℹ️  The content was reviewed, but there wasn't enough clear context to reliably verify the information.

Providing additional context or a clearer statement may help.""",
        
        OutcomeCategory.SOURCE_DEPENDENT: """ℹ️  The content was reviewed successfully.

The claim appears to depend on an informal or unspecified source, making independent verification unreliable.""",
        
        OutcomeCategory.TECHNICAL_ISSUE: """⚠️  We tried to analyze the content, but encountered a technical issue.

Please try again with a clearer input or later."""
    }
    
    return templates.get(category, templates[OutcomeCategory.TECHNICAL_ISSUE])


# Common scenarios (simplified)
def no_claims_in_image() -> str:
    """Image has no extractable factual claims"""
    return format_friendly_response(OutcomeCategory.NO_FACTUAL_CLAIM, "image")


def no_claims_in_article() -> str:
    """Article has no extractable factual claims"""
    return format_friendly_response(OutcomeCategory.NO_FACTUAL_CLAIM, "article")


def no_claims_in_text() -> str:
    """Text has no extractable factual claims"""
    return format_friendly_response(OutcomeCategory.NO_FACTUAL_CLAIM, "text")


def time_sensitive_data() -> str:
    """Content contains time-sensitive data"""
    return format_friendly_response(OutcomeCategory.TIME_SENSITIVE, "content")


def opinion_detected() -> str:
    """Statement is opinion or prediction"""
    return format_friendly_response(OutcomeCategory.OPINION_PREDICTIVE)


def insufficient_context() -> str:
    """Not enough context to verify"""
    return format_friendly_response(OutcomeCategory.INSUFFICIENT_CONTEXT)


def informal_source() -> str:
    """Source is informal or unspecified"""
    return format_friendly_response(OutcomeCategory.SOURCE_DEPENDENT)


# Technical issues (real problems only)
def ocr_issue() -> str:
    """OCR couldn't read image"""
    return """⚠️  We tried to extract text from the image, but encountered a technical issue.

Please ensure the image is clear, well-lit, and contains readable text."""


def network_issue() -> str:
    """Network connection problem"""
    return """⚠️  We couldn't fetch content from the URL.

Please check the URL and your internet connection, then try again."""


def timeout_issue() -> str:
    """Request timed out"""
    return """⚠️  The request took too long to complete.

The source may be slow or unavailable. Please try again later."""


def tesseract_missing() -> str:
    """OCR engine not installed"""
    return """⚠️  Text extraction from images requires Tesseract OCR.

Please use text or URL input instead, or install Tesseract to enable image support."""


# Smart classifier for unverifiable content
def classify_and_respond(text: str, source_type: str = "content") -> str:
    """
    Intelligently classify why content couldn't be verified
    
    Args:
        text: The extracted text
        source_type: 'image', 'article', or 'content'
        
    Returns:
        Appropriate friendly response
    """
    if not text or len(text.strip()) < 10:
        return insufficient_context()
    
    text_lower = text.lower()
    
    # Check for opinions/predictions (more keywords)
    opinion_words = ['will', 'should', 'think', 'believe', 'predict', 'must', 
                     'opinion', 'suggests', 'may', 'could', 'expect']
    if any(f' {word} ' in f' {text_lower} ' or text_lower.startswith(word) for word in opinion_words):
        return opinion_detected()
    
    # Check for time-sensitive data (expanded)
    time_words = ['price', 'stock', 'rate', 'today', 'current', 'now', 
                  'latest', 'trading', 'market', 'live', 'real-time']
    if any(word in text_lower for word in time_words):
        return time_sensitive_data()
    
    # Check for informal sources
    source_words = ['whatsapp', 'forward', 'rumor', 'allegedly', 'claims', 
                   'viral', 'unconfirmed', 'social media']
    if any(word in text_lower for word in source_words):
        return informal_source()
    
    # Default: no factual claim
    return format_friendly_response(OutcomeCategory.NO_FACTUAL_CLAIM, source_type)


# ========================================
# URL ACCESS ISSUE RESPONSES
# ========================================

def social_media_link_issue() -> str:
    """Social media link (Instagram, Facebook, X, etc.) cannot be accessed"""
    return """⚠️  We couldn't retrieve the content from the social media link.

Some platforms require login or API access to fetch post text, which limits automated analysis.

Please paste the post's caption, description, or relevant text manually so we can analyze it."""


def login_required_link() -> str:
    """Link requires login or private access"""
    return """⚠️  We couldn't access the content from the provided link.

The page appears to require login or special access, which prevents content retrieval.

If possible, please share the visible text or use a publicly accessible source."""


def paywall_link() -> str:
    """Link is behind a paywall or restricted access"""
    return """⚠️  We couldn't retrieve the full content from the link.

The source appears to be restricted or paywalled, limiting access to the article text.

You may paste the relevant excerpt or use an alternative public source for analysis."""


def broken_or_expired_link() -> str:
    """Link is broken, deleted, or expired"""
    return """⚠️  We couldn't retrieve content from the provided link.

The link may be broken, expired, or no longer available.

Please check the link or share the content text directly."""


def messaging_app_forward() -> str:
    """WhatsApp, Telegram, or other messaging app forward"""
    return """ℹ️  The link appears to reference forwarded or informal content.

Such sources often lack verifiable context or public access.

Please paste the message text or provide a reliable external source for verification."""


def classify_url_issue(url: str, status_code: int = None, error_type: str = None) -> str:
    """
    Classify URL access issues and return appropriate message
    
    Args:
        url: The URL that couldn't be accessed
        status_code: HTTP status code if available
        error_type: Type of error encountered
        
    Returns:
        Appropriate user-friendly message
    """
    url_lower = url.lower()
    
    # Check for social media platforms
    social_platforms = ['instagram.com', 'facebook.com', 'fb.com', 'twitter.com', 
                       'x.com', 'threads.net', 'tiktok.com', 'linkedin.com']
    if any(platform in url_lower for platform in social_platforms):
        return social_media_link_issue()
    
    # Check for messaging apps
    messaging_apps = ['wa.me', 'whatsapp', 't.me', 'telegram', 'chat.whatsapp']
    if any(app in url_lower for app in messaging_apps):
        return messaging_app_forward()
    
    # Check status codes
    if status_code:
        if status_code == 401 or status_code == 403:
            return login_required_link()
        elif status_code == 404 or status_code == 410:
            return broken_or_expired_link()
        elif status_code == 402 or status_code == 451:
            return paywall_link()
    
    # Check for paywalled news sites
    paywall_domains = ['nytimes.com', 'wsj.com', 'ft.com', 'economist.com', 
                      'bloomberg.com', 'telegraph.co.uk']
    if any(domain in url_lower for domain in paywall_domains):
        return paywall_link()
    
    # Check error type
    if error_type:
        if 'timeout' in error_type.lower():
            return timeout_issue()
        elif 'connection' in error_type.lower():
            return network_issue()
    
    # Default: generic broken link
    return broken_or_expired_link()
