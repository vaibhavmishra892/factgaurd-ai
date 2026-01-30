from pydantic import BaseModel, Field
from typing import List, Literal

class ClaimInput(BaseModel):
    """User's factual claim to be verified"""
    claim: str = Field(..., description="The factual claim to verify")

class RoutingDecision(BaseModel):
    """Structured output from Planner Agent"""
    intent: Literal["finance", "news", "events", "mixed", "general"] = Field(
        ..., 
        description="Primary domain of the claim"
    )
    time_sensitive: bool = Field(
        ..., 
        description="Whether the claim involves recent events or data"
    )
    required_agents: List[str] = Field(
        ..., 
        description="List of agent names to invoke (e.g., ['finance_agent', 'news_agent'])"
    )
    reasoning: str = Field(
        ..., 
        description="Brief explanation of routing decision"
    )

class EvidenceSource(BaseModel):
    """Information about a single source of evidence"""
    source_name: str = Field(..., description="Name of the source (e.g., 'Reuters', 'Alpha Vantage')")
    source_type: str = Field(..., description="Type of source (e.g., 'News', 'Market Data', 'Search')")
    content: str = Field(..., description="Relevant excerpt or data")
    url: str | None = Field(default=None, description="URL to the source if available")
    date: str | None = Field(default=None, description="Publication or data date")
    credibility: str = Field(default="Unknown", description="Source credibility assessment")
