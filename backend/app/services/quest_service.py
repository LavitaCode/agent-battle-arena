"""Service class for quest operations."""
from typing import List, Optional

from ..models import Quest, QuestCreate
from ..repositories.base import QuestRepository


class QuestService:
    """Provide operations over quest entities."""

    def __init__(self, repository: QuestRepository) -> None:
        self._repository = repository

    def list_quests(self) -> List[Quest]:
        return self._repository.list()

    def get_quest(self, quest_id: str) -> Optional[Quest]:
        return self._repository.get(quest_id)

    def create_quest(self, quest_in: QuestCreate) -> Quest:
        return self._repository.create(quest_in)
