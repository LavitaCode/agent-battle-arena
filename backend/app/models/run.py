"""Pydantic models for run entities."""
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RunSuiteResult(BaseModel):
    suite: str = Field(..., description="Suite identifier")
    passed: int = Field(0, description="Number of passed tests")
    failed: int = Field(0, description="Number of failed tests")
    duration_ms: Optional[int] = Field(None, description="Suite duration in milliseconds")


class RunSummary(BaseModel):
    technical_score: float = Field(0.0, description="Technical score for the run")
    total_score: float = Field(0.0, description="Total score for the run")
    duration_ms: Optional[int] = Field(None, description="Total duration in milliseconds")
    suites: List[RunSuiteResult] = Field(
        default_factory=list, description="Recorded test suite results"
    )
    notes: List[str] = Field(default_factory=list, description="Summary notes")
    artifacts: Dict[str, str] = Field(default_factory=dict, description="Execution artifacts")


class RunBase(BaseModel):
    quest_id: str = Field(..., description="Quest identifier")
    agent_profile_id: str = Field(..., description="Agent profile identifier")
    workspace_files: Dict[str, str] = Field(
        default_factory=dict,
        description="Workspace file overrides applied before execution",
    )


class RunCreate(RunBase):
    pass


class Run(RunBase):
    id: str = Field(..., description="Run identifier")
    status: str = Field(..., description="Run status")
    sandbox_id: Optional[str] = Field(None, description="Sandbox identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    summary: RunSummary = Field(default_factory=RunSummary, description="Run summary")

    model_config = ConfigDict(from_attributes=True)
