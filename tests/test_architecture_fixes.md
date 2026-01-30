# Architectural Violation Fixes - Test Checklist

## V-001: Input Detection Removed from fact_verifier
- [ ] Test text claim still works
- [ ] Test URL input still works
- [ ] Test image input still works
- [ ] Verify fact_verifier has NO input detection code

## V-002: claim_extractor is Stateless
- [ ] Verify no LLM in claim_extractor.__init__
- [ ] Test claim extraction still works
- [ ] Verify delegates to claim_utils

## V-003: Single Claim Extraction Pipeline
- [ ] Verify article_extractor has no extract_claims method
- [ ] All claim extraction uses tools/claim_utils.py

## V-004: Planner Authority Restored
- [ ] Planner outputs input_type
- [ ] main.py uses planner decision
- [ ] input_router trusts planner output

## Integration Tests
- [ ] Run test_simple_ocr.py
- [ ] Run main.py with text claim
- [ ] Run main.py with URL (if available)
- [ ] Run main.py with image (requires Tesseract)
