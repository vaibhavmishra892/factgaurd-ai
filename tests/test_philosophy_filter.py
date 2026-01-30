"""
Test Strengthened Opinion and Philosophy Filters
"""
from tools.claim_utils import extract_factual_claims


def test_philosophy_filter():
    """Test that philosophical questions are filtered out"""
    
    print("\n=== PHILOSOPHY FILTER TEST ===\n")
    
    philosophical_texts = [
        "What is the meaning of life and human existence?",
        "The nature of consciousness remains a deep philosophical question that science cannot answer",
        "Ethics and morality guide our understanding of justice in society",
        "Human nature is fundamentally about the search for truth and purpose",
    ]
    
    for text in philosophical_texts:
        claims = extract_factual_claims(text)
        print(f"Text: '{text[:60]}...'")
        print(f"Claims extracted: {len(claims)}")
        print(f"Result: {'❌ FAILED - should be 0' if claims else '✅ PASSED - filtered out'}")
        print("-" * 60)


def test_prediction_filter():
    """Test that predictions are filtered out"""
    
    print("\n=== PREDICTION FILTER TEST ===\n")
    
    predictions = [
        "The stock market will crash next year according to experts",
        "Climate change is going to cause massive flooding in coastal cities",
        "AI technology shall revolutionize healthcare in the coming decades",
        "The economy would collapse if this policy is implemented",
    ]
    
    for text in predictions:
        claims = extract_factual_claims(text)
        print(f"Text: '{text[:60]}...'")
        print(f"Claims extracted: {len(claims)}")
        print(f"Result: {'❌ FAILED - should be 0' if claims else '✅ PASSED - filtered out'}")
        print("-" * 60)


def test_subjective_filter():
    """Test that subjective comparisons without data are filtered"""
    
    print("\n=== SUBJECTIVE COMPARISON FILTER TEST ===\n")
    
    test_cases = [
        ("This policy is better than the previous one for the country", 0, "Subjective - no data"),
        ("Product A is superior to Product B in every way possible", 0, "Subjective - no data"),
        ("Tesla stock performed 25% better than Ford this quarter", 1, "Factual - has data"),
    ]
    
    for text, expected, description in test_cases:
        claims = extract_factual_claims(text)
        actual = len(claims)
        print(f"Text: '{text[:60]}...'")
        print(f"Description: {description}")
        print(f"Expected: {expected} | Got: {actual}")
        print(f"Result: {'✅ PASSED' if actual == expected else '❌ FAILED'}")
        print("-" * 60)


def test_factual_claims_still_work():
    """Ensure factual claims still get through"""
    
    print("\n=== FACTUAL CLAIMS STILL EXTRACTED ===\n")
    
    factual_texts = [
        "The president announced new economic sanctions against Russia on January 15, 2025",
        "Gold prices increased to $3000 per ounce in trading today",
        "Tesla stock reached $250 per share yesterday according to market data",
    ]
    
    for text in factual_texts:
        claims = extract_factual_claims(text)
        print(f"Text: '{text[:60]}...'")
        print(f"Claims extracted: {len(claims)}")
        print(f"Result: {'✅ PASSED - extracted' if claims else '❌ FAILED - should extract'}")
        if claims:
            print(f"Claim: {claims[0]}")
        print("-" * 60)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  STRENGTHENED FILTER TESTS")
    print("="*60)
    
    test_philosophy_filter()
    test_prediction_filter()
    test_subjective_filter()
    test_factual_claims_still_work()
    
    print("\n" + "="*60)
    print("  ALL TESTS COMPLETE")
    print("="*60 + "\n")
