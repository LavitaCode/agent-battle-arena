#!/bin/bash
set -e

# This script populates the backend directory with a minimal FastAPI application
# and then invokes the frontend setup script.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Setting up backend skeleton..."

# Create main application file
cat <<'MAINPY' > "$ROOT_DIR/backend/app/main.py"
"""Entry point for the FastAPI application.

This file configures a basic FastAPI instance and includes a versioned API router.
"""
from fastapi import FastAPI

from .api.v1 import router as api_v1_router


def get_application() -> FastAPI:
    """Create and configure a FastAPI application instance.

    Returns:
        FastAPI: The configured application.
    """
    application = FastAPI(title="Agent Battle Arena API")
    application.include_router(api_v1_router, prefix="/api/v1")
    return application


app = get_application()

MAINPY

# Create API package with a simple health endpoint and include quest routes
cat <<'INITPY' > "$ROOT_DIR/backend/app/api/v1/__init__.py"
"""Version 1 of the API.

This module exposes a top‑level APIRouter that aggregates version 1 endpoints.
Currently it includes a health check endpoint and quest management endpoints.
"""
from fastapi import APIRouter

from .endpoints.quests import router as quests_router

router = APIRouter()

@router.get("/health", summary="Health Check", tags=["health"])
def health_check() -> dict:
    """Return a simple status payload for uptime checks."""
    return {"status": "ok"}

# Mount quest routes under /quests
router.include_router(quests_router, prefix="/quests", tags=["quests"])

INITPY

# Core configuration file
cat <<'CONFIGPY' > "$ROOT_DIR/backend/app/core/config.py"
"""Configuration settings for the FastAPI application.

This module defines simple configuration classes. In a real project you might
pull settings from environment variables or a .env file using Pydantic's
BaseSettings.
"""

class Settings:
    """Application configuration with sensible defaults."""

    PROJECT_NAME: str = "Agent Battle Arena"
    API_V1_PREFIX: str = "/api/v1"


settings = Settings()

CONFIGPY

echo "Backend skeleton created."
###############################
# Additional backend structure
###############################

# Create directories for models, repositories, services and endpoints
mkdir -p "$ROOT_DIR/backend/app/models"
mkdir -p "$ROOT_DIR/backend/app/repositories"
mkdir -p "$ROOT_DIR/backend/app/services"
mkdir -p "$ROOT_DIR/backend/app/api/v1/endpoints"

# Pydantic models for Quest entities
cat <<'QUEST_MODEL_PY' > "$ROOT_DIR/backend/app/models/quest.py"
"""Pydantic models for Quest objects.

The `QuestBase` model defines shared attributes used for both reading and
creating quests. The `QuestCreate` model is used when a new quest is
submitted, and the `Quest` model includes an ID field for reading from
storage.
"""
from pydantic import BaseModel, Field


class QuestBase(BaseModel):
    name: str = Field(..., description="Nome do desafio")
    description: str = Field(..., description="Descrição do desafio")


class QuestCreate(QuestBase):
    pass


class Quest(QuestBase):
    id: int = Field(..., description="Identificador único do desafio")

    class Config:
        orm_mode = True

QUEST_MODEL_PY

cat <<'QUEST_MODELS_INIT' > "$ROOT_DIR/backend/app/models/__init__.py"
"""Export quest models from the models package."""
from .quest import Quest, QuestBase, QuestCreate  # noqa: F401
QUEST_MODELS_INIT

# Repository pattern: base and in-memory implementations
cat <<'REPO_BASE_PY' > "$ROOT_DIR/backend/app/repositories/base.py"
"""Abstract base classes for repository patterns.

Defines interfaces for retrieving and persisting Quest objects. Concrete
implementations can be provided for different storage backends (e.g. SQL,
in‑memory, or external services). This promotes separation of concerns and
adheres to the Dependency Inversion Principle (SOLID).
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from ..models import Quest, QuestCreate


class QuestRepository(ABC):
    """Abstract repository interface for Quest entities."""

    @abstractmethod
    def list(self) -> List[Quest]:
        """Return all quests."""

    @abstractmethod
    def get(self, quest_id: int) -> Optional[Quest]:
        """Retrieve a quest by its ID."""

    @abstractmethod
    def create(self, quest_in: QuestCreate) -> Quest:
        """Persist a new quest and return it with an assigned ID."""
REPO_BASE_PY

cat <<'REPO_INMEMORY_PY' > "$ROOT_DIR/backend/app/repositories/in_memory.py"
"""In‑memory implementation of the Quest repository.

This repository stores quests in a Python dictionary. It is suitable for
testing and demonstration purposes and can be replaced by a database-backed
repository without changing the service or API layers.
"""
from typing import Dict, List, Optional

from .base import QuestRepository
from ..models import Quest, QuestCreate


class InMemoryQuestRepository(QuestRepository):
    """A simple in‑memory repository using an auto‑incrementing integer ID."""

    def __init__(self) -> None:
        self._storage: Dict[int, Quest] = {}
        self._counter: int = 0

    def list(self) -> List[Quest]:
        return list(self._storage.values())

    def get(self, quest_id: int) -> Optional[Quest]:
        return self._storage.get(quest_id)

    def create(self, quest_in: QuestCreate) -> Quest:
        self._counter += 1
        quest = Quest(id=self._counter, **quest_in.dict())
        self._storage[self._counter] = quest
        return quest

REPO_INMEMORY_PY

# Service layer encapsulating business logic
cat <<'QUEST_SERVICE_PY' > "$ROOT_DIR/backend/app/services/quest_service.py"
"""Service class for quest operations.

The service layer encapsulates business rules and uses a repository to
interact with persistence. This follows the Single Responsibility Principle
and makes it easier to unit test the business logic in isolation.
"""
from typing import List

from ..models import Quest, QuestCreate
from ..repositories.base import QuestRepository


class QuestService:
    """Provide operations over Quest entities."""

    def __init__(self, repository: QuestRepository) -> None:
        self._repository = repository

    def list_quests(self) -> List[Quest]:
        return self._repository.list()

    def create_quest(self, quest_in: QuestCreate) -> Quest:
        return self._repository.create(quest_in)

QUEST_SERVICE_PY

# Dependency injection for repositories
cat <<'DEPENDENCIES_PY' > "$ROOT_DIR/backend/app/core/dependencies.py"
"""FastAPI dependency providers for repositories and services."""
from functools import lru_cache

from ..repositories.base import QuestRepository
from ..repositories.in_memory import InMemoryQuestRepository


@lru_cache()
def get_quest_repository() -> QuestRepository:
    """Return a singleton in‑memory quest repository.

    In a real application, this could switch based on configuration to a
    database‑backed repository. Using lru_cache ensures we reuse the same
    instance across requests.
    """
    return InMemoryQuestRepository()

DEPENDENCIES_PY

# API endpoint module for quests
cat <<'QUESTS_ENDPOINT_PY' > "$ROOT_DIR/backend/app/api/v1/endpoints/quests.py"
"""API routes for managing quests."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from ....models import Quest, QuestCreate
from ....services.quest_service import QuestService
from ....repositories.base import QuestRepository
from ....core.dependencies import get_quest_repository


router = APIRouter()


@router.get("/", response_model=List[Quest], summary="Listar todas as quests")
def list_quests(
    repository: QuestRepository = Depends(get_quest_repository),
):
    """Retorna uma lista de todas as quests disponíveis."""
    service = QuestService(repository)
    return service.list_quests()


@router.post("/", response_model=Quest, status_code=status.HTTP_201_CREATED, summary="Criar nova quest")
def create_quest(
    quest_in: QuestCreate,
    repository: QuestRepository = Depends(get_quest_repository),
):
    """Cria uma nova quest com os dados fornecidos."""
    service = QuestService(repository)
    return service.create_quest(quest_in)

QUESTS_ENDPOINT_PY

echo "Extended backend skeleton with models, repositories, services and quest endpoints created."

# Proceed to frontend setup
bash "$SCRIPT_DIR/03_setup_frontend.sh"