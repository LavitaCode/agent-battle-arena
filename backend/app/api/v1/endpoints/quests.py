"""API routes for managing quests."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from ....core.dependencies import get_quest_repository, get_quests_root
from ....models import Quest, QuestCreate, QuestStarterFile
from ....repositories.base import QuestRepository
from ....services.quest_service import QuestService
from ....services.starter_file_service import StarterFileService


router = APIRouter()


@router.get("/", response_model=List[Quest], summary="Listar todas as quests")
def list_quests(repository: QuestRepository = Depends(get_quest_repository)):
    """Return all available quests."""
    service = QuestService(repository)
    return service.list_quests()


@router.get("/{quest_id}", response_model=Quest, summary="Detalhar uma quest")
def get_quest(
    quest_id: str, repository: QuestRepository = Depends(get_quest_repository)
):
    """Return quest details."""
    service = QuestService(repository)
    quest = service.get_quest(quest_id)
    if quest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quest not found")
    return quest


@router.get(
    "/{quest_id}/starter-files",
    response_model=List[QuestStarterFile],
    summary="Listar arquivos starter de uma quest",
)
def list_quest_starter_files(
    quest_id: str, repository: QuestRepository = Depends(get_quest_repository)
):
    """Return starter files used to prefill local editing experiences."""
    quest_service = QuestService(repository)
    quest = quest_service.get_quest(quest_id)
    if quest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quest not found")

    service = StarterFileService(get_quests_root())
    return service.list_for_quest(quest_id)


@router.post("/", response_model=Quest, status_code=status.HTTP_201_CREATED, summary="Criar nova quest")
def create_quest(
    quest_in: QuestCreate, repository: QuestRepository = Depends(get_quest_repository)
):
    """Create a quest."""
    service = QuestService(repository)
    return service.create_quest(quest_in)
