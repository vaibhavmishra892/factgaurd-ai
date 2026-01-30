"""
Test Claim Quality Validation
Tests the claim validator with complete and incomplete claims
"""
from tools.claim_validator import (
    is_complete_claim,
    merge_related_fragments,
    classify_claim_issue
)


def test_incomplete_fragments():
    """Test detection of incomplete claim fragments"""
    
    print("\n=== TESTING INCOMPLETE FRAGMENTS ===\n")
    
    fragments = [
        "captured President Nicolas",
        "Maduro and his wife, took them",
        "and destroyed the building",
        "in the capital city",
    ]
    
    for fragment in fragments:
        is_valid, reason = is_complete_claim(fragment)
        print(f"Text: '{fragment}'")
        print(f"Valid: {is_valid}")
        if not is_valid:
            print(f"Reason: {reason}")
            print(f"User Message:\n{classify_claim_issue(fragment)}")
        print("-" * 60)


def test_complete_claims():
    """Test acceptance of complete claims"""
    
    print("\n=== TESTING COMPLETE CLAIMS ===\n")
    
    complete_claims = [
        "The United States attacked Venezuela and captured President Nicolás Maduro",
        "Tesla stock reached $250 per share on January 15, 2025",
        "Gold prices increased to $3000 per ounce today",
        "The president announced new economic sanctions against Russia",
    ]
    
    for claim in complete_claims:
        is_valid, reason = is_complete_claim(claim)
        print(f"Claim: '{claim}'")
        print(f"Valid: {'✅ YES' if is_valid else '❌ NO'}")
        if not is_valid:
            print(f"Reason: {reason}")
        print("-" * 60)


def test_fragment_merging():
    """Test merging of related fragments"""
    
    print("\n=== TESTING FRAGMENT MERGING ===\n")
    
    fragments = [
        "The US military invaded Venezuela",
        "captured President Nicolas Maduro",
        "took him to a secure location",
    ]
    
    print("Original fragments:")
    for i, frag in enumerate(fragments, 1):
        print(f"  {i}. {frag}")
    
    merged = merge_related_fragments(fragments)
    
    print(f"\nMerged result ({len(merged)} claim(s)):")
    for i, claim in enumerate(merged, 1):
        print(f"  {i}. {claim}")
        is_valid, reason = is_complete_claim(claim)
        print(f"     Valid: {'✅ YES' if is_valid else '❌ NO'}")
    print("-" * 60)


def test_edge_cases():
    """Test edge cases"""
    
    print("\n=== TESTING EDGE CASES ===\n")
    
    edge_cases = [
        ("", "Empty string"),
        ("Hi", "Too short"),
        ("Is this true?", "Question"),
        ("The stock is at $250", "Somewhat complete"),
    ]
    
    for text, description in edge_cases:
        is_valid, reason = is_complete_claim(text)
        print(f"Case: {description}")
        print(f"Text: '{text}'")
        print(f"Valid: {is_valid}")
        if not is_valid:
            print(f"Reason: {reason}")
        print("-" * 60)


def test_from_claim_utils():
    """Test integration with claim_utils"""
    
    print("\n=== TESTING CLAIM_UTILS INTEGRATION ===\n")
    
    from tools.claim_utils import extract_factual_claims
    
    # Test with mixed quality text
    text = """
    The United States military attacked Venezuela yesterday.
    captured President Nicolas Maduro.
    and took him.
    This is a major international incident.
    """
    
    print("Input text:")
    print(text)
    print("\nExtracted claims:")
    
    claims = extract_factual_claims(text)
    
    if claims:
        for i, claim in enumerate(claims, 1):
            print(f"{i}. {claim}")
    else:
        print("  (No valid claims extracted)")
    
    print("-" * 60)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  CLAIM QUALITY VALIDATION TESTS")
    print("="*60)
    
    test_incomplete_fragments()
    test_complete_claims()
    test_fragment_merging()
    test_edge_cases()
    test_from_claim_utils()
    
    print("\n" + "="*60)
    print("  ALL TESTS COMPLETE")
    print("="*60 + "\n")
