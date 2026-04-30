"""Authentication endpoints for the closed alpha."""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from typing import Optional

from ....core.config import settings
from ....core.dependencies import get_public_alpha_service
from ....models import (
    AuthStartRequest,
    AuthStartResponse,
    InviteValidationResponse,
    SessionUserResponse,
)
from ....services.public_alpha_service import PublicAlphaService


router = APIRouter()


@router.post("/github/start", response_model=AuthStartResponse, summary="Iniciar login do alpha")
def start_github_auth(
    payload: AuthStartRequest,
    service: PublicAlphaService = Depends(get_public_alpha_service),
):
    """Start GitHub OAuth or the local mock auth flow."""
    try:
        state, authorization_url = service.start_auth(payload.github_login, payload.invite_code)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return AuthStartResponse(state=state, authorization_url=authorization_url)


@router.get("/github/callback", response_model=SessionUserResponse, summary="Finalizar login do alpha")
def github_callback(
    state: str,
    response: Response,
    github_login: Optional[str] = None,
    code: Optional[str] = None,
    service: PublicAlphaService = Depends(get_public_alpha_service),
):
    """Complete GitHub OAuth or the local mock callback and create a session cookie."""
    try:
        user, token = service.finish_auth(state, github_login=github_login, code=code)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=settings.SESSION_TTL_HOURS * 3600,
    )
    return SessionUserResponse(authenticated=True, user=user)


@router.get("/me", response_model=SessionUserResponse, summary="Usuario autenticado")
def get_me(
    request: Request,
    service: PublicAlphaService = Depends(get_public_alpha_service),
):
    """Return the authenticated alpha user when a session cookie is present."""
    token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    return service.get_session_user(token)


@router.get("/invites/validate", response_model=InviteValidationResponse, summary="Validar invite")
def validate_invite(
    code: str,
    github_login: str,
    service: PublicAlphaService = Depends(get_public_alpha_service),
):
    """Validate whether the invite can be used by a GitHub login."""
    return service.validate_invite(code, github_login)
