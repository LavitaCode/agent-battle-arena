"""Shared prompt builder for all LLM executors."""
from __future__ import annotations

import json

from ..models import Quest


_SYSTEM = (
    "You are an autonomous software agent competing in the Agent Battle Arena. "
    "You receive a coding quest and the starter files. "
    "Your goal: produce corrected or completed workspace files that pass all tests. "
    "Respond ONLY with a JSON object: {\"workspace_files\": {\"relative/path\": \"file content\"}}. "
    "Do not include any explanation, markdown fences, or extra keys."
)


def build_user_prompt(quest: Quest, starter_files: dict[str, str]) -> str:
    starters_block = "\n\n".join(
        f"### {path}\n```\n{content}\n```"
        for path, content in starter_files.items()
    )
    return (
        f"Quest: {quest.title}\n\n"
        f"Description:\n{quest.description}\n\n"
        f"Requirements:\n" + "\n".join(f"- {r}" for r in quest.requirements) + "\n\n"
        f"Forbidden actions:\n" + "\n".join(f"- {a}" for a in quest.forbidden_actions) + "\n\n"
        f"Starter files:\n{starters_block}\n\n"
        f"Respond with JSON only."
    )


def parse_response(raw: str) -> dict[str, str]:
    """Extract workspace_files from LLM response. Returns {} on any parse error."""
    text = raw.strip()
    # Strip markdown fences if the model added them despite instructions
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(
            line for line in lines if not line.startswith("```")
        ).strip()
    try:
        payload = json.loads(text)
        files = payload.get("workspace_files", {})
        if isinstance(files, dict) and all(
            isinstance(k, str) and isinstance(v, str) for k, v in files.items()
        ):
            return files
    except (json.JSONDecodeError, AttributeError):
        pass
    return {}


SYSTEM_PROMPT = _SYSTEM
