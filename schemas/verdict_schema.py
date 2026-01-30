from pydantic import BaseModel, Field
from typing import List, Literal
from schemas.claim_schema import EvidenceSource

class VerdictResult(BaseModel):
    """Final verification verdict with confidence and evidence"""
    verdict: Literal["VERIFIED", "CONTRADICTED", "PARTIALLY TRUE", "UNVERIFIABLE"] = Field(
        ..., 
        description="Final verdict on the claim"
    )
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Confidence score between 0 and 1"
    )
    summary: str = Field(
        ..., 
        description="Human-readable summary of findings"
    )
    evidence: List[EvidenceSource] = Field(
        default_factory=list, 
        description="List of evidence sources used"
    )
    notes: str = Field(
        default="", 
        description="Additional notes or context"
    )
    contradictions: List[str] = Field(
        default_factory=list, 
        description="List of contradictions found if any"
    )

def format_verdict_for_display(verdict: VerdictResult) -> str:
    """
    Format VerdictResult into human-readable text for Gradio UI.
    NO raw JSON output!
    """
    # Determine confidence level text
    if verdict.confidence >= 0.8:
        confidence_level = "High"
    elif verdict.confidence >= 0.5:
        confidence_level = "Medium"
    else:
        confidence_level = "Low"
    
    # Build output string
    output_lines = []
    output_lines.append(f"**Verdict:** {verdict.verdict}")
    output_lines.append(f"**Confidence:** {confidence_level} ({verdict.confidence:.2f})")
    output_lines.append(f"\n**Summary:**\n{verdict.summary}")
    
    # Add evidence sources
    if verdict.evidence:
        output_lines.append(f"\n**Evidence Sources ({len(verdict.evidence)}):**")
        for i, source in enumerate(verdict.evidence, 1):
            source_line = f"• **{source.source_name}** — {source.source_type}"
            if source.date:
                source_line += f" ({source.date})"
            output_lines.append(source_line)
            if source.content:
                # Truncate long content
                content = source.content[:200] + "..." if len(source.content) > 200 else source.content
                output_lines.append(f"  _{content}_")
    
    # Add contradictions if any
    if verdict.contradictions:
        output_lines.append(f"\n**⚠️ Contradictions Found:**")
        for contradiction in verdict.contradictions:
            output_lines.append(f"• {contradiction}")
    
    # Add notes
    if verdict.notes:
        output_lines.append(f"\n**Notes:** {verdict.notes}")
    
    return "\n".join(output_lines)
