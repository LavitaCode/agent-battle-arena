"""Executor that calls OpenAI ChatCompletion to solve the quest."""
from __future__ import annotations

import logging
import os

from ..models import Quest
from .base import AgentExecutor
from .prompt import SYSTEM_PROMPT, build_user_prompt, parse_response

logger = logging.getLogger(__name__)


class OpenAIExecutor(AgentExecutor):
    """Uses the OpenAI Chat API (gpt-4o-mini by default)."""

    name = "openai"
    timeout_seconds = 60

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
    ) -> None:
        self._api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self._model = model

    def execute(self, quest: Quest, starter_files: dict[str, str]) -> dict[str, str]:
        if not self._api_key:
            logger.warning("openai_executor_no_api_key", extra={"quest_id": quest.id})
            return {}
        try:
            import openai  # type: ignore[import]
        except ImportError:
            logger.warning("openai_executor_missing_sdk")
            return {}
        try:
            client = openai.OpenAI(api_key=self._api_key)
            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_user_prompt(quest, starter_files)},
                ],
                max_tokens=4096,
                timeout=self.timeout_seconds,
            )
            raw = response.choices[0].message.content or ""
            return parse_response(raw)
        except Exception:
            logger.exception("openai_executor_failed", extra={"quest_id": quest.id})
            return {}
