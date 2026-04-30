"""Local CLI for running quests without the web UI."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

from ..core.dependencies import (
    get_agent_profile_repository,
    get_post_mortem_repository,
    get_quest_repository,
    get_ranking_repository,
    get_replay_event_repository,
    get_run_repository,
    get_sandbox_runner,
)
from ..models import AgentProfileCreate, RunCreate
from ..services.agent_profile_service import AgentProfileService
from ..services.execution_service import ExecutionService
from ..services.quest_service import QuestService
from ..services.run_service import RunService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Agent Battle Arena quests locally.")
    parser.add_argument("--list-quests", action="store_true", help="List available quests and exit.")
    parser.add_argument("--quest-id", help="Quest identifier to run.")
    parser.add_argument("--profile-id", default="cli-profile", help="Agent profile identifier.")
    parser.add_argument("--profile-name", default="CLI Profile", help="Agent profile display name.")
    parser.add_argument("--archetype", default="architect", help="Agent archetype.")
    parser.add_argument("--planning-style", default="tests_first", help="Planning style.")
    parser.add_argument(
        "--override-file",
        action="append",
        default=[],
        metavar="PATH=FILE",
        help="Override a workspace file from a local file path.",
    )
    parser.add_argument(
        "--override-inline",
        action="append",
        default=[],
        metavar="PATH=CONTENT",
        help="Override a workspace file using inline content.",
    )
    parser.add_argument(
        "--print-json",
        action="store_true",
        help="Print the full run payload as JSON.",
    )
    return parser


def parse_overrides(args: argparse.Namespace) -> Dict[str, str]:
    workspace_files: Dict[str, str] = {}
    for item in args.override_file:
        path, local_file = item.split("=", 1)
        workspace_files[path] = Path(local_file).read_text(encoding="utf-8")
    for item in args.override_inline:
        path, content = item.split("=", 1)
        workspace_files[path] = content
    return workspace_files


def ensure_profile(args: argparse.Namespace) -> AgentProfileCreate:
    return AgentProfileCreate(
        id=args.profile_id,
        name=args.profile_name,
        archetype=args.archetype,
        planning_style=args.planning_style,
        preferred_stack=["python", "fastapi"],
        engineering_principles=["Preservar requisitos", "Preferir simplicidade testavel"],
        modules=["api_design", "test_debugging"],
        constraints={
            "allow_dependency_install": True,
            "allow_external_network": False,
            "allow_schema_change": True,
            "max_runtime_minutes": 20,
        },
        memory={"slots": ["Ler testes antes de editar"]},
        limits={"max_files_edited": 25, "max_runs": 10},
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    quest_service = QuestService(get_quest_repository())
    profile_service = AgentProfileService(get_agent_profile_repository())
    run_service = RunService(
        get_run_repository(),
        get_quest_repository(),
        get_agent_profile_repository(),
    )
    execution_service = ExecutionService(
        get_replay_event_repository(),
        get_post_mortem_repository(),
        get_ranking_repository(),
        get_sandbox_runner(),
    )

    if args.list_quests:
        for quest in quest_service.list_quests():
            print(f"{quest.id}: {quest.title} [{quest.difficulty}]")
        return 0

    if not args.quest_id:
        parser.error("--quest-id is required unless --list-quests is used")

    quest = quest_service.get_quest(args.quest_id)
    if quest is None:
        raise SystemExit(f"Quest '{args.quest_id}' not found.")

    profile = profile_service.get_profile(args.profile_id)
    if profile is None:
        profile = profile_service.create_profile(ensure_profile(args))

    workspace_files = parse_overrides(args)
    run = run_service.create_run(
        RunCreate(
            quest_id=quest.id,
            agent_profile_id=profile.id,
            workspace_files=workspace_files,
        )
    )
    completed_runs = len(run_service.list_runs())
    executed = execution_service.execute(run, quest, profile, completed_runs)
    saved = run_service.save_run(executed)

    if args.print_json:
        print(json.dumps(saved.model_dump(mode="json"), indent=2))
        return 0

    print(f"Run: {saved.id}")
    print(f"Quest: {quest.title}")
    print(f"Profile: {profile.name} ({profile.archetype})")
    print(f"Score: {saved.summary.technical_score}")
    print("Suites:")
    for suite in saved.summary.suites:
        print(f"  - {suite.suite}: {suite.passed} passed / {suite.failed} failed")
    print("Artifacts:")
    for name, path in saved.summary.artifacts.items():
        print(f"  - {name}: {path}")
    if saved.summary.notes:
        print("Notes:")
        for note in saved.summary.notes:
            print(f"  - {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
