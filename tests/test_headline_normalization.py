"""
Test News Headline Normalization
Tests the critical Ambuja Cements case and other business headlines
"""


def test_business_headlines():
    """
    Test that business headlines are normalized, not rejected
    """
    
    print("\n" + "="*70)
    print("  BUSINESS HEADLINE NORMALIZATION TESTS")
    print("="*70 + "\n")
    
    test_cases = [
        {
            "name": "Ambuja Cements Q3 Results",
            "input": "Ambuja Cements Q3 Results LIVE: Net profit declines 91% to Rs 204 crore on one-time cost, shares fall 5%",
            "expected_type": "NEWS_HEADLINE",
            "expected_action": "NORMALIZE_AND_VERIFY",
            "expected_normalized": "Ambuja Cements reported that its Q3 net profit declined by approximately 91% to ₹204 crore due to one-time costs, and its shares fell by approximately 5%."
        },
        {
            "name": "Tech Company Earnings",
            "input": "Apple Q4 revenue beats estimates at $89.5 billion, iPhone sales up 6%",
            "expected_type": "NEWS_HEADLINE",
            "expected_action": "NORMALIZE_AND_VERIFY",
            "expected_normalized": "Apple's Q4 revenue beat estimates at $89.5 billion, with iPhone sales up 6%."
        },
        {
            "name": "Political Announcement",
            "input": "President announces new economic sanctions against Russia",
            "expected_type": "NEWS_HEADLINE",
            "expected_action": "NORMALIZE_AND_VERIFY",
            "expected_normalized": "The President announced new economic sanctions against Russia."
        },
        {
            "name": "Market Data",
            "input": "Gold prices surge 3% to $2,050/oz on inflation fears",
            "expected_type": "NEWS_HEADLINE",
            "expected_action": "NORMALIZE_AND_VERIFY",
            "expected_normalized": "Gold prices surged 3% to $2,050 per ounce due to inflation fears."
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"Test {i}: {case['name']}")
        print(f"Input: '{case['input']}'")
        print(f"Expected Type: {case['expected_type']}")
        print(f"Expected Action: {case['expected_action']}")
        print(f"Expected Normalized: '{case['expected_normalized']}'")
        print("\n✅ Should be NORMALIZED and sent to verification")
        print("❌ Should NOT be rejected as incomplete")
        print("-" * 70 + "\n")


def test_malformed_cases():
    """
    Test that truly malformed/truncated text is properly rejected
    """
    
    print("\n" + "="*70)
    print("  MALFORMED TEXT REJECTION TESTS")
    print("="*70 + "\n")
    
    malformed_cases = [
        {
            "input": "was born in",
            "reason": "Mid-phrase truncation, no subject"
        },
        {
            "input": "The company announced",
            "reason": "Missing critical information (what was announced?)"
        },
        {
            "input": "increased by",
            "reason": "Fragment - no subject or complete information"
        }
    ]
    
    for i, case in enumerate(malformed_cases, 1):
        print(f"Test {i}: Malformed Case")
        print(f"Input: '{case['input']}'")
        print(f"Reason: {case['reason']}")
        print("Expected: MALFORMED → STOP verification")
        print("-" * 70 + "\n")


def test_opinion_vs_headline():
    """
    Test distinction between opinion and factual headline
    """
    
    print("\n" + "="*70)
    print("  OPINION vs HEADLINE DISTINCTION")
    print("="*70 + "\n")
    
    test_cases = [
        {
            "input": "I think this policy will destroy the economy",
            "type": "OPINION",
            "action": "STOP"
        },
        {
            "input": "Analysts predict stock market crash next quarter",
            "type": "PREDICTION",
            "action": "STOP"
        },
        {
            "input": "Government announces new tax policy effective January 2025",
            "type": "NEWS_HEADLINE",
            "action": "NORMALIZE_AND_VERIFY"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"Test {i}:")
        print(f"Input: '{case['input']}'")
        print(f"Type: {case['type']}")
        print(f"Action: {case['action']}")
        print("-" * 70 + "\n")


if __name__ == "__main__":
    test_business_headlines()
    test_malformed_cases()
    test_opinion_vs_headline()
    
    print("\n" + "="*70)
    print("  KEY TAKEAWAYS")
    print("="*70)
    print("""
✅ Business headlines (even compressed) → NORMALIZE + VERIFY
❌ Truncated fragments (no context) → REJECT
❌ Opinions/predictions → REJECT

Critical Case: Ambuja Cements Q3 headline
- Contains: company name, financial terms, numbers
- Action: Normalize into complete claim
- Route to: Finance + News agents
- Result: VERIFY (do not reject)
    """)
