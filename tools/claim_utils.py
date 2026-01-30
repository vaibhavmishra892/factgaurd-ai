"""
Claim Extraction Utilities
Pure stateless functions for extracting factual claims from text
NO LLM - rule-based only
"""
import re
from typing import List
from tools.claim_validator import is_complete_claim, merge_related_fragments


def extract_factual_claims(text: str, max_claims: int = 5) -> List[str]:
    """
    Extract verifiable factual claims from text using heuristics
    
    Args:
        text: Raw text (from OCR, article, etc.)
        max_claims: Maximum number of claims to extract
        
    Returns:
        List of complete, validated factual claim sentences
    """
    if not text or len(text.strip()) < 10:
        return []
    
    # Split into sentences
    sentences = _split_into_sentences(text)
    
    # Filter for factual sentences
    factual = _filter_factual_sentences(sentences)
    
    # Merge related fragments into complete claims
    merged = merge_related_fragments(factual)
    
    # Validate completeness - only return complete claims
    validated = []
    for claim in merged:
        is_valid, reason = is_complete_claim(claim)
        if is_valid:
            validated.append(claim)
    
    return validated[:max_claims]


def _split_into_sentences(text: str) -> List[str]:
    """Split text into sentences"""
    sentences = re.split(r'[.!?\n]+', text)
    # Increased minimum length from 15 to 25 for better quality
    sentences = [s.strip() for s in sentences if len(s.strip()) > 25]
    return sentences


def _filter_factual_sentences(sentences: List[str]) -> List[str]:
    """
    Filter sentences that likely contain factual claims
    
    Rules:
    - Skip questions
    - Skip opinions (think, believe, should, best, worst)
    - Skip rhetoric (fight, destroy, evil)
    - Prefer sentences with numbers, dates, proper nouns
    """
    factual = []
    
    for sentence in sentences:
        # Skip if too short (increased from 20 to 30)
        if len(sentence) < 30:
            continue
        
        # Skip questions
        if sentence.strip().endswith('?'):
            continue
        
        # Skip common non-factual patterns
        opinion_words = ['think', 'believe', 'feel', 'should', 'must', 'best', 'worst',
                        'opinion', 'suggests', 'may', 'could', 'might']
        if any(word in sentence.lower() for word in opinion_words):
            continue
        
        # Skip predictions (NEW)
        prediction_patterns = ['will', 'going to', 'shall', 'would', 'won\'t', 'gonna']
        if any(pattern in sentence.lower() for pattern in prediction_patterns):
            continue
        
        # Skip philosophical/abstract concepts (NEW)
        philosophy_keywords = ['existence', 'consciousness', 'reality', 'truth', 'meaning', 
                              'purpose', 'ethics', 'morality', 'justice', 'virtue',
                              'what is life', 'why do we', 'human nature']
        if any(keyword in sentence.lower() for keyword in philosophy_keywords):
            continue
        
        # Skip subjective comparatives (NEW)
        subjective_words = ['better', 'worse', 'superior', 'inferior', 'greatest', 'worst']
        # Allow if it's a quote or has numbers (comparison with data is factual)
        has_numbers = bool(re.search(r'\d+', sentence))
        if not has_numbers and any(word in sentence.lower() for word in subjective_words):
            continue
        
        # Skip emotional/political rhetoric
        rhetoric_words = ['fight', 'destroy', 'evil', 'hero', 'enemy']
        if any(word in sentence.lower() for word in rhetoric_words):
            continue
        
        # Prefer sentences with numbers, dates, proper nouns
        has_number = bool(re.search(r'\d+', sentence))
        has_proper_noun = bool(re.search(r'\b[A-Z][a-z]+\b', sentence))
        has_date = bool(re.search(r'\b(19|20)\d{2}\b', sentence))
        
        if has_number or has_date or has_proper_noun:
            factual.append(sentence)
    
    return factual
