"""
Claim Extractor Tool (DEPRECATED - Use claim_utils.extract_factual_claims)
Wrapper for backward compatibility - delegates to stateless utility
"""
from typing import Dict
from tools.claim_utils import extract_factual_claims


class ClaimExtractorTool:
    """Tool for extracting verifiable claims from raw text (NO LLM - stateless)"""
    
    def __init__(self):
        """No initialization needed - stateless tool"""
        pass
    
    def extract_claims(self, text: str, max_claims: int = 5) -> Dict[str, any]:
        """
        Extract verifiable factual claims from text (delegates to stateless utility)
        
        Args:
            text: Raw text (often from OCR)
            max_claims: Maximum number of claims to extract
            
        Returns:
            Dictionary with extracted claims and metadata
        """
        if not text or len(text.strip()) < 10:
            return {"error": "Text too short or empty"}
        
        # Delegate to stateless utility (NO LLM)
        claims = extract_factual_claims(text, max_claims)
        
        if not claims:
            return {
                "claims": [],
                "message": "No factual claims found in text"
            }
        
        return {
            "claims": claims,
            "claim_count": len(claims),
            "source": "Claim Extractor (Rule-based)"
        }

