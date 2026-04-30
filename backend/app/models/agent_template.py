"""Pydantic models for public alpha agent templates."""
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field


class AgentTemplate(BaseModel):
    id: str = Field(..., description="Template identifier")
    name: str = Field(..., description="Template display name")
    archetype: str = Field(..., description="Template archetype")
    description: str = Field(..., description="Template description")
    recommended_for: List[str] = Field(default_factory=list, description="Recommended scenarios")
    locked_fields: List[str] = Field(default_factory=list, description="Locked profile fields")
    default_profile_payload: Dict[str, Any] = Field(
        default_factory=dict, description="Base payload used to create a profile"
    )
    editable_sections: List[str] = Field(
        default_factory=list, description="Profile sections editable by the user"
    )
    tips: List[str] = Field(default_factory=list, description="Template usage tips")

    model_config = ConfigDict(from_attributes=True)
