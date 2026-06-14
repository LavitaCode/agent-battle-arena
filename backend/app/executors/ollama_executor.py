"""Executor that calls a local Ollama instance to solve the quest."""
from __future__ import annotations

import json
import logging
from urllib.request import Request, urlopen
from urllib.error import URLError

from ..models import Quest
from .base import AgentExecutor
from .prompt import SYSTEM_PROMPT, build_user_prompt, parse_response

logger = logging.getLogger(__name__)


class OllamaExecutor(AgentExecutor):
    """Calls Ollama /api/chat (default: http://localhost:11434, model qwen2.5-coder:7b)."""

    name = "ollama"
    timeout_seconds = 120  # local inference can be slow

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen2.5-coder:7b",
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    def execute(self, quest: Quest, starter_files: dict[str, str]) -> dict[str, str]:
        payload = {
            "model": self._model,
            "stream": False,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(quest, starter_files)},
            ],
        }
        data = json.dumps(payload).encode()
        req = Request(
            f"{self._base_url}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(req, timeout=self.timeout_seconds) as resp:
                body = json.loads(resp.read().decode())
            raw = body.get("message", {}).get("content", "")
            return parse_response(raw)
        except (URLError, OSError):
            logger.warning("ollama_executor_unreachable", extra={"quest_id": quest.id})
            return {}
        except Exception:
            logger.exception("ollama_executor_failed", extra={"quest_id": quest.id})
            return {}
