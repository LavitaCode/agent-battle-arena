"""Maps executor names from agent profiles to concrete executor instances."""
from __future__ import annotations

import os
from typing import Optional

from .base import AgentExecutor


def get_executor(executor_name: str) -> Optional[AgentExecutor]:
    """Return an executor instance for the given name, or None if unconfigured.

    Names:
      "claude"  — requires ANTHROPIC_API_KEY env var
      "openai"  — requires OPENAI_API_KEY env var
      "ollama"  — requires local Ollama; uses OLLAMA_BASE_URL / OLLAMA_MODEL env vars
      anything else → None (human submission path)
    """
    if executor_name == "claude":
        from .claude_executor import ClaudeExecutor
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            return None
        return ClaudeExecutor(api_key=api_key)

    if executor_name == "openai":
        from .openai_executor import OpenAIExecutor
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return None
        return OpenAIExecutor(api_key=api_key)

    if executor_name == "ollama":
        from .ollama_executor import OllamaExecutor
        return OllamaExecutor(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b"),
        )

    return None
