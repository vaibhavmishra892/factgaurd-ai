"""
Test URL Classification and Response Messages
"""
from schemas.response_messages import (
    social_media_link_issue,
    login_required_link,
    paywall_link,
    broken_or_expired_link,
    messaging_app_forward,
    classify_url_issue
)


def test_url_classification():
    """Test URL classification with various problematic URLs"""
    
    test_cases = [
        # (URL, expected_type, description)
        ("https://www.instagram.com/p/ABC123", "Social Media", "Instagram post"),
        ("https://twitter.com/user/status/123", "Social Media", "Twitter/X post"),
        ("https://www.facebook.com/post/456", "Social Media", "Facebook post"),
        ("https://wa.me/1234567890", "Messaging App", "WhatsApp link"),
        ("https://t.me/channel/post", "Messaging App", "Telegram link"),
        ("https://www.nytimes.com/article", "Paywall", "NYT article"),
        ("https://www.wsj.com/news", "Paywall", "WSJ article"),
        ("https://example.com/gone", "Generic", "Generic broken link"),
    ]
    
    print("\n=== URL CLASSIFICATION TESTS ===\n")
    
    for url, expected, description in test_cases:
        print(f"Test: {description}")
        print(f"URL: {url}")
        print(f"Expected: {expected}")
        print("-" * 60)
        response = classify_url_issue(url)
        print(response)
        print("\n")


def test_status_codes():
    """Test classification with different HTTP status codes"""
    
    print("\n=== HTTP STATUS CODE TESTS ===\n")
    
    test_codes = [
        (401, "Unauthorized (login required)"),
        (403, "Forbidden (access denied)"),
        (404, "Not Found (broken link)"),
        (410, "Gone (expired link)"),
        (402, "Payment Required (paywall)"),
    ]
    
    for code, description in test_codes:
        print(f"Test: HTTP {code} - {description}")
        print("-" * 60)
        response = classify_url_issue("https://example.com/article", status_code=code)
        print(response)
        print("\n")


def test_all_messages():
    """Test all individual message functions"""
    
    print("\n=== ALL URL MESSAGE TYPES ===\n")
    
    messages = [
        ("Social Media", social_media_link_issue()),
        ("Login Required", login_required_link()),
        ("Paywall", paywall_link()),
        ("Broken/Expired", broken_or_expired_link()),
        ("Messaging App", messaging_app_forward()),
    ]
    
    for name, msg in messages:
        print(f"=== {name} ===")
        print(msg)
        print("\n")


def check_message_quality():
    """Check that messages follow guidelines"""
    
    print("\n=== QUALITY CHECKS ===\n")
    
    all_messages = [
        social_media_link_issue(),
        login_required_link(),
        paywall_link(),
        broken_or_expired_link(),
        messaging_app_forward(),
    ]
    
    # Check for forbidden words in URL messages
    forbidden = ["error", "failed", "invalid", "blocked"]
    
    print("Checking for forbidden words...")
    found_issues = False
    for i, msg in enumerate(all_messages, 1):
        msg_lower = msg.lower()
        for word in forbidden:
            if word in msg_lower:
                print(f"  Message {i}: Found '{word}'")
                found_issues = True
    
    if not found_issues:
        print("  PASS: No forbidden words found!")
    
    # Check for helpful alternatives
    print("\nChecking for helpful suggestions...")
    helpful_words = ["please", "paste", "share", "use", "try"]
    for i, msg in enumerate(all_messages, 1):
        has_suggestion = any(word in msg.lower() for word in helpful_words)
        print(f"  Message {i}: {'PASS' if has_suggestion else 'FAIL'} - Has helpful suggestion")
    
    print("\nALL QUALITY CHECKS COMPLETE\n")


if __name__ == "__main__":
    test_all_messages()
    test_url_classification()
    test_status_codes()
    check_message_quality()
