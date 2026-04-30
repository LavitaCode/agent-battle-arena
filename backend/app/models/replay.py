"""Pydantic models for replay events."""
from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field


class ReplayEvent(BaseModel):
    """A single event recorded during a run."""

    id: str = Field(..., description="Event identifier")
    run_id: str = Field(..., description="Run identifier")
    type: str = Field(..., description="Event type")
    message: str = Field(..., description="Human-readable event message")
    timestamp: datetime = Field(..., description="Timestamp for the event")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Structured event payload")

    model_config = ConfigDict(from_attributes=True)
