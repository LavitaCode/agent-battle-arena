"""Service class for ranking operations."""
from typing import List

from ..models import RankingEntry
from ..repositories.base import RankingRepository


class RankingService:
    """Provide operations over rankings."""

    def __init__(self, repository: RankingRepository) -> None:
        self._repository = repository

    def list_for_quest(self, quest_id: str) -> List[RankingEntry]:
        return self._repository.list_for_quest(quest_id)
