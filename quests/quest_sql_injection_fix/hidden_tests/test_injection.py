import unittest

from fastapi.testclient import TestClient

from app.main import app


class InjectionHiddenTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_classic_tautology_injection_returns_empty(self) -> None:
        # "' OR '1'='1" retornaria todos os usuários em código vulnerável
        response = self.client.get("/users", params={"name": "' OR '1'='1"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["users"], [])

    def test_union_injection_does_not_leak_data(self) -> None:
        payload = "alice' UNION SELECT 1, 'hacked"
        response = self.client.get("/users", params={"name": payload})
        self.assertEqual(response.status_code, 200)
        users = response.json()["users"]
        for u in users:
            self.assertNotEqual(u.get("name"), "hacked")
