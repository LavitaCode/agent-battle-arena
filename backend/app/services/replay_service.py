"""Service class for replay operations."""
from typing import List

from ..models import ReplayEvent
from ..repositories.base import ReplayEventRepository


class ReplayService:
    """Provide operations over replay events."""

    def __init__(self, repository: ReplayEventRepository) -> None:
        self._repository = repository

    def list_events(self, run_id: str) -> List[ReplayEvent]:
        return self._repository.list_by_run(run_id)
