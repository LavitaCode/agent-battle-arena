"""FastAPI dependency providers for repositories and services."""
from functools import lru_cache
from pathlib import Path
from typing import List

import yaml

from .config import settings
from ..models import QuestCreate
from ..repositories.base import (
    AgentProfileRepository,
    PostMortemRepository,
    QuestRepository,
    RankingRepository,
    ReplayEventRepository,
    RunRepository,
)
from ..repositories.in_memory import (
    InMemoryAgentProfileRepository,
    InMemoryPostMortemRepository,
    InMemoryQuestRepository,
    InMemoryRankingRepository,
    InMemoryReplayEventRepository,
    InMemoryRunRepository,
)
from ..sandbox.runner import SandboxRunner
from ..services.alpha_store import AlphaStore
from ..services.public_alpha_service import PublicAlphaService
from ..services.quest_service import QuestService


def _quests_root() -> Path:
    return Path(__file__).resolve().parents[3] / "quests"


def get_quests_root() -> Path:
    """Return the local quests registry root path."""
    return _quests_root()


def _load_quest_definitions() -> List[QuestCreate]:
    """Load quest definitions from the local quests directory."""
    quest_definitions: List[QuestCreate] = []
    for quest_file in sorted(_quests_root().glob("*/quest.yaml")):
        with quest_file.open("r", encoding="utf-8") as handle:
            raw_data = yaml.safe_load(handle) or {}

        quest_id = raw_data.get("id") or quest_file.parent.name
        tests = raw_data.get("tests", [])
        quest_definitions.append(
            QuestCreate(
                id=quest_id,
                title=raw_data.get("title") or raw_data.get("name") or quest_id,
                description=raw_data.get("description", ""),
                difficulty=raw_data.get("difficulty", "bronze"),
                mode=raw_data.get("mode", "solo"),
                time_limit_minutes=raw_data.get("time_limit_minutes", 25),
                stack=raw_data.get("stack", {}),
                objective=raw_data.get("objective"),
                requirements=raw_data.get("requirements", []),
                forbidden_actions=raw_data.get("forbidden_actions", []),
                visible_tests=raw_data.get("visible_tests", []),
                hidden_tests=raw_data.get("hidden_tests", []),
                tests=tests,
                scoring_profile=raw_data.get("scoring_profile", "standard_app_build_v1"),
                instructions=(
                    f"Quest loaded from {quest_file.parent.relative_to(_quests_root())}."
                ),
            )
        )
    return quest_definitions


@lru_cache()
def get_quest_repository() -> QuestRepository:
    """Return a singleton quest repository seeded from local quest files."""
    return InMemoryQuestRepository(initial_quests=_load_quest_definitions())


@lru_cache()
def get_agent_profile_repository() -> AgentProfileRepository:
    """Return a singleton in-memory agent profile repository."""
    return InMemoryAgentProfileRepository()


@lru_cache()
def get_run_repository() -> RunRepository:
    """Return a singleton in-memory run repository."""
    return InMemoryRunRepository()


@lru_cache()
def get_replay_event_repository() -> ReplayEventRepository:
    """Return a singleton in-memory replay repository."""
    return InMemoryReplayEventRepository()


@lru_cache()
def get_post_mortem_repository() -> PostMortemRepository:
    """Return a singleton in-memory post-mortem repository."""
    return InMemoryPostMortemRepository()


@lru_cache()
def get_ranking_repository() -> RankingRepository:
    """Return a singleton in-memory ranking repository."""
    return InMemoryRankingRepository()


@lru_cache()
def get_sandbox_runner() -> SandboxRunner:
    """Return the sandbox runner used by the execution pipeline."""
    return SandboxRunner(_quests_root())


@lru_cache()
def get_alpha_store() -> AlphaStore:
    """Return the persistent store used by the public alpha battle flow."""
    return AlphaStore(settings.ALPHA_DB_PATH, settings.DATABASE_URL)


@lru_cache()
def get_public_alpha_service() -> PublicAlphaService:
    """Return the service orchestrating auth, profiles and battles."""
    return PublicAlphaService(get_alpha_store(), QuestService(get_quest_repository()), get_sandbox_runner())
