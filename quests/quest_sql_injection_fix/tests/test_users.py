import unittest

from fastapi.testclient import TestClient

from app.main import app


class UsersQuestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_search_by_exact_name_returns_user(self) -> None:
        response = self.client.get("/users", params={"name": "alice"})
        self.assertEqual(response.status_code, 200)
        users = response.json()["users"]
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["name"], "alice")

    def test_unknown_name_returns_empty(self) -> None:
        response = self.client.get("/users", params={"name": "nobody"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["users"], [])
