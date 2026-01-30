"""
Test Script for Response Message System
Tests all message types with various scenarios
"""
from schemas.response_messages import (
    no_claims_in_image,
    no_claims_in_article,
    time_sensitive_data,
    opinion_detected,
    insufficient_context,
    ocr_issue,
    network_issue,
    timeout_issue,
    tesseract_missing,
    classify_and_respond
)


def print_separator(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_all_messages():
    """Test all predefined messages"""
    
    print_separator("1. NO CLAIMS IN IMAGE")
    print(no_claims_in_image())
    
    print_separator("2. NO CLAIMS IN ARTICLE")
    print(no_claims_in_article())
    
    print_separator("3. TIME-SENSITIVE DATA")
    print(time_sensitive_data())
    
    print_separator("4. OPINION DETECTED")
    print(opinion_detected())
    
    print_separator("5. INSUFFICIENT CONTEXT")
    print(insufficient_context())
    
    print_separator("6. OCR ISSUE (Technical)")
    print(ocr_issue())
    
    print_separator("7. NETWORK ISSUE (Technical)")
    print(network_issue())
    
    print_separator("8. TIMEOUT ISSUE (Technical)")
    print(timeout_issue())
    
    print_separator("9. TESSERACT MISSING (Technical)")
    print(tesseract_missing())


def test_smart_classifier():
    """Test smart classification with different text samples"""
    
    print_separator("SMART CLASSIFIER TESTS")
    
    # Test cases with expected classifications
    test_cases = [
        ("Tesla stock is at $250 today", "Time-sensitive"),
        ("I think this will be the biggest scam", "Opinion"),
        ("Gold price increased to 3000", "Time-sensitive"),
        ("According to WhatsApp forward, the event happened", "Informal source"),
        ("", "Insufficient context (empty)"),
        ("Hi", "Insufficient context (too short)"),
        ("This poster shows company logo and slogan", "No factual claim"),
        ("The president will win the election", "Opinion"),
        ("Current stock market is bullish", "Time-sensitive"),
        ("People believe this is a hoax", "Opinion"),
    ]
    
    for text, expected in test_cases:
        print(f"\n📝 Input: '{text}'")
        print(f"   Expected: {expected}")
        print("-" * 60)
        response = classify_and_respond(text, "image")
        print(response)
        print()


def analyze_message_quality():
    """Analyze messages for quality issues"""
    
    print_separator("QUALITY ANALYSIS")
    
    # Check for forbidden words
    forbidden_words = ["error", "failed", "invalid", "unverifiable", "rejected", "wrong"]
    all_messages = [
        no_claims_in_image(),
        no_claims_in_article(),
        time_sensitive_data(),
        opinion_detected(),
        insufficient_context(),
        ocr_issue(),
        network_issue(),
        timeout_issue(),
        tesseract_missing()
    ]
    
    print("\n✅ Checking for forbidden words...")
    issues_found = False
    for msg in all_messages:
        msg_lower = msg.lower()
        for word in forbidden_words:
            if word in msg_lower:
                print(f"  ⚠️ Found '{word}' in message")
                issues_found = True
    
    if not issues_found:
        print("  ✅ No forbidden words found!")
    
    print("\n✅ Checking message structure...")
    for i, msg in enumerate(all_messages, 1):
        lines = msg.split('\n')
        first_line = lines[0] if lines else ""
        
        # Check for emoji
        has_emoji = "ℹ️" in first_line or "⚠️" in first_line
        
        # Check for positive acknowledgment in non-technical messages
        has_positive = any(word in msg.lower() for word in 
                          ["successfully", "analyzed", "reviewed", "processed"])
        
        print(f"  Message {i}: Emoji={has_emoji}, Positive={has_positive}")


if __name__ == "__main__":
    print("\n" + "🧪 RESPONSE MESSAGE SYSTEM TEST".center(60, "="))
    
    # Run all tests
    test_all_messages()
    test_smart_classifier()
    analyze_message_quality()
    
    print("\n" + "="*60)
    print("  ✅ ALL TESTS COMPLETE")
    print("="*60 + "\n")
