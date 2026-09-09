from typing import List, Optional
from pydantic import BaseModel, Field


class AIAnalysisOutput(BaseModel):
    """
    Schema representing the structured AI bug triage analysis.
    In Phase 1, this validates the mock AI response.
    In Phase 2, this validates the Grok model's structured JSON output.
    """

    id: Optional[int] = Field(
        default=None,
        description="Database primary key ID assigned upon persistence.",
    )
    summary: str = Field(
        ...,
        description="Clear, concise one-sentence bug summary.",
    )
    severity: str = Field(
        ...,
        description="Assessed severity level (Critical, High, Medium, Low).",
    )
    priority: str = Field(
        ...,
        description="Action priority (e.g., P1, P2, P3, P4).",
    )
    impact: str = Field(
        ...,
        description="User or business impact analysis.",
    )
    steps_to_reproduce: List[str] = Field(
        ...,
        description="Step-by-step reproduction instructions.",
    )
    affected_component: str = Field(
        ...,
        description="System component or module affected.",
    )
    entities: List[str] = Field(
        ...,
        description="Named technical entities, UI elements, or services involved.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="AI confidence score between 0.0 and 1.0.",
    )
    processing_status: Optional[str] = Field(
        default="completed",
        description="Status of the triage job ('completed', 'failed', 'pending').",
    )
