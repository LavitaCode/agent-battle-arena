import unittest

from fastapi.testclient import TestClient

from app.main import app


class BugfixHeadersVisibleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_status_returns_expected_payload(self) -> None:
        response = self.client.get("/status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": "true"})

    def test_status_returns_json_header(self) -> None:
        response = self.client.get("/status")
        self.assertIn("application/json", response.headers["content-type"])
