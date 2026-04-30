"""API routes for managing agent profiles."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ....core.config import settings
from ....core.dependencies import get_agent_profile_repository, get_public_alpha_service
from ....models import AgentProfile, AgentProfileCreate, AgentProfileUpdate
from ....repositories.base import AgentProfileRepository
from ....services.agent_profile_service import AgentProfileService
from ....services.public_alpha_service import PublicAlphaService


router = APIRouter()


def _get_optional_user(request: Request, service: PublicAlphaService):
    session = service.get_session_user(request.cookies.get(settings.SESSION_COOKIE_NAME))
    return session.user


@router.get("/", response_model=List[AgentProfile], summary="Listar profiles")
def list_profiles(
    repository: AgentProfileRepository = Depends(get_agent_profile_repository),
):
    """Return all agent profiles."""
    service = AgentProfileService(repository)
    return service.list_profiles()


@router.get("/mine", response_model=List[AgentProfile], summary="Listar meus profiles")
def list_my_profiles(
    request: Request,
    alpha_service: PublicAlphaService = Depends(get_public_alpha_service),
):
    """Return the authenticated user's alpha profiles."""
    user = _get_optional_user(request, alpha_service)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return alpha_service.list_profiles_for_user(user)


@router.get("/{profile_id}", response_model=AgentProfile, summary="Detalhar profile")
def get_profile(
    profile_id: str,
    repository: AgentProfileRepository = Depends(get_agent_profile_repository),
):
    """Return a single agent profile."""
    service = AgentProfileService(repository)
    profile = service.get_profile(profile_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.post("/", response_model=AgentProfile, status_code=status.HTTP_201_CREATED, summary="Criar profile")
def create_profile(
    profile_in: AgentProfileCreate,
    request: Request,
    repository: AgentProfileRepository = Depends(get_agent_profile_repository),
    alpha_service: PublicAlphaService = Depends(get_public_alpha_service),
):
    """Create a new agent profile."""
    user = _get_optional_user(request, alpha_service)
    if user is not None:
        try:
            return alpha_service.create_profile_from_payload(user, profile_in)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    service = AgentProfileService(repository)
    return service.create_profile(profile_in)


@router.patch("/{profile_id}", response_model=AgentProfile, summary="Atualizar profile")
def update_profile(
    profile_id: str,
    profile_in: AgentProfileUpdate,
    request: Request,
    alpha_service: PublicAlphaService = Depends(get_public_alpha_service),
):
    """Patch an authenticated user's profile."""
    user = _get_optional_user(request, alpha_service)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        return alpha_service.update_profile(profile_id, user, profile_in)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
