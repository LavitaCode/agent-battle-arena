"""Leaderboard endpoints for the public alpha."""
from fastapi import APIRouter, Depends

from ....core.dependencies import get_public_alpha_service
from ....models import LeaderboardEntry
from ....services.public_alpha_service import PublicAlphaService


router = APIRouter()


@router.get("/", response_model=list[LeaderboardEntry], summary="Leaderboard do alpha")
def list_leaderboard(
    service: PublicAlphaService = Depends(get_public_alpha_service),
):
    """Return public alpha standings aggregated from completed battles."""
    return service.list_leaderboard()
