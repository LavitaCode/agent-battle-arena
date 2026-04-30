"""Service class for run artifact operations."""
from pathlib import Path
from typing import List, Optional

from ..models import Run, RunArtifact


class ArtifactService:
    """Read artifact metadata and content from persisted run outputs."""

    def list_artifacts(self, run: Run) -> List[RunArtifact]:
        artifacts = []
        for name, path in run.summary.artifacts.items():
            artifacts.append(
                RunArtifact(
                    name=name,
                    path=path,
                    content="",
                )
            )
        return artifacts

    def get_artifact(self, run: Run, artifact_name: str) -> Optional[RunArtifact]:
        artifact_path = run.summary.artifacts.get(artifact_name)
        if artifact_path is None:
            return None
        path = Path(artifact_path)
        if not path.exists():
            return RunArtifact(name=artifact_name, path=str(path), content="")
        return RunArtifact(
            name=artifact_name,
            path=str(path),
            content=path.read_text(encoding="utf-8"),
        )
