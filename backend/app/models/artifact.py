"""Pydantic models for run artifacts."""
from pydantic import BaseModel, ConfigDict, Field


class RunArtifact(BaseModel):
    """Metadata and content for a single run artifact."""

    name: str = Field(..., description="Artifact logical name")
    path: str = Field(..., description="Artifact filesystem path")
    content: str = Field(..., description="Artifact content")

    model_config = ConfigDict(from_attributes=True)
