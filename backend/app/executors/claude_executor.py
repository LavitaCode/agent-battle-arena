"""Executor that calls Anthropic Claude to solve the quest."""
from __future__ import annotations

import logging
import os

from ..models import Quest
from .base import AgentExecutor
from .prompt import SYSTEM_PROMPT, build_user_prompt, parse_response

logger = logging.getLogger(__name__)


class ClaudeExecutor(AgentExecutor):
    """Uses the Anthropic Messages API (claude-haiku-4-5-20251001 by default)."""

    name = "claude"
    timeout_seconds = 60

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-haiku-4-5-20251001",
    ) -> None:
        self._api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self._model = model

    def execute(self, quest: Quest, starter_files: dict[str, str]) -> dict[str, str]:
        if not self._api_key:
            logger.warning("claude_executor_no_api_key", extra={"quest_id": quest.id})
            return {}
        try:
            import anthropic  # type: ignore[import]
        except ImportError:
            logger.warning("claude_executor_missing_anthropic_sdk")
            return {}
        try:
            client = anthropic.Anthropic(api_key=self._api_key)
            message = client.messages.create(
                model=self._model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": build_user_prompt(quest, starter_files)}],
                timeout=self.timeout_seconds,
            )
            raw = message.content[0].text if message.content else ""
            return parse_response(raw)
        except Exception:
            logger.exception("claude_executor_failed", extra={"quest_id": quest.id})
            return {}
