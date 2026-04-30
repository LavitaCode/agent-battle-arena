"""Service class for run operations."""
from typing import List, Optional

from ..models import Run, RunCreate
from ..core.config import settings
from ..repositories.base import AgentProfileRepository, QuestRepository, RunRepository


class RunService:
    """Provide operations over run entities."""

    def __init__(
        self,
        run_repository: RunRepository,
        quest_repository: QuestRepository,
        profile_repository: AgentProfileRepository,
    ) -> None:
        self._run_repository = run_repository
        self._quest_repository = quest_repository
        self._profile_repository = profile_repository

    def list_runs(self) -> List[Run]:
        return self._run_repository.list()

    def get_run(self, run_id: str) -> Optional[Run]:
        return self._run_repository.get(run_id)

    def create_run(self, run_in: RunCreate) -> Run:
        if self._quest_repository.get(run_in.quest_id) is None:
            raise ValueError(f"Quest '{run_in.quest_id}' not found")
        profile = self._profile_repository.get(run_in.agent_profile_id)
        if profile is None:
            raise ValueError(f"Agent profile '{run_in.agent_profile_id}' not found")
        if profile.constraints.allow_external_network and not settings.ALLOW_EXTERNAL_NETWORK:
            raise ValueError("Agent profile requests external network access, which is forbidden")
        if profile.constraints.max_runtime_minutes > settings.MAX_RUN_TIME_MINUTES:
            raise ValueError(
                f"Agent profile runtime exceeds the local maximum of {settings.MAX_RUN_TIME_MINUTES} minutes"
            )
        return self._run_repository.create(run_in)

    def save_run(self, run: Run) -> Run:
        return self._run_repository.save(run)

    def get_quest_for_run(self, run: Run):
        return self._quest_repository.get(run.quest_id)

    def get_profile_for_run(self, run: Run):
        return self._profile_repository.get(run.agent_profile_id)
