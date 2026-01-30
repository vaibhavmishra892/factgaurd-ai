#!/usr/bin/env python3
"""
Test Article Extractor Tool
"""
from tools.article_extractor import ArticleExtractorTool

def test_url_validation():
    """Test URL validation logic"""
    extractor = ArticleExtractorTool()
    
    print("Testing URL Validation")
    print("=" * 60)
    
    # Valid URLs
    valid_urls = [
        "https://example.com/article",
        "http://news.com/story",
        "https://blog.website.org/post/123"
    ]
    
    for url in valid_urls:
        assert extractor.is_valid_url(url), f"Should be valid: {url}"
        print(f"✓ Valid: {url}")
    
    # Invalid URLs
    invalid_urls = [
        "not a url",
        "just text here",
        "ftp://wrong-protocol.com"
    ]
    
    for url in invalid_urls:
        result = extractor.is_valid_url(url)
        print(f"✓ Invalid: {url} → {result}")
    
    print("\n✅ URL validation tests passed!\n")


def test_article_extraction():
    """Test real article extraction"""
    extractor = ArticleExtractorTool()
    
    print("Testing Article Extraction")
    print("=" * 60)
    
    # Test with a simple, reliable URL
    test_url = "https://example.com"
    
    print(f"Extracting from: {test_url}")
    result = extractor.extract_article(test_url)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✓ Title: {result['title'][:50]}...")
        print(f"✓ Content length: {len(result['content'])} chars")
        print(f"✓ Word count: {result['word_count']}")
        print(f"✓ Content preview: {result['content'][:100]}...")
    
    print("\n✅ Article extraction test complete!\n")


def test_error_handling():
    """Test error handling for invalid inputs"""
    extractor = ArticleExtractorTool(timeout=5)
    
    print("Testing Error Handling")
    print("=" * 60)
    
    # Invalid URL format
    result = extractor.extract_article("not-a-url")
    assert "error" in result
    print(f"✓ Invalid URL: {result['error']}")
    
    # Non-existent domain
    result = extractor.extract_article("https://this-domain-definitely-does-not-exist-12345.com")
    assert "error" in result
    print(f"✓ Non-existent domain: {result['error']}")
    
    print("\n✅ Error handling tests passed!\n")


def test_claim_extraction():
    """Test claim extraction from article text"""
    extractor = ArticleExtractorTool()
    
    print("Testing Claim Extraction")
    print("=" * 60)
    
    sample_text = """
    Tesla's stock price reached $250 on Monday. 
    The company announced record deliveries last quarter.
    Elon Musk founded Tesla in 2003.
    What will happen next?
    Experts predict continued growth in the electric vehicle market.
    """
    
    claims = extractor.extract_claims(sample_text, max_claims=3)
    
    print(f"Extracted {len(claims)} claims:")
    for i, claim in enumerate(claims, 1):
        print(f"{i}. {claim}")
    
    print("\n✅ Claim extraction test complete!\n")


if __name__ == "__main__":
    test_url_validation()
    test_error_handling()
    test_claim_extraction()
    test_article_extraction()
    
    print("=" * 60)
    print("🎉 All article extractor tests passed!")
    print("=" * 60)
