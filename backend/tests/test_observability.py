"""Operational health and metrics tests."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from uuid import uuid4

from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.core.dependencies import get_quest_repository
from backend.app.core.metrics import reset_metrics, snapshot_metrics
from backend.app.core.rate_limit import reset_rate_limiter
from backend.app.main import app
from backend.app.models import BattleCreate, BattleJoin
from backend.app.services.alpha_store import AlphaStore
from backend.app.services.public_alpha_service import PublicAlphaService
from backend.app.services.quest_service import QuestService
from backend.app.core.dependencies import get_sandbox_runner


class ObservabilityTestCase(unittest.TestCase):
    def setUp(self) -> None:
        reset_metrics()
        reset_rate_limiter()
        get_quest_repository.cache_clear()
        self.client = TestClient(app)
        self.login_suffix = uuid4().hex[:8]

    def test_health_reports_storage_worker_and_metrics(self) -> None:
        response = self.client.get("/api/v1/health")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertIn(payload["storage"]["backend"], {"sqlite", "postgres"})
        self.assertGreaterEqual(payload["storage"]["schema_version"], 1)
        self.assertIn("pending_jobs", payload["worker"])
        self.assertIn("requests_total", payload["metrics"])

    def test_admin_debug_requires_configured_token(self) -> None:
        original_token = settings.ADMIN_DEBUG_TOKEN
        try:
            settings.ADMIN_DEBUG_TOKEN = "operator-secret"

            missing = self.client.get("/api/v1/admin/debug")
            wrong = self.client.get(
                "/api/v1/admin/debug",
                headers={"X-CQA-Admin-Token": "wrong-secret"},
            )
        finally:
            settings.ADMIN_DEBUG_TOKEN = original_token

        self.assertEqual(missing.status_code, 403)
        self.assertEqual(wrong.status_code, 403)

    def test_admin_debug_reports_operational_snapshot(self) -> None:
        original_token = settings.ADMIN_DEBUG_TOKEN
        try:
            settings.ADMIN_DEBUG_TOKEN = "operator-secret"
            response = self.client.get(
                "/api/v1/admin/debug",
                headers={"X-CQA-Admin-Token": "operator-secret"},
            )
        finally:
            settings.ADMIN_DEBUG_TOKEN = original_token

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertIn("storage", payload)
        self.assertIn("worker", payload)
        self.assertIn("metrics", payload)
        self.assertEqual(payload["sandbox"]["docker_network"], "none")
        self.assertIn("--read-only", payload["sandbox"]["docker_hardening_flags"])

    def test_rate_limit_hit_increments_metric(self) -> None:
        original_enabled = settings.RATE_LIMIT_ENABLED
        original_limit = settings.RATE_LIMIT_AUTH_REQUESTS_PER_MINUTE
        try:
            settings.RATE_LIMIT_ENABLED = True
            settings.RATE_LIMIT_AUTH_REQUESTS_PER_MINUTE = 1
            first = self.client.post(
                "/api/v1/auth/github/start",
                json={
                    "github_login": f"metrics-one-{self.login_suffix}",
                    "invite_code": settings.DEFAULT_ALPHA_INVITE_CODE,
                },
            )
            second = self.client.post(
                "/api/v1/auth/github/start",
                json={
                    "github_login": f"metrics-two-{self.login_suffix}",
                    "invite_code": settings.DEFAULT_ALPHA_INVITE_CODE,
                },
            )
        finally:
            settings.RATE_LIMIT_ENABLED = original_enabled
            settings.RATE_LIMIT_AUTH_REQUESTS_PER_MINUTE = original_limit

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 429)
        self.assertEqual(snapshot_metrics()["rate_limit_hits_total"], 1)

    def test_battle_start_increments_queued_metric(self) -> None:
        class FakeWorker:
            def __init__(self) -> None:
                self.enqueued: list[str] = []

            def enqueue(self, battle_id: str) -> None:
                self.enqueued.append(battle_id)

            def pending_count(self) -> int:
                return len(self.enqueued)

        with TemporaryDirectory() as temp_dir:
            store = AlphaStore(str(Path(temp_dir) / "alpha.sqlite3"))
            worker = FakeWorker()
            service = PublicAlphaService(
                store,
                QuestService(get_quest_repository()),
                get_sandbox_runner(),
                battle_worker=worker,
            )
            creator = store.upsert_user(f"obs-left-{self.login_suffix}")
            opponent = store.upsert_user(f"obs-right-{self.login_suffix}")
            left = service.create_profile_from_template(creator, "buildknight")
            right = service.create_profile_from_template(opponent, "speedster")
            detail = service.create_battle(
                creator,
                BattleCreate(
                    quest_id="quest_hello_world",
                    agent_profile_id=left.id,
                    workspace_files={"app/main.py": "ready"},
                ),
            )
            service.join_battle(
                detail.battle.id,
                opponent,
                BattleJoin(agent_profile_id=right.id, workspace_files={"app/main.py": "ready"}),
            )

            service.start_battle(detail.battle.id, creator)

        self.assertEqual(snapshot_metrics()["battles_queued_total"], 1)
        self.assertEqual(worker.enqueued, [detail.battle.id])


if __name__ == "__main__":
    unittest.main()
