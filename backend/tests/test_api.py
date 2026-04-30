"""Integration tests for the Sprint 1 API surface."""
import unittest

from fastapi.testclient import TestClient

from backend.app.core.dependencies import (
    get_agent_profile_repository,
    get_post_mortem_repository,
    get_quest_repository,
    get_ranking_repository,
    get_replay_event_repository,
    get_run_repository,
)
from backend.app.main import app


class ApiContractTestCase(unittest.TestCase):
    """Verify the main domain endpoints added in Sprint 1."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def setUp(self) -> None:
        get_quest_repository.cache_clear()
        get_agent_profile_repository.cache_clear()
        get_run_repository.cache_clear()
        get_replay_event_repository.cache_clear()
        get_post_mortem_repository.cache_clear()
        get_ranking_repository.cache_clear()

    def test_lists_seeded_quests(self) -> None:
        response = self.client.get("/api/v1/quests/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreaterEqual(len(payload), 3)
        ids = {item["id"] for item in payload}
        self.assertIn("quest_hello_world", ids)
        self.assertIn("quest_bugfix_headers", ids)
        self.assertIn("quest_profile_settings", ids)
        hello_world = next(item for item in payload if item["id"] == "quest_hello_world")
        self.assertIn("requirements", hello_world)

    def test_lists_starter_files_for_seeded_quest(self) -> None:
        response = self.client.get("/api/v1/quests/quest_hello_world/starter-files")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreaterEqual(len(payload), 1)
        self.assertTrue(any(item["path"] == "app/main.py" for item in payload))
        app_main = next(item for item in payload if item["path"] == "app/main.py")
        self.assertIn("FastAPI", app_main["content"])

    def test_creates_and_reads_agent_profile(self) -> None:
        create_response = self.client.post(
            "/api/v1/profiles/",
            json={
                "id": "buildknight",
                "name": "BuildKnight",
                "archetype": "architect",
                "planning_style": "tests_first",
                "preferred_stack": ["python", "fastapi", "angular"],
                "engineering_principles": ["Preservar requisitos", "Preferir simplicidade"],
                "modules": ["api_design", "test_debugging"],
                "constraints": {
                    "allow_dependency_install": True,
                    "allow_external_network": False,
                    "allow_schema_change": True,
                    "max_runtime_minutes": 20,
                },
                "memory": {
                    "slots": [
                        "Ler testes antes de editar",
                        "Criar reproducao minima antes de refatorar",
                    ]
                },
                "limits": {"max_files_edited": 20, "max_runs": 8},
            },
        )

        self.assertEqual(create_response.status_code, 201)
        get_response = self.client.get("/api/v1/profiles/buildknight")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["archetype"], "architect")

    def test_creates_run_for_existing_quest_and_profile(self) -> None:
        self.client.post(
            "/api/v1/profiles/",
            json={
                "id": "speedster",
                "name": "Speedster",
                "archetype": "speedrunner",
                "planning_style": "simplest_possible",
                "preferred_stack": ["python"],
                "engineering_principles": ["Entregar rapido sem quebrar requisitos"],
                "modules": ["api_design"],
                "constraints": {
                    "allow_dependency_install": True,
                    "allow_external_network": False,
                    "allow_schema_change": True,
                    "max_runtime_minutes": 15,
                },
                "memory": {"slots": []},
                "limits": {"max_files_edited": 10, "max_runs": 5},
            },
        )

        create_run_response = self.client.post(
            "/api/v1/runs/",
            json={
                "quest_id": "quest_hello_world",
                "agent_profile_id": "speedster",
            },
        )

        self.assertEqual(create_run_response.status_code, 201)
        payload = create_run_response.json()
        self.assertEqual(payload["status"], "completed")
        self.assertEqual(payload["quest_id"], "quest_hello_world")
        self.assertEqual(payload["agent_profile_id"], "speedster")
        self.assertIn("summary", payload)
        self.assertGreaterEqual(payload["summary"]["technical_score"], 0)
        self.assertIn("artifacts", payload["summary"])
        self.assertIn("stdout_log", payload["summary"]["artifacts"])
        self.assertIn("workspace", payload["summary"]["artifacts"])
        self.assertIn("provider 'local-process'", payload["summary"]["notes"][1])
        self.assertTrue(
            any("Starter copiado para workspace isolado" in note for note in payload["summary"]["notes"])
        )

        replay_response = self.client.get(f"/api/v1/runs/{payload['id']}/replay")
        self.assertEqual(replay_response.status_code, 200)
        self.assertGreaterEqual(len(replay_response.json()), 4)

        artifacts_response = self.client.get(f"/api/v1/runs/{payload['id']}/artifacts")
        self.assertEqual(artifacts_response.status_code, 200)
        self.assertTrue(any(item["name"] == "workspace_diff" for item in artifacts_response.json()))

        artifact_response = self.client.get(
            f"/api/v1/runs/{payload['id']}/artifacts/workspace_diff"
        )
        self.assertEqual(artifact_response.status_code, 200)
        self.assertIn("No changes", artifact_response.json()["content"])

        post_mortem_response = self.client.get(f"/api/v1/runs/{payload['id']}/post-mortem")
        self.assertEqual(post_mortem_response.status_code, 200)
        self.assertIn("claude_analysis", post_mortem_response.json())

        ranking_response = self.client.get("/api/v1/rankings/quests/quest_hello_world")
        self.assertEqual(ranking_response.status_code, 200)
        self.assertEqual(ranking_response.json()[0]["agent_profile_id"], "speedster")
        self.assertIn("Politica de hardening ativa", payload["summary"]["notes"][2])

    def test_workspace_override_changes_diff_and_score(self) -> None:
        self.client.post(
            "/api/v1/profiles/",
            json={
                "id": "mutator",
                "name": "Mutator",
                "archetype": "architect",
                "planning_style": "tests_first",
                "preferred_stack": ["python"],
                "engineering_principles": ["Preservar requisitos"],
                "modules": ["api_design"],
                "constraints": {
                    "allow_dependency_install": True,
                    "allow_external_network": False,
                    "allow_schema_change": True,
                    "max_runtime_minutes": 15,
                },
                "memory": {"slots": []},
                "limits": {"max_files_edited": 10, "max_runs": 5},
            },
        )

        create_run_response = self.client.post(
            "/api/v1/runs/",
            json={
                "quest_id": "quest_hello_world",
                "agent_profile_id": "mutator",
                "workspace_files": {
                    "app/main.py": (
                        "from fastapi import FastAPI\n\n"
                        "app = FastAPI()\n\n"
                        "@app.get('/hello')\n"
                        "def hello() -> dict[str, str]:\n"
                        "    return {'message': 'Oops'}\n"
                    )
                },
            },
        )

        self.assertEqual(create_run_response.status_code, 201)
        payload = create_run_response.json()
        self.assertLess(payload["summary"]["technical_score"], 100.0)
        self.assertTrue(
            any("Arquivos sobrescritos antes da execucao" in note for note in payload["summary"]["notes"])
        )

        artifact_response = self.client.get(
            f"/api/v1/runs/{payload['id']}/artifacts/workspace_diff"
        )
        self.assertEqual(artifact_response.status_code, 200)
        self.assertIn("Oops", artifact_response.json()["content"])

        replay_response = self.client.get(f"/api/v1/runs/{payload['id']}/replay")
        self.assertEqual(replay_response.status_code, 200)
        self.assertTrue(any(item["type"] == "FILE_CHANGED" for item in replay_response.json()))

    def test_rejects_run_when_dependencies_do_not_exist(self) -> None:
        response = self.client.post(
            "/api/v1/runs/",
            json={
                "quest_id": "missing-quest",
                "agent_profile_id": "missing-profile",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("not found", response.json()["detail"])

    def test_rejects_profiles_that_request_external_network(self) -> None:
        self.client.post(
            "/api/v1/profiles/",
            json={
                "id": "unsafe",
                "name": "Unsafe",
                "archetype": "speedrunner",
                "planning_style": "simplest_possible",
                "preferred_stack": ["python"],
                "engineering_principles": ["Entregar rapido"],
                "modules": ["api_design"],
                "constraints": {
                    "allow_dependency_install": True,
                    "allow_external_network": True,
                    "allow_schema_change": True,
                    "max_runtime_minutes": 10,
                },
                "memory": {"slots": []},
                "limits": {"max_files_edited": 10, "max_runs": 5},
            },
        )

        response = self.client.post(
            "/api/v1/runs/",
            json={
                "quest_id": "quest_bugfix_headers",
                "agent_profile_id": "unsafe",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("external network access", response.json()["detail"])

    def test_cors_preflight_is_allowed_for_frontend_origin(self) -> None:
        response = self.client.options(
            "/api/v1/quests/",
            headers={
                "Origin": "http://localhost:4200",
                "Access-Control-Request-Method": "GET",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"], "http://localhost:4200")


if __name__ == "__main__":
    unittest.main()
