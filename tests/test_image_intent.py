"""
Test Image Intent Classification
Tests the image intent classifier with various OCR text scenarios
"""
from tools.image_intent_classifier import (
    classify_image_intent,
    reconstruct_claims_from_image,
    should_verify_image_content,
    ImageIntent
)


def test_news_viral_claims():
    """Test detection of news/viral claims"""
    
    print("\n=== NEWS/VIRAL CLAIM DETECTION ===\n")
    
    test_cases = [
        ("US attacked Venezuela yesterday and captured President Maduro", "Complete news"),
        ("Man kills leopard. Forest department files case", "Local news"),
        ("Breaking: Minister announced new policy today", "Breaking news"),
        ("President arrested by military forces", "Political news"),
    ]
    
    for text, description in test_cases:
        intent = classify_image_intent(text)
        print(f"Text: '{text}'")
        print(f"Description: {description}")
        print(f"Intent: {intent.value}")
        print(f"Match: {'✅ NEWS' if intent == ImageIntent.NEWS_OR_VIRAL_CLAIM else '❌ WRONG'}")
        print("-" * 60)


def test_opinion_detection():
    """Test detection of opinions vs news"""
    
    print("\n=== OPINION VS NEWS DETECTION ===\n")
    
    test_cases = [
        ("I think this government is evil", "Pure opinion", ImageIntent.OPINION_OR_COMMENTARY),
        ("This will destroy the country", "Opinion/prediction", ImageIntent.OPINION_OR_COMMENTARY),
        ("Minister said this policy will help economy", "News (quoting)", ImageIntent.NEWS_OR_VIRAL_CLAIM),
    ]
    
    for text, description, expected in test_cases:
        intent = classify_image_intent(text)
        print(f"Text: '{text}'")
        print(f"Description: {description}")
        print(f"Expected: {expected.value}")
        print(f"Got: {intent.value}")
        print(f"Match: {'✅ CORRECT' if intent == expected else '❌ WRONG'}")
        print("-" * 60)


def test_claim_reconstruction():
    """Test reconstruction of fragmented OCR text"""
    
    print("\n=== CLAIM RECONSTRUCTION ===\n")
    
    # Fragmented news text (like OCR from image)
    fragmented_text = """US attacked Venezuela
captured President Nicolas
Maduro and his wife
took them to military base"""
    
    print("Fragmented OCR text:")
    print(fragmented_text)
    print("\n")
    
    claims = reconstruct_claims_from_image(fragmented_text)
    
    print(f"Reconstructed {len(claims)} claim(s):")
    for i, claim in enumerate(claims, 1):
        print(f"{i}. {claim}")
    print("-" * 60)


def test_should_verify():
    """Test the main decision function"""
    
    print("\n=== VERIFICATION DECISION TESTS ===\n")
    
    test_cases = [
        ("US attacked Venezuela captured Maduro", "Fragmented news"),
        ("Gold price today: $3000/oz", "Time-sensitive data"),
        ("I believe this is wrong", "Opinion"),
        ("Buy now! 50% discount", "Advertisement"),
    ]
    
    for text, description in test_cases:
        should_verify, reason, claims = should_verify_image_content(text)
        
        print(f"Text: '{text}'")
        print(f"Description: {description}")
        print(f"Should verify: {'✅ YES' if should_verify else '❌ NO'}")
        print(f"Reason: {reason}")
        if claims:
            print(f"Reconstructed claims: {claims}")
        print("-" * 60)


def test_edge_cases():
    """Test edge cases"""
    
    print("\n=== EDGE CASES ===\n")
    
    edge_cases = [
        ("", "Empty string"),
        ("abc", "Too short"),
        ("This is just random text without news keywords", "Generic text"),
        ("Breaking News: US attacked Venezuela and captured President Nicolas Maduro", "Ideal news format"),
    ]
    
    for text, description in edge_cases:
        intent = classify_image_intent(text)
        should_verify, reason, claims = should_verify_image_content(text)
        
        print(f"Case: {description}")
        print(f"Intent: {intent.value}")
        print(f"Should verify: {'YES' if should_verify else 'NO'}")
        print(f"Reason: {reason}")
        print("-" * 60)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  IMAGE INTENT CLASSIFICATION TESTS")
    print("="*60)
    
    test_news_viral_claims()
    test_opinion_detection()
    test_claim_reconstruction()
    test_should_verify()
    test_edge_cases()
    
    print("\n" + "="*60)
    print("  ALL TESTS COMPLETE")
    print("="*60 + "\n")
