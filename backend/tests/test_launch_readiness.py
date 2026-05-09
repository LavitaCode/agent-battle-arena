"""Smoke checks for opening the controlled public alpha."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import yaml
from fastapi.testclient import TestClient

from backend.app.core.dependencies import get_quest_repository
from backend.app.main import app
from backend.app.services.alpha_store import AlphaStore


REPO_ROOT = Path(__file__).resolve().parents[2]


class LaunchReadinessTestCase(unittest.TestCase):
    def setUp(self) -> None:
        get_quest_repository.cache_clear()

    def test_official_quest_catalog_has_launch_metadata(self) -> None:
        quest_files = sorted((REPO_ROOT / "quests").glob("*/quest.yaml"))

        self.assertGreaterEqual(len(quest_files), 3)
        self.assertLessEqual(len(quest_files), 5)
        for quest_file in quest_files:
            payload = yaml.safe_load(quest_file.read_text(encoding="utf-8"))
            with self.subTest(quest=quest_file.parent.name):
                self.assertEqual(payload["id"], quest_file.parent.name)
                self.assertTrue(payload["title"])
                self.assertIn(payload["difficulty"], {"bronze", "silver", "gold"})
                self.assertIn(payload["mode"], {"solo", "async_1v1"})
                self.assertGreater(payload["time_limit_minutes"], 0)
                self.assertGreaterEqual(len(payload["requirements"]), 2)
                self.assertGreaterEqual(len(payload["forbidden_actions"]), 1)
                self.assertGreaterEqual(len(payload["visible_tests"]), 1)
                self.assertGreaterEqual(len(payload["hidden_tests"]), 1)

    def test_alpha_has_four_official_agent_templates(self) -> None:
        with TemporaryDirectory() as temp_dir:
            store = AlphaStore(str(Path(temp_dir) / "launch-readiness.sqlite3"))

            templates = store.list_templates()

        self.assertEqual(len(templates), 4)
        self.assertEqual(
            {template.id for template in templates},
            {"buildknight", "debugger", "refiner", "speedster"},
        )
        for template in templates:
            with self.subTest(template=template.id):
                self.assertGreaterEqual(len(template.recommended_for), 2)
                self.assertGreaterEqual(len(template.tips), 2)

    def test_public_launch_docs_exist(self) -> None:
        rules = REPO_ROOT / "docs" / "public-alpha-rules.md"
        faq = REPO_ROOT / "docs" / "public-alpha-faq.md"
        incident_runbook = REPO_ROOT / "docs" / "incident-response.md"

        self.assertIn("ALPHA-ACCESS", rules.read_text(encoding="utf-8"))
        self.assertIn("Como entro no alpha?", faq.read_text(encoding="utf-8"))
        self.assertIn("Severidade", incident_runbook.read_text(encoding="utf-8"))
        self.assertIn("/api/v1/admin/debug", incident_runbook.read_text(encoding="utf-8"))

    def test_public_quest_endpoint_smoke(self) -> None:
        response = TestClient(app).get("/api/v1/quests/")

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json()), 3)


if __name__ == "__main__":
    unittest.main()
