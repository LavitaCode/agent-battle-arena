"""Service class for agent profile operations."""
from typing import List, Optional

from ..models import AgentProfile, AgentProfileCreate
from ..repositories.base import AgentProfileRepository


class AgentProfileService:
    """Provide operations over agent profile entities."""

    def __init__(self, repository: AgentProfileRepository) -> None:
        self._repository = repository

    def list_profiles(self) -> List[AgentProfile]:
        return self._repository.list()

    def get_profile(self, profile_id: str) -> Optional[AgentProfile]:
        return self._repository.get(profile_id)

    def create_profile(self, profile_in: AgentProfileCreate) -> AgentProfile:
        return self._repository.create(profile_in)
