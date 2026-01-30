"""Claim Validation Module
Validates claim completeness before fact-checking
Includes OCR completeness check and headline normalization"""
import re
from typing import List, Tuple, Dict, Optional


def is_ocr_incomplete(text: str) -> Tuple[bool, str]:
    """
    Check if text appears to be incomplete OCR extraction.
    This is a HARD GATE - incomplete OCR must NOT be verified.
    
    Returns (is_incomplete, reason)
    
    OCR is incomplete if:
    - Ends mid-phrase (common OCR truncations)
    - Missing terminal punctuation AND semantic closure
    - Clearly truncated connectors
    """
    text = text.strip()
    
    # Common mid-phrase endings (OCR truncation indicators)
    mid_phrase_endings = [
        'was born in',
        'according to',
        'said that',
        'reported that',
        'announced that',
        'stated that',
        'claims that',
        'believes that',
        'in the',
        'on the',
        'at the',
        'from the',
        'by the',
        'to the',
        'of the',
        'and the',
        'with a',
        'for a',
        'as a',
        'is a',
        'was a'
    ]
    
    text_lower = text.lower()
    
    # Check for mid-phrase truncation
    for ending in mid_phrase_endings:
        if text_lower.endswith(ending):
            return True, f"Text appears truncated (ends with '{ending}')"
    
    # Check for very short text without clear semantic closure
    words = text.split()
    if len(words) < 5 and not text.endswith(('.', '!', '?', '%')):
        return True, "Text too short and lacks semantic closure"
    
    # Check for missing object after transitive verbs
    transitive_verb_patterns = [
        r'\b(announced|reported|said|stated|claimed|confirmed|denied)$',
        r'\b(increased|decreased|rose|fell|grew|declined)\s+by$',
        r'\b(according|due|thanks)\s+to$'
    ]
    
    for pattern in transitive_verb_patterns:
        if re.search(pattern, text_lower):
            return True, "Text ends with incomplete verb phrase"
    
    return False, ""


def is_complete_claim(claim: str) -> Tuple[bool, str]:
    """
    Check if a claim is complete enough to verify.
    Returns (is_valid, reason_if_invalid)
    
    STEP 1: OCR completeness check (HARD GATE)
    STEP 2: Structural completeness check
    
    A complete claim must have:
    - Subject (who/what)
    - Verb (action/state)
    - Object or predicate (what happened)
    
    Incomplete examples:
    - "captured President Nicolas" (no subject)
    - "The company announced" (no object)
    - "according to sources" (fragment)
    """
    claim = claim.strip()
    
    # STEP 1: Check for OCR incompleteness (HARD GATE)
    is_incomplete, ocr_reason = is_ocr_incomplete(claim)
    if is_incomplete:
        return False, f"OCR text appears incomplete: {ocr_reason}"
    
    # STEP 2: Structural checks
    # Too short
    if len(claim.split()) < 5:
        return False, "Claim is too short (less than 5 words)"
    
    # Check for basic verb presence
    if not _has_verb(claim):
        return False, "Missing action verb - appears to be a fragment"
    
    # Check for sentence fragments (common OCR issues)
    fragment_indicators = [
        # Starts with conjunction
        re.compile(r'^(and|or|but|because|since|while|although)\s+', re.I),
        # Starts with verb without subject
        re.compile(r'^(captured|took|said|went|came)\s+', re.I),
    ]
    
    for pattern in fragment_indicators:
        if pattern.search(claim):
            return False, "Appears to be a sentence fragment, not a complete claim"
    
    # Check minimum word count (complete claims rarely < 5 words)
    words = claim.split()
    if len(words) < 5:
        return False, "Too few words to form a meaningful claim"
    
    # Check for proper noun or subject
    if not _has_subject(claim):
        return False, "Missing clear subject"
    
    return True, None


def _has_verb(text: str) -> bool:
    """Check if text contains action verbs"""
    # Common verbs in claims
    verb_patterns = [
        r'\b(is|are|was|were|has|have|had|will|would|can|could|did|does)\b',
        r'\b(announced|reported|confirmed|denied|stated|claimed)\b',
        r'\b(increased|decreased|rose|fell|reached|hit|surged)\b',
        r'\b(attacked|invaded|captured|arrested|killed|injured)\b',
        r'\b(signed|passed|approved|rejected|banned|authorized)\b',
    ]
    
    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in verb_patterns)


def _has_subject(text: str) -> bool:
    """Check if text has a clear subject (proper noun or definite noun phrase)"""
    # Look for proper nouns (capitalized words not at start)
    words = text.split()
    if len(words) < 2:
        return False
    
    # Check for proper nouns in non-first positions (indicates subject)
    for i, word in enumerate(words[1:], 1):
        if word[0].isupper() and not word.isupper():  # Capitalized but not acronym
            return True
    
    # Check for definite articles + noun ("the president", "a company")
    if re.search(r'\b(the|a|an)\s+[a-z]+', text.lower()):
        return True
    
    # Check for pronouns as subjects
    if re.search(r'\b(he|she|it|they|we|this|that)\s+(is|are|was|were|has|have)', text.lower()):
        return True
    
    return False


def merge_related_fragments(claims: List[str]) -> List[str]:
    """
    Merge related claim fragments into complete narratives
    
    Args:
        claims: List of potential claim fragments
        
    Returns:
        List of merged, complete claims
    """
    if len(claims) <= 1:
        return claims
    
    merged = []
    skip_indices = set()
    
    for i, claim1 in enumerate(claims):
        if i in skip_indices:
            continue
        
        # Try to find related fragments
        related = [claim1]
        
        for j, claim2 in enumerate(claims[i+1:], i+1):
            if j in skip_indices:
                continue
            
            # Check if claims are related (same proper nouns, events)
            if _are_related(claim1, claim2):
                related.append(claim2)
                skip_indices.add(j)
        
        # Merge if we found related fragments
        if len(related) > 1:
            merged_claim = _merge_claims(related)
            merged.append(merged_claim)
        else:
            merged.append(claim1)
    
    return merged


def _are_related(claim1: str, claim2: str) -> bool:
    """Check if two claims are about the same event/narrative"""
    # Extract proper nouns from both
    nouns1 = set(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', claim1))
    nouns2 = set(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', claim2))
    
    # If they share significant proper nouns, likely related
    if len(nouns1 & nouns2) >= 1:
        return True
    
    # Check for pronoun references (he, she, they referring back)
    pronouns = ['he', 'she', 'they', 'it', 'them', 'him', 'her']
    claim2_lower = claim2.lower()
    if any(claim2_lower.startswith(p + ' ') or ' ' + p + ' ' in claim2_lower for p in pronouns):
        return True
    
    return False


def _merge_claims(claims: List[str]) -> str:
    """Intelligently merge multiple claim fragments into one coherent claim"""
    if len(claims) == 1:
        return claims[0]
    
    # Simple concatenation with "and" connector
    # Remove redundant proper nouns in subsequent claims
    base = claims[0]
    
    for claim in claims[1:]:
        # If claim starts with a verb or pronoun, connect directly
        if re.match(r'^(and |captured |took |said |arrested )', claim, re.I):
            base = base.rstrip('.') + ' ' + claim
        else:
            base = base.rstrip('.') + ' and ' + claim
    
    return base


def classify_claim_issue(text: str) -> str:
    """
    Generate friendly message explaining why claim is incomplete
    
    Args:
        text: The incomplete claim text
        
    Returns:
        User-friendly explanation
    """
    is_valid, reason = is_complete_claim(text)
    
    if is_valid:
        return ""  # No issue
    
    # Return polite, helpful message
    return f"""ℹ️  The extracted text does not form a complete factual claim.

The content appears to be {_get_fragment_description(reason)}.

Please provide a complete claim with a clear subject, action, and context for verification."""


def _get_fragment_description(reason: str) -> str:
    """Convert technical reason to user-friendly description"""
    if "fragment" in reason.lower():
        return "a sentence fragment or partial statement"
    elif "verb" in reason.lower():
        return "missing an action or verb"
    elif "subject" in reason.lower():
        return "missing a clear subject"
    elif "short" in reason.lower() or "few words" in reason.lower():
        return "too brief or incomplete"
    else:
        return "incomplete or unclear"
