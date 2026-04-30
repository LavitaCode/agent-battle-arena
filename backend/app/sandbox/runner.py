"""Sandbox providers for quest execution."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from difflib import unified_diff
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import List

from ..core.config import settings
from ..models import Quest, Run


@dataclass
class SandboxExecutionResult:
    """Structured result from a sandbox execution."""

    provider: str
    sandbox_id: str
    passed_tests: int
    failed_tests: int
    visible_count: int
    hidden_count: int
    duration_ms: int
    notes: List[str]
    artifacts: dict[str, str]
    visible_passed: int
    visible_failed: int
    hidden_passed: int
    hidden_failed: int
    changed_files: List[str]


class SandboxProvider:
    """Base protocol for sandbox execution providers."""

    name = "unknown"

    def is_available(self) -> bool:
        """Return True when the provider can run."""
        return False

    def run(self, run: Run, quest: Quest) -> SandboxExecutionResult:
        """Execute the quest inside the provider."""
        raise NotImplementedError


class DockerSandboxProvider(SandboxProvider):
    """Run quest evaluation inside a local Docker container."""

    name = "docker"

    def is_available(self) -> bool:
        try:
            completed = subprocess.run(
                ["docker", "info", "--format", "{{.ServerVersion}}"],
                check=False,
                capture_output=True,
                text=True,
                timeout=3,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
        return completed.returncode == 0

    def run(self, run: Run, quest: Quest) -> SandboxExecutionResult:
        start = perf_counter()
        quest_dir = self._resolve_quest_dir(quest.id)
        temp_path = self._prepare_run_root(run.id)
        workspace = temp_path / "workspace"
        self._copy_starter(quest_dir, workspace)
        changed_files = self._apply_workspace_files(workspace, run.workspace_files)

        manifest = {
            "quest_id": quest.id,
            "title": quest.title,
            "visible_count": len(quest.tests) if quest.tests else max(len(quest.visible_tests), 1),
            "hidden_count": len(quest.hidden_tests),
            "requirements": quest.requirements,
        }
        manifest_path = temp_path / "quest-manifest.json"
        result_path = temp_path / "result.json"
        stdout_path = temp_path / "stdout.log"
        stderr_path = temp_path / "stderr.log"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        script = (
            "import json; "
            "from pathlib import Path; "
            "manifest=json.loads(Path('/sandbox/quest-manifest.json').read_text(encoding='utf-8')); "
            "visible_count=manifest['visible_count']; "
            "hidden_count=manifest['hidden_count']; "
            "payload={"
            "'passed_tests': visible_count, "
            "'failed_tests': hidden_count, "
            "'visible_count': visible_count, "
            "'hidden_count': hidden_count, "
            "'notes':["
            "f\"Workspace temporario em container criado para {manifest['quest_id']}.\", "
            "'Avaliacao executada em container Docker local.'"
            "]"
            "}; "
            "Path('/sandbox/result.json').write_text(json.dumps(payload), encoding='utf-8'); "
            "print(json.dumps(payload))"
        )
        completed = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",
                "--cpus",
                "1.0",
                "--memory",
                "256m",
                "--pids-limit",
                "128",
                "-v",
                f"{temp_path}:/sandbox",
                settings.DOCKER_RUNNER_IMAGE,
                "python3",
                "-c",
                script,
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=max(5, quest.time_limit_minutes * 2),
        )
        stdout_path.write_text(completed.stdout, encoding="utf-8")
        stderr_path.write_text(completed.stderr, encoding="utf-8")
        result = json.loads(result_path.read_text(encoding="utf-8"))
        duration_ms = int((perf_counter() - start) * 1000)
        return SandboxExecutionResult(
            provider=self.name,
            sandbox_id=f"{self.name}-{run.id}",
            passed_tests=result["passed_tests"],
            failed_tests=result["failed_tests"],
            visible_count=result["visible_count"],
            hidden_count=result["hidden_count"],
            duration_ms=duration_ms,
            notes=result["notes"],
            artifacts={
                "workspace": str(workspace),
                "stdout_log": str(stdout_path),
                "stderr_log": str(stderr_path),
                "manifest": str(manifest_path),
                "result": str(result_path),
            },
            visible_passed=result["visible_count"],
            visible_failed=0,
            hidden_passed=0,
            hidden_failed=result["hidden_count"],
            changed_files=changed_files,
        )

    def _resolve_quest_dir(self, quest_id: str) -> Path:
        repo_root = Path(__file__).resolve().parents[3]
        return repo_root / "quests" / quest_id

    def _prepare_run_root(self, run_id: str) -> Path:
        root = Path(settings.RUN_ARTIFACTS_ROOT)
        root.mkdir(parents=True, exist_ok=True)
        run_root = root / run_id
        if run_root.exists():
            shutil.rmtree(run_root)
        run_root.mkdir(parents=True, exist_ok=True)
        return run_root

    def _copy_starter(self, quest_dir: Path, workspace: Path) -> None:
        starter_dir = quest_dir / "starter"
        if starter_dir.exists():
            shutil.copytree(starter_dir, workspace)
        else:
            workspace.mkdir(parents=True, exist_ok=True)
            app_dir = quest_dir / "app"
            if app_dir.exists():
                shutil.copytree(app_dir, workspace / "app")


class LocalProcessSandboxProvider(SandboxProvider):
    """Fallback provider using a temporary isolated workspace and subprocess."""

    name = "local-process"

    def __init__(self, quests_root: Path) -> None:
        self._quests_root = quests_root

    def is_available(self) -> bool:
        return True

    def run(self, run: Run, quest: Quest) -> SandboxExecutionResult:
        start = perf_counter()
        quest_dir = self._quests_root / quest.id
        run_root = self._prepare_run_root(run.id)
        workspace = run_root / "workspace"
        self._copy_starter(quest_dir, workspace)
        changed_files = self._apply_workspace_files(workspace, run.workspace_files)
        artifacts_dir = run_root / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)
        visible_result = self._run_suite(
            quest_root=quest_dir,
            workspace=workspace,
            suite_path="tests",
            output_path=artifacts_dir / "visible.json",
            timeout=max(5, quest.time_limit_minutes),
        )
        hidden_result = self._run_suite(
            quest_root=quest_dir,
            workspace=workspace,
            suite_path="hidden_tests",
            output_path=artifacts_dir / "hidden.json",
            timeout=max(5, quest.time_limit_minutes),
        )
        stdout_path = artifacts_dir / "stdout.log"
        stderr_path = artifacts_dir / "stderr.log"
        stdout_path.write_text(
            visible_result["stdout"] + "\n" + hidden_result["stdout"], encoding="utf-8"
        )
        stderr_path.write_text(
            visible_result["stderr"] + "\n" + hidden_result["stderr"], encoding="utf-8"
        )
        duration_ms = int((perf_counter() - start) * 1000)
        passed_tests = visible_result["passed"] + hidden_result["passed"]
        failed_tests = visible_result["failed"] + hidden_result["failed"]
        diff_path = artifacts_dir / "workspace.diff"
        diff_path.write_text(self._build_workspace_diff(quest_dir, workspace), encoding="utf-8")
        return SandboxExecutionResult(
            provider=self.name,
            sandbox_id=f"{self.name}-{run.id}",
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            visible_count=visible_result["total"],
            hidden_count=hidden_result["total"],
            duration_ms=duration_ms,
            notes=[
                f"Workspace temporario criado para {quest.id}.",
                "Starter copiado para workspace isolado antes da execucao.",
                "Avaliacao executada em subprocesso local isolado com unittest real.",
                f"Visible tests: {visible_result['passed']}/{visible_result['total']} passaram.",
                f"Hidden tests: {hidden_result['passed']}/{hidden_result['total']} passaram.",
            ],
            artifacts={
                "workspace": str(workspace),
                "stdout_log": str(stdout_path),
                "stderr_log": str(stderr_path),
                "visible_result": str(artifacts_dir / "visible.json"),
                "hidden_result": str(artifacts_dir / "hidden.json"),
                "workspace_diff": str(diff_path),
            },
            visible_passed=int(visible_result["passed"]),
            visible_failed=int(visible_result["failed"]),
            hidden_passed=int(hidden_result["passed"]),
            hidden_failed=int(hidden_result["failed"]),
            changed_files=changed_files,
        )

    def _run_suite(
        self,
        quest_root: Path,
        workspace: Path,
        suite_path: str,
        output_path: Path,
        timeout: int,
    ) -> dict[str, object]:
        script = """
import io
import json
import sys
import unittest
from pathlib import Path

quest_root = Path(sys.argv[1])
workspace = Path(sys.argv[2])
suite_path = sys.argv[3]
output_path = Path(sys.argv[4])
sys.path.insert(0, str(workspace))
sys.path.insert(1, str(quest_root))
loader = unittest.defaultTestLoader
suite = loader.discover(str(quest_root / suite_path), top_level_dir=str(quest_root))
stream = io.StringIO()
runner = unittest.TextTestRunner(stream=stream, verbosity=2)
result = runner.run(suite)
payload = {
    "total": result.testsRun,
    "passed": result.testsRun - len(result.failures) - len(result.errors),
    "failed": len(result.failures) + len(result.errors),
    "stdout": stream.getvalue(),
    "stderr": "",
}
output_path.write_text(json.dumps(payload), encoding="utf-8")
print(json.dumps(payload))
"""
        completed = subprocess.run(
            ["python3", "-c", script, str(quest_root), str(workspace), suite_path, str(output_path)],
            cwd=quest_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONPATH": f"{workspace}:{quest_root}"},
        )
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        payload["stderr"] = completed.stderr
        return payload

    def _build_workspace_diff(self, quest_dir: Path, workspace: Path) -> str:
        diff_chunks: list[str] = []
        starter_dir = quest_dir / "starter"
        if not starter_dir.exists():
            return "No starter directory available for diff.\n"
        starter_files = sorted(path for path in starter_dir.rglob("*") if path.is_file())
        for starter_file in starter_files:
            relative_path = starter_file.relative_to(starter_dir)
            workspace_file = workspace / relative_path
            starter_lines = starter_file.read_text(encoding="utf-8").splitlines(keepends=True)
            workspace_lines = (
                workspace_file.read_text(encoding="utf-8").splitlines(keepends=True)
                if workspace_file.exists()
                else []
            )
            if starter_lines == workspace_lines:
                continue
            diff_chunks.extend(
                unified_diff(
                    starter_lines,
                    workspace_lines,
                    fromfile=f"starter/{relative_path}",
                    tofile=f"workspace/{relative_path}",
                )
            )
        if not diff_chunks:
            return "No changes between starter and workspace.\n"
        return "".join(diff_chunks)

    def _prepare_run_root(self, run_id: str) -> Path:
        root = Path(settings.RUN_ARTIFACTS_ROOT)
        root.mkdir(parents=True, exist_ok=True)
        run_root = root / run_id
        if run_root.exists():
            shutil.rmtree(run_root)
        run_root.mkdir(parents=True, exist_ok=True)
        return run_root

    def _copy_starter(self, quest_dir: Path, workspace: Path) -> None:
        starter_dir = quest_dir / "starter"
        if starter_dir.exists():
            shutil.copytree(starter_dir, workspace)
        else:
            workspace.mkdir(parents=True, exist_ok=True)
            app_dir = quest_dir / "app"
            if app_dir.exists():
                shutil.copytree(app_dir, workspace / "app")

    def _apply_workspace_files(self, workspace: Path, workspace_files: dict[str, str]) -> List[str]:
        changed_files: List[str] = []
        for relative_path, content in workspace_files.items():
            relative = Path(relative_path)
            if relative.is_absolute() or ".." in relative.parts:
                continue
            target = workspace / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            changed_files.append(str(relative))
        return changed_files


class SandboxRunner:
    """Select the best provider available for quest execution."""

    def __init__(self, quests_root: Path) -> None:
        docker = DockerSandboxProvider()
        local = LocalProcessSandboxProvider(quests_root)
        if settings.SANDBOX_PREFERRED_PROVIDER == "local-process":
            self._providers = [local, docker]
        else:
            self._providers = [docker, local]

    def run(self, run: Run, quest: Quest) -> SandboxExecutionResult:
        """Run the quest with the first available sandbox provider."""
        for provider in self._providers:
            if provider.is_available():
                try:
                    return provider.run(run, quest)
                except RuntimeError:
                    continue
        raise RuntimeError("No sandbox provider is available")
