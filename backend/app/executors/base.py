"""Abstract base for LLM agent executors."""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import Quest


class AgentExecutor(ABC):
    """Given a quest and its starter files, produce workspace_files via an LLM."""

    name: str = "unknown"
    timeout_seconds: int = 60

    @abstractmethod
    def execute(self, quest: Quest, starter_files: dict[str, str]) -> dict[str, str]:
        """Return workspace_files the agent wants to submit.

        Must not raise — return {} on any failure so the sandbox scores 0.
        """
