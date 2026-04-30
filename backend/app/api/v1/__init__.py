"""Version 1 of the API.

This module exposes a top‑level APIRouter that aggregates version 1 endpoints.
Currently it includes a health check endpoint and quest management endpoints.
"""
from fastapi import APIRouter, Depends, Request

from ...core.config import settings
from ...core.dependencies import get_public_alpha_service
from ...models import InviteValidationResponse, SessionUserResponse
from ...services.public_alpha_service import PublicAlphaService

from .endpoints.auth import router as auth_router
from .endpoints.battles import router as battles_router
from .endpoints.leaderboard import router as leaderboard_router
from .endpoints.profiles import router as profiles_router
from .endpoints.quests import router as quests_router
from .endpoints.rankings import router as rankings_router
from .endpoints.runs import router as runs_router
from .endpoints.templates import router as templates_router

router = APIRouter()

@router.get("/health", summary="Health Check", tags=["health"])
def health_check() -> dict:
    """Return a simple status payload for uptime checks."""
    return {"status": "ok"}


@router.get("/me", response_model=SessionUserResponse, summary="Sessao atual", tags=["auth"])
def me(
    request: Request,
    service: PublicAlphaService = Depends(get_public_alpha_service),
):
    """Alias para o usuario autenticado no alpha."""
    token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    return service.get_session_user(token)


@router.get(
    "/invites/validate",
    response_model=InviteValidationResponse,
    summary="Validar invite",
    tags=["auth"],
)
def validate_invite_alias(
    code: str,
    github_login: str,
    service: PublicAlphaService = Depends(get_public_alpha_service),
):
    """Alias curto para validacao de invite do alpha."""
    return service.validate_invite(code, github_login)

# Mount quest routes under /quests
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(quests_router, prefix="/quests", tags=["quests"])
router.include_router(templates_router, prefix="/templates", tags=["templates"])
router.include_router(profiles_router, prefix="/profiles", tags=["profiles"])
router.include_router(runs_router, prefix="/runs", tags=["runs"])
router.include_router(battles_router, prefix="/battles", tags=["battles"])
router.include_router(leaderboard_router, prefix="/leaderboard", tags=["leaderboard"])
router.include_router(rankings_router, prefix="/rankings", tags=["rankings"])
