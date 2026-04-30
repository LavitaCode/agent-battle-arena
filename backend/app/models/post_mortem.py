"""Pydantic models for post-mortem entities."""
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class PostMortem(BaseModel):
    """Post-mortem generated after a run."""

    id: str = Field(..., description="Post-mortem identifier")
    run_id: str = Field(..., description="Run identifier")
    final_score: float = Field(..., description="Final run score")
    tests_passed: int = Field(..., description="Number of passed tests")
    tests_failed: int = Field(..., description="Number of failed tests")
    claude_analysis: str = Field(..., description="Narrative analysis")
    strengths: List[str] = Field(default_factory=list, description="Positive aspects")
    failures: List[str] = Field(default_factory=list, description="Main failures")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")

    model_config = ConfigDict(from_attributes=True)
