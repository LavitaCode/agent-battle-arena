"""Version 1 of the API.

This module exposes a top‑level APIRouter that aggregates version 1 endpoints.
Currently it includes a health check endpoint and quest management endpoints.
"""
from secrets import compare_digest
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from ...core.config import settings
from ...core.dependencies import get_alpha_store, get_public_alpha_service
from ...core.metrics import snapshot_metrics
from ...core.rate_limit import enforce_rate_limit
from ...models import InviteValidationResponse, SessionUserResponse
from ...sandbox.runner import DockerSandboxProvider
from ...services.public_alpha_service import PublicAlphaService
from ...services.alpha_store import AlphaStore

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
def health_check(
    service: PublicAlphaService = Depends(get_public_alpha_service),
    store: AlphaStore = Depends(get_alpha_store),
) -> dict:
    """Return operational readiness details for uptime checks."""
    return _operational_snapshot(service, store)


@router.get("/admin/debug", summary="Admin Debug Snapshot", tags=["admin"])
def admin_debug(
    x_cqa_admin_token: Optional[str] = Header(default=None),
    service: PublicAlphaService = Depends(get_public_alpha_service),
    store: AlphaStore = Depends(get_alpha_store),
) -> dict:
    """Return a token-protected operational snapshot for alpha maintainers."""
    configured_token = settings.ADMIN_DEBUG_TOKEN
    if not configured_token or not x_cqa_admin_token or not compare_digest(
        configured_token,
        x_cqa_admin_token,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin debug access denied",
        )
    return _operational_snapshot(service, store, include_admin=True)


def _operational_snapshot(
    service: PublicAlphaService,
    store: AlphaStore,
    *,
    include_admin: bool = False,
) -> dict:
    storage = "postgres" if settings.DATABASE_URL.startswith(("postgres://", "postgresql://")) else "sqlite"
    payload = {
        "status": "ok",
        "storage": {
            "backend": storage,
            "schema_version": store.get_schema_version(),
        },
        "worker": {
            "pending_jobs": service.pending_battle_jobs(),
        },
        "metrics": snapshot_metrics(),
    }
    if include_admin:
        payload["sandbox"] = {
            "preferred_provider": settings.SANDBOX_PREFERRED_PROVIDER,
            "docker_image": settings.DOCKER_RUNNER_IMAGE,
            "docker_network": "none",
            "docker_hardening_flags": DockerSandboxProvider.hardening_flags,
            "allow_external_network": settings.ALLOW_EXTERNAL_NETWORK,
            "max_run_time_minutes": settings.MAX_RUN_TIME_MINUTES,
        }
        payload["limits"] = {
            "rate_limit_enabled": settings.RATE_LIMIT_ENABLED,
            "requests_per_minute": settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
            "auth_requests_per_minute": settings.RATE_LIMIT_AUTH_REQUESTS_PER_MINUTE,
            "max_workspace_files": settings.MAX_WORKSPACE_FILES,
            "max_workspace_file_bytes": settings.MAX_WORKSPACE_FILE_BYTES,
            "max_workspace_total_bytes": settings.MAX_WORKSPACE_TOTAL_BYTES,
        }
    return {
        **payload,
    }


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
    request: Request,
    service: PublicAlphaService = Depends(get_public_alpha_service),
):
    """Alias curto para validacao de invite do alpha."""
    enforce_rate_limit(request, "auth")
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
