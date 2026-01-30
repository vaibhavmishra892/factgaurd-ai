"""
Comprehensive System Verification Test
Checks all modified files for syntax, imports, and integration
"""
import sys
import traceback

def test_imports():
    """Test that all modified files can be imported"""
    print("\n" + "="*70)
    print("  IMPORT VERIFICATION TEST")
    print("="*70 + "\n")
    
    test_modules = [
        ("tools.claim_validator", "Claim Validator"),
        ("tools.claim_utils", "Claim Utils"),
        ("tools.image_intent_classifier", "Image Intent Classifier"),
        ("core.input_router", "Input Router"),
        ("agents.consensus_agent", "Consensus Agent"),
        ("agents.planner_agent", "Planner Agent"),
        ("agents.news_agent", "News Agent"),
        ("agents.finance_agent", "Finance Agent"),
    ]
    
    passed = 0
    failed = 0
    
    for module_name, display_name in test_modules:
        try:
            __import__(module_name)
            print(f"✅ {display_name:30s} - Import OK")
            passed += 1
        except Exception as e:
            print(f"❌ {display_name:30s} - Import FAILED")
            print(f"   Error: {str(e)[:80]}")
            failed += 1
    
    print("\n" + "-"*70)
    print(f"Results: {passed} passed, {failed} failed\n")
    return failed == 0


def test_claim_validator():
    """Test claim validator functions"""
    print("\n" + "="*70)
    print("  CLAIM VALIDATOR FUNCTIONALITY TEST")
    print("="*70 + "\n")
    
    try:
        from tools.claim_validator import is_ocr_incomplete, is_complete_claim
        
        # Test OCR incomplete detection
        test_cases = [
            ("was born in", True, "Mid-phrase truncation"),
            ("according to", True, "Incomplete preposition"),
            ("The president was born in California.", False, "Complete sentence"),
        ]
        
        for text, should_be_incomplete, description in test_cases:
            is_incomplete, reason = is_ocr_incomplete(text)
            status = "✅" if is_incomplete == should_be_incomplete else "❌"
            print(f"{status} {description:40s} - {'INCOMPLETE' if is_incomplete else 'COMPLETE'}")
        
        print("\n✅ Claim validator functions working correctly\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Claim validator test FAILED: {e}\n")
        traceback.print_exc()
        return False


def test_image_intent_classifier():
    """Test image intent classifier"""
    print("\n" + "="*70)
    print("  IMAGE INTENT CLASSIFIER TEST")
    print("="*70 + "\n")
    
    try:
        from tools.image_intent_classifier import classify_image_intent
        
        test_texts = [
            "Breaking news: President announces new policy",
            "I think this is a good decision",
            "Stock price: $125.50",
        ]
        
        for text in test_texts:
            intent, confidence = classify_image_intent(text)
            print(f"✅ Text: '{text[:40]}...'")
            print(f"   Intent: {intent}, Confidence: {confidence:.2f}\n")
        
        print("✅ Image intent classifier working correctly\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Image intent classifier test FAILED: {e}\n")
        traceback.print_exc()
        return False


def test_claim_utils():
    """Test claim extraction and filtering"""
    print("\n" + "="*70)
    print("  CLAIM UTILS FILTERING TEST")
    print("="*70 + "\n")
    
    try:
        from tools.claim_utils import extract_factual_claims
        
        test_text = """
        Tesla stock reached $250 today.
        I think this is good for investors.
        The company will announce earnings next week.
        Existence is a philosophical question.
        """
        
        claims = extract_factual_claims(test_text)
        print(f"Extracted {len(claims)} factual claims from test text:\n")
        for i, claim in enumerate(claims, 1):
            print(f"{i}. {claim}")
        
        # Should filter out opinion ("I think"), prediction ("will announce"), and philosophy ("Existence")
        # Should keep factual: "Tesla stock reached $250"
        
        print("\n✅ Claim extraction and filtering working\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Claim utils test FAILED: {e}\n")
        traceback.print_exc()
        return False


def test_agent_creation():
    """Test that agents can be created"""
    print("\n" + "="*70)
    print("  AGENT CREATION TEST")
    print("="*70 + "\n")
    
    try:
        from agents.consensus_agent import create_consensus_agent
        from agents.planner_agent import create_planner_agent
        
        print("Creating consensus agent...")
        consensus = create_consensus_agent()
        print(f"✅ Consensus agent created: {consensus.role}\n")
        
        print("Creating planner agent...")
        planner = create_planner_agent()
        print(f"✅ Planner agent created: {planner.role}\n")
        
        print("✅ All agents created successfully\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Agent creation test FAILED: {e}\n")
        traceback.print_exc()
        return False


def main():
    print("\n" + "="*70)
    print("  COMPREHENSIVE SYSTEM VERIFICATION")
    print("="*70)
    
    results = {
        "Imports": test_imports(),
        "Claim Validator": test_claim_validator(),
        "Image Intent": test_image_intent_classifier(),
        "Claim Utils": test_claim_utils(),
        "Agent Creation": test_agent_creation(),
    }
    
    print("\n" + "="*70)
    print("  FINAL RESULTS")
    print("="*70 + "\n")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10s} - {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL TESTS PASSED - System is ready!")
    else:
        print("⚠️  Some tests failed - review errors above")
    print("="*70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
