"""
Image Intent Classifier & Claim Reconstructor
Determines if OCR text from images should be fact-checked and reconstructs claims
"""
import re
from typing import Tuple, List, Optional
from enum import Enum


class ImageIntent(Enum):
    """Classification of image content intent"""
    NEWS_OR_VIRAL_CLAIM = "news_or_viral_claim"
    OPINION_OR_COMMENTARY = "opinion_or_commentary"
    TIME_SENSITIVE_DATA = "time_sensitive_data"
    ADVERTISEMENT_OR_OTHER = "advertisement_or_other"
    UNREADABLE_OR_INSUFFICIENT_TEXT = "unreadable_or_insufficient_text"


def classify_image_intent(ocr_text: str) -> ImageIntent:
    """
    Classify the intent of OCR text from an image
    
    Args:
        ocr_text: Text extracted from image via OCR
        
    Returns:
        ImageIntent classification
    """
    if not ocr_text or len(ocr_text.strip()) < 10:
        return ImageIntent.UNREADABLE_OR_INSUFFICIENT_TEXT
    
    text_lower = ocr_text.lower()
    
    # Check for news/viral claim indicators (HIGHEST PRIORITY)
    news_keywords = [
        # Events & Actions
        'attacked', 'arrested', 'captured', 'killed', 'injured', 'shot',
        'announced', 'confirmed', 'reported', 'breaking', 'news',
        'filed case', 'charged', 'convicted', 'sentenced',
        
        # Entities that make it newsworthy
        'president', 'minister', 'government', 'military', 'army',
        'police', 'court', 'department', 'official',
        
        # Event language
        'yesterday', 'today', 'breaking', 'just in', 'alert',
        'incident', 'case', 'investigation'
    ]
    
    # Check for proper nouns (countries, people, organizations)
    has_proper_nouns = bool(re.search(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', ocr_text))
    
    # Check for news indicators
    news_score = sum(1 for keyword in news_keywords if keyword in text_lower)
    
    # If has news keywords + proper nouns → NEWS
    if news_score >= 2 and has_proper_nouns:
        return ImageIntent.NEWS_OR_VIRAL_CLAIM
    
    # Single strong news keyword + proper noun
    strong_news = ['attacked', 'arrested', 'captured', 'killed', 'breaking news']
    if any(kw in text_lower for kw in strong_news) and has_proper_nouns:
        return ImageIntent.NEWS_OR_VIRAL_CLAIM
    
    # Check for time-sensitive data (prices, stocks, rates)
    price_indicators = ['price', 'stock', 'rate', '₹', '$', '€', 'gold', 'silver',
                       'market', 'trading', 'high:', 'low:', 'open:', 'close:']
    if sum(1 for ind in price_indicators if ind in text_lower) >= 2:
        return ImageIntent.TIME_SENSITIVE_DATA
    
    # Check for pure opinion/commentary
    opinion_indicators = [
        # Pure opinions without factual assertions
        'i think', 'i believe', 'in my opinion', 'i feel',
        'this is evil', 'this is good', 'this is bad',
        'will destroy', 'will save', 'should', 'must'
    ]
    
    # But distinguish from news: "Minister said X should happen" is NEWS, not opinion
    is_pure_opinion = any(ind in text_lower for ind in opinion_indicators)
    is_quoting_or_news = any(kw in text_lower for kw in ['said', 'stated', 'announced', 'reported'])
    
    if is_pure_opinion and not is_quoting_or_news and not has_proper_nouns:
        return ImageIntent.OPINION_OR_COMMENTARY
    
    # Check for advertisements
    ad_indicators = ['buy now', 'sale', 'offer', 'discount', 'limited time',
                    'call now', 'visit', 'www.', '.com', 'download app']
    if sum(1 for ind in ad_indicators if ind in text_lower) >= 2:
        return ImageIntent.ADVERTISEMENT_OR_OTHER
    
    # Default: If has proper nouns and some meaningful content, treat as potential news
    # This is CONSERVATIVE - we prefer to verify rather than reject
    if has_proper_nouns and len(ocr_text.strip()) > 30:
        return ImageIntent.NEWS_OR_VIRAL_CLAIM
    
    # Otherwise, likely other content
    return ImageIntent.ADVERTISEMENT_OR_OTHER


def reconstruct_claims_from_image(ocr_text: str) -> List[str]:
    """
    Reconstruct complete factual claims from fragmented OCR text
    
    This is MORE LENIENT than normal claim extraction because:
    - Images often have fragmented text
    - News screenshots may have incomplete sentences
    - We want to give users benefit of doubt for verification
    
    Args:
        ocr_text: Raw OCR text from image
        
    Returns:
        List of reconstructed complete claims
    """
    if not ocr_text or len(ocr_text.strip()) < 15:
        return []
    
    # Split into lines/sentences
    lines = [l.strip() for l in ocr_text.split('\n') if l.strip()]
    if not lines:
        return []
    
    # Try to identify main claim components
    # Look for fragments that can be merged
    
    # Simple heuristic: Combine lines that likely belong together
    reconstructed = []
    current_claim = []
    
    for line in lines:
        # Skip very short fragments (< 10 chars) unless they're part of a name
        if len(line) < 10 and not re.match(r'^[A-Z][a-z]+', line):
            continue
        
        # Check if line starts with lowercase or conjunction (fragment continuation)
        if current_claim and (line[0].islower() or line.startswith(('and ', 'or ', 'but '))):
            current_claim.append(line)
        else:
            # Start new claim
            if current_claim:
                merged = ' '.join(current_claim)
                if len(merged) >= 30:  # Only keep substantial claims
                    reconstructed.append(merged)
            current_claim = [line]
    
    # Don't forget last claim
    if current_claim:
        merged = ' '.join(current_claim)
        if len(merged) >= 30:
            reconstructed.append(merged)
    
    # If reconstruction produced nothing, try to use longest line
    if not reconstructed and lines:
        longest = max(lines, key=len)
        if len(longest) >= 30:
            reconstructed = [longest]
    
    return reconstructed


def should_verify_image_content(ocr_text: str) -> Tuple[bool, str, Optional[List[str]]]:
    """
    Determine if image content should be verified and reconstruct claims if needed
    
    Args:
        ocr_text: Text extracted from image
        
    Returns:
        (should_verify, reason, reconstructed_claims)
        - should_verify: True if content should be fact-checked
        - reason: Human-readable explanation
        - reconstructed_claims: List of claims if verifiable, None otherwise
    """
    # Classify intent
    intent = classify_image_intent(ocr_text)
    
    if intent == ImageIntent.NEWS_OR_VIRAL_CLAIM:
        # Reconstruct claims from potentially fragmented text
        claims = reconstruct_claims_from_image(ocr_text)
        
        if claims:
            return (
                True,
                "Image appears to contain news or viral factual claims",
                claims
            )
        else:
            return (
                False,
                "Image appears news-related but text is too fragmented to reconstruct claims",
                None
            )
    
    elif intent == ImageIntent.OPINION_OR_COMMENTARY:
        return (
            False,
            "Image appears to contain opinion or commentary rather than factual claims",
            None
        )
    
    elif intent == ImageIntent.TIME_SENSITIVE_DATA:
        return (
            False,
            "Image appears to contain time-sensitive data (prices, rates) which requires real-time verification",
            None
        )
    
    elif intent == ImageIntent.ADVERTISEMENT_OR_OTHER:
        return (
            False,
            "Image appears to be promotional or outside verification scope",
            None
        )
    
    else:  # UNREADABLE_OR_INSUFFICIENT_TEXT
        return (
            False,
            "Image has insufficient readable text for verification",
            None
        )


def format_image_verdict_response(should_verify: bool, reason: str, ocr_text: str = "") -> str:
    """
    Generate user-friendly response for image analysis
    
    Args:
        should_verify: Whether content should be verified
        reason: Classification reason
        ocr_text: Original OCR text (optional, for context)
        
    Returns:
        Formatted response message
    """
    if not should_verify:
        # Determine the specific message based on reason
        if "opinion" in reason.lower():
            return """ℹ️  The image was analyzed successfully.

The content appears to express an opinion or commentary rather than a factual claim that can be verified.

If you believe there are specific factual assertions in the image, please share them as text."""
        
        elif "time-sensitive" in reason.lower():
            return """ℹ️  The image was reviewed successfully.

It appears to contain time-sensitive information (like prices or rates) that changes frequently.

Verifying this type of data requires real-time authoritative sources, which are not currently used."""
        
        elif "promotional" in reason.lower() or "advertisement" in reason.lower():
            return """ℹ️  The image was analyzed successfully.

The content appears to be promotional or informational, which is outside the scope of fact verification."""
        
        elif "insufficient" in reason.lower() or "fragmented" in reason.lower():
            return """ℹ️  The image was analyzed, but the extracted text is too fragmentary or unclear.

Please ensure the image is clear, well-lit, and contains readable text, or share the key claims as text."""
        
        else:
            return f"""ℹ️  The image was analyzed successfully.

{reason}

Please provide complete factual claims as text if you'd like verification."""
    
    return ""  # If should_verify is True, let normal verification proceed
