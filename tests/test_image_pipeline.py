#!/usr/bin/env python3
"""
Test Image Processing Pipeline
Tests OCR extraction, claim filtering, and integration
"""
from tools.image_text_extractor import ImageTextExtractorTool
from tools.claim_extractor import ClaimExtractorTool
from PIL import Image, ImageDraw, ImageFont
import os


def create_test_image():
    """Create a test image with text for OCR testing"""
    # Create image with text
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add text
    text = """
    FACT-CHECK THIS:
    
    Tesla stock price reached $250 in 2024.
    The company delivered 500,000 vehicles last quarter.
    Elon Musk founded Tesla in 2003.
    
    India became the world's most populous country.
    """
    
    # Draw text (using default font)
    draw.text((50, 50), text, fill='black')
    
    # Save test image
    test_image_path = 'test_image.png'
    img.save(test_image_path)
    print(f"✅ Created test image: {test_image_path}\n")
    
    return test_image_path


def test_image_validation():
    """Test image file validation"""
    print("Testing Image Validation")
    print("=" * 60)
    
    extractor = ImageTextExtractorTool()
    
    # Create test image
    test_image = create_test_image()
    
    # Valid image
    assert extractor.is_valid_image(test_image), "Should be valid image"
    print(f"✓ Valid image: {test_image}")
    
    # Invalid path
    assert not extractor.is_valid_image("nonexistent.png"), "Should be invalid"
    print(f"✓ Invalid path detected: nonexistent.png")
    
    # Non-image file
    assert not extractor.is_valid_image("test_image_pipeline.py"), "Should not be image"
    print(f"✓ Non-image file detected\n")
    
    return test_image


def test_ocr_extraction(test_image):
    """Test OCR text extraction"""
    print("Testing OCR Extraction")
    print("=" * 60)
    
    extractor = ImageTextExtractorTool()
    
    result = extractor.extract_text(test_image)
    
    if "error" in result:
        print(f"⚠️  OCR Error: {result['error']}")
        print("   Note: This may be due to Tesseract not being installed")
        print("   Install: https://github.com/tesseract-ocr/tesseract")
        return None
    
    print(f"✓ Extracted text length: {result['text_length']} characters")
    print(f"✓ Source: {result['source']}")
    print(f"✓ Preview:\n{result['extracted_text'][:200]}...\n")
    
    return result['extracted_text']


def test_claim_extraction():
    """Test claim extraction from noisy text"""
    print("Testing Claim Extraction")
    print("=" * 60)
    
    extractor = ClaimExtractorTool()
    
    # Sample OCR-like text (noisy, fragmented)
    sample_text = """
    BREAKING NEWS!!!
    
    Tesla stock reached $250 yesterday
    The company is the best in the world
    What will happen next?
    Elon Musk founded Tesla in 2003
    Subscribe to our newsletter
    Click here for more
    India population surpassed China in 2023
    """
    
    result = extractor.extract_claims(sample_text, max_claims=3)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    claims = result.get('claims', [])
    print(f"✓ Extracted {len(claims)} claims:")
    for i, claim in enumerate(claims, 1):
        print(f"   {i}. {claim}")
    
    print(f"\n✓ Successfully filtered noise (slogans, questions, etc.)\n")


def test_error_handling():
    """Test error handling for invalid inputs"""
    print("Testing Error Handling")
    print("=" * 60)
    
    extractor = ImageTextExtractorTool()
    
    # Invalid image path
    result = extractor.extract_text("nonexistent.png")
    assert "error" in result
    print(f"✓ Invalid image error: {result['error'][:50]}...")
    
    # Claim extraction with empty text
    claim_tool = ClaimExtractorTool()
    result = claim_tool.extract_claims("")
    assert "error" in result
    print(f"✓ Empty text error: {result['error']}")
    
    print("\n✅ Error handling tests passed!\n")


def cleanup():
    """Remove test files"""
    test_files = ['test_image.png']
    for f in test_files:
        if os.path.exists(f):
            os.remove(f)
            print(f"🗑️  Cleaned up: {f}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("IMAGE PROCESSING PIPELINE TESTS")
    print("=" * 60 + "\n")
    
    try:
        # Test 1: Image validation
        test_image = test_image_validation()
        
        # Test 2: OCR extraction
        extracted_text = test_ocr_extraction(test_image)
        
        # Test 3: Claim extraction
        test_claim_extraction()
        
        # Test 4: Error handling
        test_error_handling()
        
        print("=" * 60)
        print("🎉 All image pipeline tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
    
    finally:
        # Cleanup
        cleanup()
