"""
Input Router
Centralizes input modality routing based on planner decisions
"""
from typing import Dict, List
from tools.article_extractor import ArticleExtractorTool
from tools.image_text_extractor import ImageTextExtractorTool
from tools.claim_utils import extract_factual_claims
from schemas.response_messages import classify_and_respond
from tools.image_intent_classifier import (
    should_verify_image_content,
    format_image_verdict_response
)


class InputRouter:
    """Routes input based on planner's decision (does NOT detect type itself)"""
    
    def __init__(self):
        """Initialize tools for preprocessing"""
        self.article_extractor = ArticleExtractorTool()
        self.image_text_extractor = ImageTextExtractorTool()
    
    def route(self, input_type: str, content: str) -> Dict[str, any]:
        """
        Route input based on type determined by planner
        
        Args:
            input_type: Type from planner ('text', 'url', or 'image')
            content: The input content
            
        Returns:
            Dictionary with extracted claims and metadata
        """
        if input_type == "image":
            return self._process_image(content)
        elif input_type == "url":
            return self._process_url(content)
        elif input_type == "text":
            return self._process_text(content)
        else:
            return {"error": f"Unknown input type: {input_type}"}
    
    def _process_image(self, image_path):
        """Process image input - extract text and verify claims"""
        print(f"📷 Processing image: {image_path}")
        
        # Step 1: OCR - extract text from image
        ocr_result = self.image_text_extractor.extract_text(image_path)
        
        if "error" in ocr_result:
            return ocr_result
        
        ocr_text = ocr_result.get("extracted_text", "")
        print(f"📝 Extracted text ({len(ocr_text)} chars):")
        print(f"\n{'='*60}")
        print(ocr_text)
        print(f"{'='*60}\n")
        
        # Step 2: IMAGE INTENT CLASSIFICATION (NEW - CRITICAL)
        # Determine if this is news/viral content that should be verified
        should_verify, reason, reconstructed_claims = should_verify_image_content(ocr_text)
        
        print(f"🎯 Image intent: {reason}")
        
        # If NOT verifiable (opinion, ad, time-sensitive, etc.), return friendly message
        if not should_verify:
            friendly_message = format_image_verdict_response(should_verify, reason, ocr_text)
            return {"error": friendly_message}
        
        # Step 3: Use reconstructed claims for NEWS/VIRAL images
        # This is MORE LENIENT than direct text input
        if reconstructed_claims:
            print(f"✅ Reconstructed {len(reconstructed_claims)} claims from image")
            claims = reconstructed_claims
        else:
            # Fallback to normal extraction
            claims = extract_factual_claims(ocr_text)
        
        # Step 4: Verify reconstructed claims
        if not claims:
            # Even for news images, if we can't extract anything meaningful
            return {
                "error": classify_and_respond(ocr_text, "image")
            }
        
        print(f"🔍 Verifying {len(claims)} claim(s) from image...")
        
        # Determine if we should skip validation
        # Skip for reconstructed claims (MORE LENIENT for images)
        skip_validation = bool(reconstructed_claims)
        
        return {
            "input_type": "image",
            "source": image_path,
            "claims": claims,
            "skip_validation": skip_validation,  # Pass flag to main.py
            "metadata": {
                "text_length": ocr_result['text_length']
            }
        }
    
    def _process_url(self, url: str) -> Dict[str, any]:
        """Extract article and identify claims"""
        # Step 1: Fetch article
        article_result = self.article_extractor.extract_article(url)
        
        if "error" in article_result:
            return article_result
        
        # Step 2: Extract claims using shared utility
        claims = extract_factual_claims(
            article_result['content'],
            max_claims=3
        )
        
        # Step 3: Handle no claims with intelligent, friendly message
        if not claims:
            return {
                "error": classify_and_respond(
                    article_result['content'],
                    "article"
                )
            }
        
        return {
            "input_type": "url",
            "source": url,
            "title": article_result['title'],
            "claims": claims,
            "metadata": {
                "word_count": article_result['word_count']
            }
        }
    
    def _process_text(self, text: str) -> Dict[str, any]:
        """Process direct text input"""
        return {
            "input_type": "text",
            "source": "direct_input",
            "claims": [text],  # Single claim
            "metadata": {}
        }
