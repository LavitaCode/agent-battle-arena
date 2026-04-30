"""Service for reading quest starter files from the local registry."""
from pathlib import Path
from typing import List

from ..models import QuestStarterFile


class StarterFileService:
    """Read starter files associated with a quest."""

    def __init__(self, quests_root: Path) -> None:
        self._quests_root = quests_root

    def list_for_quest(self, quest_id: str) -> List[QuestStarterFile]:
        starter_root = self._quests_root / quest_id / "starter"
        if not starter_root.exists() or not starter_root.is_dir():
            return []

        files: List[QuestStarterFile] = []
        for file_path in sorted(path for path in starter_root.rglob("*") if path.is_file()):
            files.append(
                QuestStarterFile(
                    path=file_path.relative_to(starter_root).as_posix(),
                    content=file_path.read_text(encoding="utf-8"),
                )
            )
        return files
