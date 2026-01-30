#!/usr/bin/env python3
"""
Fact Verification AI - CLI Interface
NEW ARCHITECTURE: Planner decides input type → Router preprocesses → Verifier verifies
"""

from fact_verifier import fact_verifier
from core.input_router import InputRouter
from config import config
import os
import re


def detect_input_type(user_input: str) -> str:
    """
    Detect input modality (used by planner logic)
    
    Args:
        user_input: Raw user input
        
    Returns:
        'text', 'url', or 'image'
    """
    # Check for URL
    if re.match(r'https?://', user_input):
        return 'url'
    
    # Check for image file
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']
    ext = os.path.splitext(user_input)[1].lower()
    if ext in image_extensions and os.path.exists(user_input):
        return 'image'
    
    # Default to text
    return 'text'


def main():
    print("\n" + "="*60)
    print("🔍 FACT VERIFICATION AI")
    print("="*60)
    print("Verify claims from text, URLs, or images.\n")
    
    # Validate config on startup
    config.validate()
    print()
    
    # Initialize router
    router = InputRouter()
    
    try:
        user_input = input("📝 Enter claim, URL, or image path: ").strip()
        
        if len(user_input) < 5:
            print("⚠️  Please enter a valid claim, URL, or image path (at least 5 characters).")
            return
        
        print("\n⏳ Processing input...\n")
        
        # STEP 1: Detect input type (simulating planner decision)
        input_type = detect_input_type(user_input)
        print(f"📋 Input type detected: {input_type.upper()}")
        
        # STEP 2: Route to appropriate preprocessing
        if input_type in ['url', 'image']:
            print(f"🔄 Routing to {input_type} processor...\n")
            routed_result = router.route(input_type, user_input)
            
            if "error" in routed_result:
                print(f"❌ Error: {routed_result['error']}\n")
                return
            
            # Extract claims from routing result
            claims = routed_result['claims']
            skip_validation = routed_result.get('skip_validation', False)  # Get flag for reconstructed claims
            source_info = {
                'source': routed_result.get('source', user_input),
                'title': routed_result.get('title')
            }
            
            print(f"✅ Found {len(claims)} claims to verify\n")
            
            # STEP 3: Verify claims
            result = fact_verifier.verify_claims_batch(claims, source_info, skip_validation=skip_validation)
        else:
            # Direct text claim - verify immediately
            print("📝 Processing text claim...\n")
            result = fact_verifier.verify_claim(user_input)
        
        # Display results
        print("\n" + "="*60)
        print("📊 VERIFICATION RESULT")
        print("="*60)
        print(result)
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure program exits cleanly
        import sys
        print("✅ Verification complete. Exiting...\n")
        sys.stdout.flush()
        sys.exit(0)

if __name__ == "__main__":
    main()
