"""Battle endpoints for the public alpha."""
from fastapi import APIRouter, Depends, HTTPException, Request, status

from ....core.config import settings
from ....core.dependencies import get_public_alpha_service
from ....models import (
    BattleCreate,
    BattleDetail,
    BattleJoin,
    BattleParticipantSubmission,
    BattleReplayBundle,
    BattleResult,
)
from ....services.public_alpha_service import PublicAlphaService


router = APIRouter()


def _require_user(request: Request, service: PublicAlphaService):
    session = service.get_session_user(request.cookies.get(settings.SESSION_COOKIE_NAME))
    if not session.authenticated or session.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return session.user


@router.get("/", response_model=list[BattleDetail], summary="Listar battles")
def list_battles(
    service: PublicAlphaService = Depends(get_public_alpha_service),
):
    """Return public alpha battles with their participant state."""
    return [service.get_battle_detail(battle.id) for battle in service.list_battles()]


@router.post("/", response_model=BattleDetail, status_code=status.HTTP_201_CREATED, summary="Criar battle")
def create_battle(
    battle_in: BattleCreate,
    request: Request,
    service: PublicAlphaService = Depends(get_public_alpha_service),
):
    """Create a new async 1v1 battle."""
    user = _require_user(request, service)
    try:
        return service.create_battle(user, battle_in)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{battle_id}", response_model=BattleDetail, summary="Detalhar battle")
def get_battle(
    battle_id: str,
    service: PublicAlphaService = Depends(get_public_alpha_service),
):
    """Return the current state of a public alpha battle."""
    try:
        return service.get_battle_detail(battle_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{battle_id}/join", response_model=BattleDetail, summary="Entrar em battle")
def join_battle(
    battle_id: str,
    battle_in: BattleJoin,
    request: Request,
    service: PublicAlphaService = Depends(get_public_alpha_service),
):
    """Join an existing battle with a selected agent profile."""
    user = _require_user(request, service)
    try:
        return service.join_battle(battle_id, user, battle_in)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{battle_id}/submit", response_model=BattleDetail, summary="Submeter workspace")
def submit_battle(
    battle_id: str,
    submission: BattleParticipantSubmission,
    request: Request,
    service: PublicAlphaService = Depends(get_public_alpha_service),
):
    """Submit or replace the workspace payload for the authenticated participant."""
    user = _require_user(request, service)
    try:
        return service.submit_for_battle(battle_id, user, submission)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{battle_id}/start", response_model=BattleDetail, summary="Iniciar battle")
def start_battle(
    battle_id: str,
    request: Request,
    service: PublicAlphaService = Depends(get_public_alpha_service),
):
    """Queue a battle for execution and return immediately for polling."""
    user = _require_user(request, service)
    try:
        return service.start_battle(battle_id, user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{battle_id}/result", response_model=BattleResult, summary="Resultado da battle")
def get_battle_result(
    battle_id: str,
    service: PublicAlphaService = Depends(get_public_alpha_service),
):
    """Return the consolidated 1v1 result when available."""
    try:
        return service.get_battle_result(battle_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{battle_id}/replay", response_model=BattleReplayBundle, summary="Replay da battle")
def get_battle_replay(
    battle_id: str,
    service: PublicAlphaService = Depends(get_public_alpha_service),
):
    """Return replay, post-mortem and run bundles for both participants."""
    return service.get_battle_replay(battle_id)
