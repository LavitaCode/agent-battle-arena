"""Pydantic models for quest starter files."""
from pydantic import BaseModel, Field


class QuestStarterFile(BaseModel):
    """Represents a starter file exposed to local editors."""

    path: str = Field(..., description="Path relative to the quest starter directory")
    content: str = Field(..., description="UTF-8 content of the starter file")
