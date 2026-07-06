"""Tests for the DPO export service and /battles/export endpoint."""
import json
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.core.dependencies import (
    get_agent_profile_repository,
    get_alpha_store,
    get_post_mortem_repository,
    get_public_alpha_service,
    get_quest_repository,
    get_ranking_repository,
    get_replay_event_repository,
    get_run_repository,
)
from backend.app.core.rate_limit import reset_rate_limiter
from backend.app.main import app
from backend.app.models import Quest
from backend.app.services.dpo_export_service import (
    _build_prompt,
    _workspace_to_text,
    iter_dpo_pairs,
)


# ---------------------------------------------------------------------------
# Unit tests — pure functions in dpo_export_service
# ---------------------------------------------------------------------------


class BuildPromptTest(unittest.TestCase):
    def _make_quest(self, **kwargs) -> Quest:
        defaults = {
            "id": "q1",
            "title": "Hello World",
            "description": "Build a hello endpoint",
            "requirements": [],
        }
        defaults.update(kwargs)
        return Quest(**defaults)

    def test_build_prompt_contains_title_and_requirements(self) -> None:
        quest = self._make_quest(
            title="Fix the bug",
            description="There is a regression in the auth flow.",
            requirements=["Must return 200", "Must set Content-Type"],
        )
        prompt = _build_prompt(quest)
        self.assertIn("Fix the bug", prompt)
        self.assertIn("There is a regression in the auth flow.", prompt)
        self.assertIn("Must return 200", prompt)
        self.assertIn("Must set Content-Type", prompt)

    def test_build_prompt_no_requirements_section_when_empty(self) -> None:
        quest = self._make_quest(requirements=[])
        prompt = _build_prompt(quest)
        self.assertNotIn("Requirements:", prompt)


class WorkspaceToTextTest(unittest.TestCase):
    def test_workspace_to_text_formats_files(self) -> None:
        files = {"app/main.py": "print('hello')", "README.md": "# Hello"}
        text = _workspace_to_text(json.dumps(files))
        self.assertIn("app/main.py", text)
        self.assertIn("README.md", text)
        self.assertIn("print('hello')", text)
        self.assertIn("# Hello", text)

    def test_workspace_to_text_empty_on_invalid_json(self) -> None:
        result = _workspace_to_text("not-valid-json")
        self.assertEqual(result, "")

    def test_workspace_to_text_empty_on_empty_dict(self) -> None:
        result = _workspace_to_text("{}")
        self.assertEqual(result, "")


class IterDpoPairsTest(unittest.TestCase):
    def _make_quest(self, quest_id: str = "q1") -> Quest:
        return Quest(
            id=quest_id,
            title="Hello World",
            description="Build a hello endpoint",
            requirements=["Must return 200"],
        )

    def _make_battle(
        self,
        quest_id: str = "q1",
        winner_score: float = 90.0,
        loser_score: float = 60.0,
        winner_files: dict | None = None,
        loser_files: dict | None = None,
    ) -> dict:
        if winner_files is None:
            winner_files = {"app/main.py": "# winner"}
        if loser_files is None:
            loser_files = {"app/main.py": "# loser"}
        return {
            "id": f"battle-{uuid4().hex[:8]}",
            "quest_id": quest_id,
            "status": "completed",
            "finished_at": "2026-06-01T00:00:00",
            "participants": [
                {
                    "user_id": "u1",
                    "score": winner_score,
                    "workspace_files": json.dumps(winner_files),
                },
                {
                    "user_id": "u2",
                    "score": loser_score,
                    "workspace_files": json.dumps(loser_files),
                },
            ],
        }

    def test_iter_dpo_pairs_yields_winner_as_chosen(self) -> None:
        quest = self._make_quest()
        battle = self._make_battle(
            winner_files={"app/main.py": "# winner code"},
            loser_files={"app/main.py": "# loser code"},
        )
        pairs = list(iter_dpo_pairs([battle], {"q1": quest}))
        self.assertEqual(len(pairs), 1)
        pair = pairs[0]
        self.assertIn("winner code", pair["chosen"])
        self.assertIn("loser code", pair["rejected"])
        self.assertEqual(pair["metadata"]["winner_score"], 90.0)
        self.assertEqual(pair["metadata"]["loser_score"], 60.0)
        self.assertIn("Hello World", pair["prompt"])

    def test_iter_dpo_pairs_skips_draws(self) -> None:
        quest = self._make_quest()
        battle = self._make_battle(winner_score=70.0, loser_score=70.0)
        pairs = list(iter_dpo_pairs([battle], {"q1": quest}))
        self.assertEqual(len(pairs), 0)

    def test_iter_dpo_pairs_skips_missing_quest(self) -> None:
        battle = self._make_battle(quest_id="nonexistent")
        pairs = list(iter_dpo_pairs([battle], {}))
        self.assertEqual(len(pairs), 0)

    def test_iter_dpo_pairs_skips_empty_workspace(self) -> None:
        quest = self._make_quest()
        battle = self._make_battle(winner_files={}, loser_files={"app/main.py": "# loser"})
        pairs = list(iter_dpo_pairs([battle], {"q1": quest}))
        self.assertEqual(len(pairs), 0)


# ---------------------------------------------------------------------------
# Endpoint tests — hit /api/v1/battles/export via TestClient
# ---------------------------------------------------------------------------


class ExportEndpointTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def setUp(self) -> None:
        self.login_suffix = uuid4().hex[:8]
        get_quest_repository.cache_clear()
        get_agent_profile_repository.cache_clear()
        get_run_repository.cache_clear()
        get_replay_event_repository.cache_clear()
        get_post_mortem_repository.cache_clear()
        get_ranking_repository.cache_clear()
        get_public_alpha_service.cache_clear()
        get_alpha_store.cache_clear()
        reset_rate_limiter()
        if os.path.exists(settings.ALPHA_DB_PATH):
            os.remove(settings.ALPHA_DB_PATH)

    def _login(self, client: TestClient, github_login: str) -> None:
        start = client.post(
            "/api/v1/auth/github/start",
            json={
                "github_login": github_login,
                "invite_code": settings.DEFAULT_ALPHA_INVITE_CODE,
            },
        )
        self.assertEqual(start.status_code, 200)
        callback_path = start.json()["authorization_url"]
        callback = client.get(callback_path)
        self.assertEqual(callback.status_code, 200)
        self.assertTrue(callback.json()["authenticated"])

    def test_export_endpoint_returns_ndjson(self) -> None:
        """Authenticated request returns 200 with ndjson content-type (empty when no battles)."""
        github_login = f"export-user-{self.login_suffix}"
        self._login(self.client, github_login)

        response = self.client.get("/api/v1/battles/export?format=dpo")
        self.assertEqual(response.status_code, 200)
        content_type = response.headers.get("content-type", "")
        self.assertIn("ndjson", content_type)
        # Body is valid JSONL: each non-empty line must parse as JSON
        for line in response.text.splitlines():
            line = line.strip()
            if line:
                parsed = json.loads(line)
                self.assertIn("prompt", parsed)
                self.assertIn("chosen", parsed)
                self.assertIn("rejected", parsed)

    def test_export_endpoint_rejects_unknown_format(self) -> None:
        """Request with unsupported format returns 400."""
        github_login = f"export-fmt-{self.login_suffix}"
        self._login(self.client, github_login)

        response = self.client.get("/api/v1/battles/export?format=csv")
        self.assertEqual(response.status_code, 400)
        self.assertIn("csv", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
