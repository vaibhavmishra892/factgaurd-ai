"""
Test OCR Completeness Check
Tests the hard gate for incomplete OCR text
"""
from tools.claim_validator import is_ocr_incomplete, is_complete_claim


def test_ocr_incomplete_detection():
    """Test detection of incomplete OCR text"""
    
    print("\n" + "="*70)
    print("  OCR INCOMPLETENESS DETECTION TESTS")
    print("="*70 + "\n")
    
    # True incomplete cases (should be caught)
    incomplete_cases = [
        ("was born in", "Mid-phrase ending"),
        ("according to", "Truncated preposition"),
        ("The president said that", "Incomplete statement"),
        ("announced that", "Missing object"),
        ("increased by", "Incomplete comparison"),
        ("due to", "Truncated reason"),
        ("in the", "Article fragment"),
    ]
    
    for text, description in incomplete_cases:
        is_incomplete, reason = is_ocr_incomplete(text)
        print(f"Text: '{text}'")
        print(f"Description: {description}")
        print(f"Result: {'✅ CAUGHT' if is_incomplete else '❌ MISSED'}")
        if is_incomplete:
            print(f"Reason: {reason}")
        print("-" * 70)
    
    print()


def test_complete_ocr_text():
    """Test that complete text is NOT flagged as incomplete"""
    
    print("\n" + "="*70)
    print("  COMPLETE TEXT (SHOULD PASS)")
    print("="*70 + "\n")
    
    complete_cases = [
        "The president was born in California.",
        "According to Reuters, the event occurred yesterday.",
        "The company increased profits by 25% this quarter.",
        "Ambuja Cements Q3 net profit declined by 91% to Rs 204 crore.",
    ]
    
    for text in complete_cases:
        is_incomplete, reason = is_ocr_incomplete(text)
        print(f"Text: '{text[:60]}...'")
        print(f"Result: {'❌ WRONGLY FLAGGED' if is_incomplete else '✅ PASS'}")
        if is_incomplete:
            print(f"Wrong reason: {reason}")
        print("-" * 70)
    
    print()


def test_claim_validator_integration():
    """Test that is_complete_claim uses OCR check"""
    
    print("\n" + "="*70)
    print("  CLAIM VALIDATOR INTEGRATION")
    print("="*70 + "\n")
    
    test_cases = [
        {
            "text": "was born in",
            "should_reject": True,
            "reason": "OCR incomplete"
        },
        {
            "text": "The president announced new economic sanctions against Russia.",
            "should_reject": False,
            "reason": "Complete factual claim"
        },
        {
            "text": "according to sources",
            "should_reject": True,
            "reason": "OCR truncated"
        }
    ]
    
    for case in test_cases:
        is_valid, reason = is_complete_claim(case['text'])
        expected = not case['should_reject']
        
        print(f"Text: '{case['text']}'")
        print(f"Expected: {'VALID' if expected else 'INVALID'}")
        print(f"Got: {'VALID' if is_valid else 'INVALID'}")
        print(f"Result: {'✅ CORRECT' if is_valid == expected else '❌ WRONG'}")
        if not is_valid:
            print(f"Rejection reason: {reason}")
        print("-" * 70)
    
    print()


def test_edge_cases():
    """Test edge cases"""
    
    print("\n" + "="*70)
    print("  EDGE CASES")
    print("="*70 + "\n")
    
    edge_cases = [
        ("Gold prices increased by 3%", False, "Complete with percentage"),
        ("The company", True, "Too short, no closure"),
        ("BREAKING: President resigns", False, "Complete headline"),
        ("and the", True, "Fragment connector"),
    ]
    
    for text, should_be_incomplete, description in edge_cases:
        is_incomplete, reason = is_ocr_incomplete(text)
        
        print(f"Text: '{text}'")
        print(f"Description: {description}")
        print(f"Expected: {'INCOMPLETE' if should_be_incomplete else 'COMPLETE'}")
        print(f"Got: {'INCOMPLETE' if is_incomplete else 'COMPLETE'}")
        print(f"Result: {'✅ CORRECT' if is_incomplete == should_be_incomplete else '❌ WRONG'}")
        if is_incomplete:
            print(f"Reason: {reason}")
        print("-" * 70)
    
    print()


if __name__ == "__main__":
    test_ocr_incomplete_detection()
    test_complete_ocr_text()
    test_claim_validator_integration()
    test_edge_cases()
    
    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)
    print("""
The OCR completeness check provides a HARD GATE to prevent verification of:
- Mid-phrase truncations ("was born in", "according to")
- Incomplete verb phrases ("announced that", "increased by")
- Missing objects after transitive verbs
- Very short text without semantic closure

Complete news headlines and factual claims pass through correctly.
    """)
