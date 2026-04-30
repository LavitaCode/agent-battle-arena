"""Service class for post-mortem operations."""
from typing import Optional

from ..models import PostMortem
from ..repositories.base import PostMortemRepository


class PostMortemService:
    """Provide operations over post-mortems."""

    def __init__(self, repository: PostMortemRepository) -> None:
        self._repository = repository

    def get_for_run(self, run_id: str) -> Optional[PostMortem]:
        return self._repository.get_by_run(run_id)
