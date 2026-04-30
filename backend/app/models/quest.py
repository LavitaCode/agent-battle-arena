"""Pydantic models for quest entities."""
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class QuestTestRequest(BaseModel):
    method: str = Field(..., description="HTTP method used by the test request")
    path: str = Field(..., description="Path used by the test request")


class QuestExpectedResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status_code: Optional[int] = Field(None, description="Expected HTTP status code")
    expected_json: Optional[Dict[str, str]] = Field(
        None, alias="json", serialization_alias="json", description="Expected JSON payload"
    )


class QuestTestDefinition(BaseModel):
    description: str = Field(..., description="Human-readable test description")
    type: str = Field(..., description="Quest test type")
    request: QuestTestRequest = Field(..., description="Request definition")
    expected_response: Optional[QuestExpectedResponse] = Field(
        None, description="Expected response payload"
    )
    expected_headers: Optional[Dict[str, str]] = Field(
        None, description="Expected response headers"
    )


class QuestStack(BaseModel):
    backend: Optional[str] = Field(None, description="Preferred backend stack")
    frontend: Optional[str] = Field(None, description="Preferred frontend stack")
    database: Optional[str] = Field(None, description="Preferred database stack")


class QuestBase(BaseModel):
    title: str = Field(..., description="Quest title")
    description: str = Field(..., description="Quest description")
    difficulty: str = Field("bronze", description="Quest difficulty")
    mode: str = Field("solo", description="Quest mode")
    time_limit_minutes: int = Field(25, description="Time limit in minutes")
    stack: QuestStack = Field(default_factory=QuestStack, description="Target stack")
    objective: Optional[str] = Field(None, description="Quest objective")
    requirements: List[str] = Field(default_factory=list, description="Quest requirements")
    forbidden_actions: List[str] = Field(
        default_factory=list, description="Forbidden actions during execution"
    )
    visible_tests: List[str] = Field(
        default_factory=list, description="Paths for visible test suites"
    )
    hidden_tests: List[str] = Field(
        default_factory=list, description="Paths for hidden test suites"
    )
    tests: List[QuestTestDefinition] = Field(
        default_factory=list, description="Structured test definitions"
    )
    scoring_profile: str = Field(
        "standard_app_build_v1", description="Scoring profile identifier"
    )
    instructions: Optional[str] = Field(
        None, description="Additional quest instructions for the competitor"
    )


class QuestCreate(QuestBase):
    id: str = Field(..., description="Unique quest identifier")


class Quest(QuestBase):
    id: str = Field(..., description="Unique quest identifier")

    model_config = ConfigDict(from_attributes=True)
