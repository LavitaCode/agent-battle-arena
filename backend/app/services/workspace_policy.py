"""Validation policy for submitted workspace file overrides."""
from __future__ import annotations

from pathlib import PurePosixPath

from ..core.config import settings


SUSPICIOUS_PATH_PARTS = {
    ".git",
    ".github",
    ".ssh",
    "__pycache__",
    "node_modules",
}


def validate_workspace_files(
    workspace_files: dict[str, str],
    *,
    profile_max_files: int | None = None,
) -> None:
    """Validate user-submitted workspace files before sandbox execution."""
    max_files = settings.MAX_WORKSPACE_FILES
    if profile_max_files is not None:
        max_files = min(max_files, profile_max_files)
    if len(workspace_files) > max_files:
        raise ValueError(f"Too many workspace files: max {max_files}")

    total_bytes = 0
    for relative_path, content in workspace_files.items():
        _validate_workspace_path(relative_path)
        content_bytes = len(content.encode("utf-8"))
        if content_bytes > settings.MAX_WORKSPACE_FILE_BYTES:
            raise ValueError(
                f"Workspace file '{relative_path}' is too large: max {settings.MAX_WORKSPACE_FILE_BYTES} bytes"
            )
        total_bytes += content_bytes
        if total_bytes > settings.MAX_WORKSPACE_TOTAL_BYTES:
            raise ValueError(
                f"Workspace payload is too large: max {settings.MAX_WORKSPACE_TOTAL_BYTES} bytes"
            )


def _validate_workspace_path(relative_path: str) -> None:
    if not relative_path or not relative_path.strip():
        raise ValueError("Invalid workspace path: path cannot be empty")
    if "\\" in relative_path or "\x00" in relative_path:
        raise ValueError(f"Invalid workspace path: {relative_path}")
    path = PurePosixPath(relative_path)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Invalid workspace path: {relative_path}")
    if any(part in SUSPICIOUS_PATH_PARTS for part in path.parts):
        raise ValueError(f"Invalid workspace path: {relative_path}")
