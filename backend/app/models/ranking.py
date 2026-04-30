"""Pydantic models for ranking entities."""
from pydantic import BaseModel, ConfigDict, Field


class RankingEntry(BaseModel):
    """A single ranking entry for a quest."""

    quest_id: str = Field(..., description="Quest identifier")
    run_id: str = Field(..., description="Run identifier")
    agent_profile_id: str = Field(..., description="Agent profile identifier")
    score: float = Field(..., description="Technical score")
    completed_runs: int = Field(..., description="Number of completed runs for the profile")

    model_config = ConfigDict(from_attributes=True)
