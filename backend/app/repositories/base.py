"""Abstract base classes for repository patterns."""
from abc import ABC, abstractmethod
from typing import List, Optional

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


class QuestRepository(ABC):
    """Abstract repository interface for quest entities."""

    @abstractmethod
    def list(self) -> List[Quest]:
        """Return all quests."""

    @abstractmethod
    def get(self, quest_id: str) -> Optional[Quest]:
        """Retrieve a quest by its ID."""

    @abstractmethod
    def create(self, quest_in: QuestCreate) -> Quest:
        """Persist a new quest."""


class AgentProfileRepository(ABC):
    """Abstract repository interface for agent profiles."""

    @abstractmethod
    def list(self) -> List[AgentProfile]:
        """Return all agent profiles."""

    @abstractmethod
    def get(self, profile_id: str) -> Optional[AgentProfile]:
        """Retrieve a profile by its ID."""

    @abstractmethod
    def create(self, profile_in: AgentProfileCreate) -> AgentProfile:
        """Persist a new agent profile."""


class RunRepository(ABC):
    """Abstract repository interface for runs."""

    @abstractmethod
    def list(self) -> List[Run]:
        """Return all runs."""

    @abstractmethod
    def get(self, run_id: str) -> Optional[Run]:
        """Retrieve a run by its ID."""

    @abstractmethod
    def create(self, run_in: RunCreate) -> Run:
        """Persist a new run."""

    @abstractmethod
    def save(self, run: Run) -> Run:
        """Persist an updated run."""


class ReplayEventRepository(ABC):
    """Abstract repository interface for replay events."""

    @abstractmethod
    def list_by_run(self, run_id: str) -> List[ReplayEvent]:
        """Return all replay events for a run."""

    @abstractmethod
    def create_many(self, events: List[ReplayEvent]) -> List[ReplayEvent]:
        """Persist a list of replay events."""


class PostMortemRepository(ABC):
    """Abstract repository interface for post-mortems."""

    @abstractmethod
    def get_by_run(self, run_id: str) -> Optional[PostMortem]:
        """Return the post-mortem for a run if present."""

    @abstractmethod
    def save(self, post_mortem: PostMortem) -> PostMortem:
        """Persist a post-mortem."""


class RankingRepository(ABC):
    """Abstract repository interface for quest rankings."""

    @abstractmethod
    def record(self, entry: RankingEntry) -> RankingEntry:
        """Persist or replace a ranking entry."""

    @abstractmethod
    def list_for_quest(self, quest_id: str) -> List[RankingEntry]:
        """List ranking entries for a quest."""
