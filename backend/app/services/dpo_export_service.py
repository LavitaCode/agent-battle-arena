"""DPO export: converts completed battles to Direct Preference Optimization training pairs."""
from __future__ import annotations
import json
from typing import Iterator
from ..models import Quest


def _build_prompt(quest: Quest) -> str:
    lines = [f"Task: {quest.title}", f"\n{quest.description}"]
    if quest.requirements:
        lines.append("\nRequirements:")
        lines.extend(f"- {r}" for r in quest.requirements)
    return "\n".join(lines)


def _workspace_to_text(workspace_files_json: str) -> str:
    try:
        files: dict = json.loads(workspace_files_json or "{}")
        if not files:
            return ""
        return "\n\n".join(
            f"### {path}\n```\n{content}\n```"
            for path, content in sorted(files.items())
        )
    except (json.JSONDecodeError, AttributeError):
        return ""


def iter_dpo_pairs(
    battles: list[dict],
    quests_by_id: dict[str, Quest],
) -> Iterator[dict]:
    """Yield DPO training pairs for completed battles with a clear winner."""
    for battle in battles:
        participants = battle.get("participants", [])
        if len(participants) < 2:
            continue
        quest = quests_by_id.get(battle["quest_id"])
        if quest is None:
            continue
        # participants sorted by score DESC from the query
        winner, loser = participants[0], participants[1]
        winner_score = winner.get("score") or 0
        loser_score = loser.get("score") or 0
        if winner_score <= loser_score:
            continue  # draw or no clear winner — skip
        chosen = _workspace_to_text(winner.get("workspace_files", "{}"))
        rejected = _workspace_to_text(loser.get("workspace_files", "{}"))
        if not chosen or not rejected:
            continue  # skip if either submission is empty
        yield {
            "prompt": _build_prompt(quest),
            "chosen": chosen,
            "rejected": rejected,
            "metadata": {
                "battle_id": battle["id"],
                "quest_id": quest.id,
                "winner_score": winner_score,
                "loser_score": loser_score,
                "finished_at": battle.get("finished_at"),
            },
        }
