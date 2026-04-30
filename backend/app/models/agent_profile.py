"""Pydantic models for agent profile entities."""
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AgentProfileLimits(BaseModel):
    max_files_edited: int = Field(25, description="Maximum number of files that may be edited")
    max_runs: int = Field(10, description="Maximum execution attempts")


class AgentProfileConstraints(BaseModel):
    allow_dependency_install: bool = Field(
        True, description="Whether dependency installation is allowed"
    )
    allow_external_network: bool = Field(
        False, description="Whether external network access is allowed"
    )
    allow_schema_change: bool = Field(
        True, description="Whether schema changes are allowed"
    )
    max_runtime_minutes: int = Field(20, description="Maximum runtime in minutes")


class AgentProfileMemory(BaseModel):
    slots: List[str] = Field(default_factory=list, description="Memory prompts for the agent")


class AgentProfileBase(BaseModel):
    name: str = Field(..., description="Profile display name")
    archetype: str = Field(..., description="Agent archetype")
    planning_style: str = Field(..., description="Primary planning strategy")
    preferred_stack: List[str] = Field(
        default_factory=list, description="Preferred technology stack"
    )
    engineering_principles: List[str] = Field(
        default_factory=list, description="Engineering principles"
    )
    modules: List[str] = Field(default_factory=list, description="Enabled modules")
    constraints: AgentProfileConstraints = Field(
        default_factory=AgentProfileConstraints, description="Execution constraints"
    )
    memory: AgentProfileMemory = Field(
        default_factory=AgentProfileMemory, description="Persistent agent memory"
    )
    limits: AgentProfileLimits = Field(
        default_factory=AgentProfileLimits, description="Operational limits"
    )
    owner_user_id: Optional[str] = Field(None, description="Owning user identifier")
    template_id: Optional[str] = Field(None, description="Template used as the base profile")
    visibility: str = Field("private", description="Visibility level for the profile")
    version: int = Field(1, description="Profile version")


class AgentProfileCreate(AgentProfileBase):
    id: str = Field(..., description="Unique profile identifier")


class AgentProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Profile display name")
    planning_style: Optional[str] = Field(None, description="Primary planning strategy")
    preferred_stack: Optional[List[str]] = Field(None, description="Preferred technology stack")
    engineering_principles: Optional[List[str]] = Field(None, description="Engineering principles")
    modules: Optional[List[str]] = Field(None, description="Enabled modules")
    memory: Optional[AgentProfileMemory] = Field(None, description="Persistent agent memory")
    visibility: Optional[str] = Field(None, description="Visibility level for the profile")
    version: Optional[int] = Field(None, description="Explicit version override")


class AgentProfile(AgentProfileBase):
    id: str = Field(..., description="Unique profile identifier")

    model_config = ConfigDict(from_attributes=True)
