"""In-memory repository implementations."""
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .base import (
    AgentProfileRepository,
    PostMortemRepository,
    QuestRepository,
    RankingRepository,
    ReplayEventRepository,
    RunRepository,
)
from ..models import (
    AgentProfile,
    AgentProfileCreate,
    PostMortem,
    Quest,
    QuestCreate,
    RankingEntry,
    ReplayEvent,
    Run,
    RunCreate,
)


class InMemoryQuestRepository(QuestRepository):
    """Simple in-memory repository for quests."""

    def __init__(self, initial_quests: Optional[List[QuestCreate]] = None) -> None:
        self._storage: Dict[str, Quest] = {}
        for quest_in in initial_quests or []:
            self.create(quest_in)

    def list(self) -> List[Quest]:
        return list(self._storage.values())

    def get(self, quest_id: str) -> Optional[Quest]:
        return self._storage.get(quest_id)

    def create(self, quest_in: QuestCreate) -> Quest:
        quest = Quest(**quest_in.model_dump())
        self._storage[quest.id] = quest
        return quest


class InMemoryAgentProfileRepository(AgentProfileRepository):
    """Simple in-memory repository for agent profiles."""

    def __init__(self) -> None:
        self._storage: Dict[str, AgentProfile] = {}

    def list(self) -> List[AgentProfile]:
        return list(self._storage.values())

    def get(self, profile_id: str) -> Optional[AgentProfile]:
        return self._storage.get(profile_id)

    def create(self, profile_in: AgentProfileCreate) -> AgentProfile:
        profile = AgentProfile(**profile_in.model_dump())
        self._storage[profile.id] = profile
        return profile


class InMemoryRunRepository(RunRepository):
    """Simple in-memory repository for runs."""

    def __init__(self) -> None:
        self._storage: Dict[str, Run] = {}
        self._counter = 0

    def list(self) -> List[Run]:
        return list(self._storage.values())

    def get(self, run_id: str) -> Optional[Run]:
        return self._storage.get(run_id)

    def create(self, run_in: RunCreate) -> Run:
        self._counter += 1
        now = datetime.now(timezone.utc)
        run = Run(
            id=f"run-{self._counter}",
            status="created",
            sandbox_id=None,
            created_at=now,
            updated_at=now,
            **run_in.model_dump(),
        )
        self._storage[run.id] = run
        return run

    def save(self, run: Run) -> Run:
        self._storage[run.id] = run
        return run


class InMemoryReplayEventRepository(ReplayEventRepository):
    """Simple in-memory repository for replay events."""

    def __init__(self) -> None:
        self._storage: Dict[str, List[ReplayEvent]] = {}

    def list_by_run(self, run_id: str) -> List[ReplayEvent]:
        return list(self._storage.get(run_id, []))

    def create_many(self, events: List[ReplayEvent]) -> List[ReplayEvent]:
        for event in events:
            self._storage.setdefault(event.run_id, []).append(event)
        return events


class InMemoryPostMortemRepository(PostMortemRepository):
    """Simple in-memory repository for post-mortems."""

    def __init__(self) -> None:
        self._storage: Dict[str, PostMortem] = {}

    def get_by_run(self, run_id: str) -> Optional[PostMortem]:
        return self._storage.get(run_id)

    def save(self, post_mortem: PostMortem) -> PostMortem:
        self._storage[post_mortem.run_id] = post_mortem
        return post_mortem


class InMemoryRankingRepository(RankingRepository):
    """Simple in-memory repository for quest rankings."""

    def __init__(self) -> None:
        self._storage: Dict[str, Dict[str, RankingEntry]] = {}

    def record(self, entry: RankingEntry) -> RankingEntry:
        current = self._storage.setdefault(entry.quest_id, {}).get(entry.agent_profile_id)
        if current is None or entry.score >= current.score:
            self._storage[entry.quest_id][entry.agent_profile_id] = entry
        return entry

    def list_for_quest(self, quest_id: str) -> List[RankingEntry]:
        entries = list(self._storage.get(quest_id, {}).values())
        return sorted(entries, key=lambda item: (-item.score, item.completed_runs, item.agent_profile_id))
