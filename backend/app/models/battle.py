"""Pydantic models for public alpha battles."""
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .post_mortem import PostMortem
from .replay import ReplayEvent
from .run import Run


class BattleParticipantBase(BaseModel):
    agent_profile_id: str = Field(..., description="Selected agent profile")
    workspace_files: Dict[str, str] = Field(
        default_factory=dict,
        description="Workspace overrides submitted for this participant",
    )


class BattleParticipantSubmission(BaseModel):
    workspace_files: Dict[str, str] = Field(
        default_factory=dict,
        description="Workspace overrides submitted for this participant",
    )


class BattleCreate(BaseModel):
    quest_id: str = Field(..., description="Quest selected for the battle")
    agent_profile_id: str = Field(..., description="Profile used by the creator")
    workspace_files: Dict[str, str] = Field(
        default_factory=dict,
        description="Optional first submission payload for the creator",
    )


class BattleJoin(BattleParticipantBase):
    pass


class BattleParticipant(BaseModel):
    id: str = Field(..., description="Participant identifier")
    battle_id: str = Field(..., description="Battle identifier")
    user_id: str = Field(..., description="Owning user identifier")
    agent_profile_id: str = Field(..., description="Agent profile identifier")
    seat: str = Field(..., description="Seat within the battle")
    submission_status: str = Field(..., description="Submission readiness state")
    workspace_files: Dict[str, str] = Field(default_factory=dict, description="Submitted workspace")
    run_id: Optional[str] = Field(None, description="Resulting run identifier")
    joined_at: datetime = Field(..., description="Join timestamp")

    model_config = ConfigDict(from_attributes=True)


class Battle(BaseModel):
    id: str = Field(..., description="Battle identifier")
    quest_id: str = Field(..., description="Quest identifier")
    status: str = Field(..., description="Battle status")
    created_by_user_id: str = Field(..., description="Creator user identifier")
    battle_type: str = Field("async_1v1", description="Battle mode")
    created_at: datetime = Field(..., description="Creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    finished_at: Optional[datetime] = Field(None, description="Finish timestamp")

    model_config = ConfigDict(from_attributes=True)


class BattleResult(BaseModel):
    battle_id: str = Field(..., description="Battle identifier")
    winner_participant_id: Optional[str] = Field(None, description="Winner participant identifier")
    score_left: float = Field(..., description="Left seat technical score")
    score_right: float = Field(..., description="Right seat technical score")
    tie_break_reason: str = Field(..., description="Tie-break explanation")
    summary: str = Field(..., description="Human-readable summary")

    model_config = ConfigDict(from_attributes=True)


class BattleRunBundle(BaseModel):
    participant_id: str = Field(..., description="Participant identifier")
    run: Run = Field(..., description="Executed run")
    replay: List[ReplayEvent] = Field(default_factory=list, description="Replay events")
    post_mortem: PostMortem = Field(..., description="Post-mortem payload")


class BattleDetail(BaseModel):
    battle: Battle = Field(..., description="Battle core payload")
    participants: List[BattleParticipant] = Field(default_factory=list, description="Participants")
    result: Optional[BattleResult] = Field(None, description="Battle result when available")


class BattleReplayBundle(BaseModel):
    battle_id: str = Field(..., description="Battle identifier")
    runs: List[BattleRunBundle] = Field(default_factory=list, description="Run bundles for both seats")


class LeaderboardEntry(BaseModel):
    user_id: str = Field(..., description="User identifier")
    github_login: str = Field(..., description="Public GitHub login")
    display_name: str = Field(..., description="Display name")
    wins: int = Field(0, description="Completed wins")
    losses: int = Field(0, description="Completed losses")
    ties: int = Field(0, description="Completed ties")
    best_score: float = Field(0.0, description="Best technical score across battles")

    model_config = ConfigDict(from_attributes=True)
