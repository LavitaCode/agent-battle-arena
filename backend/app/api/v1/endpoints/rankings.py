"""API routes for quest rankings."""
from typing import List

from fastapi import APIRouter, Depends

from ....core.dependencies import get_ranking_repository
from ....models import RankingEntry
from ....repositories.base import RankingRepository
from ....services.ranking_service import RankingService


router = APIRouter()


@router.get("/quests/{quest_id}", response_model=List[RankingEntry], summary="Ranking por quest")
def list_quest_ranking(
    quest_id: str,
    repository: RankingRepository = Depends(get_ranking_repository),
):
    """Return local ranking entries for a quest."""
    service = RankingService(repository)
    return service.list_for_quest(quest_id)
