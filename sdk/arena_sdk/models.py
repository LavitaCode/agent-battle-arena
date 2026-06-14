"""Lightweight dataclasses mirroring the Arena API response shapes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Battle:
    id: str
    quest_id: str
    status: str
    created_by_user_id: str
    raw: dict = field(default_factory=dict, repr=False)


@dataclass
class BattleResult:
    battle_id: str
    winner_participant_id: Optional[str]
    score_left: float
    score_right: float
    summary: str
    raw: dict = field(default_factory=dict, repr=False)


@dataclass
class Quest:
    id: str
    title: str
    difficulty: str
    cognitive_layers: list[str] = field(default_factory=list)
    raw: dict = field(default_factory=dict, repr=False)
