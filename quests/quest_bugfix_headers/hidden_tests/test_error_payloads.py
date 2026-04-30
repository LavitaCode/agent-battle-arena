import unittest

from fastapi.testclient import TestClient

from app.main import app


class BugfixHeadersHiddenTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_status_does_not_return_unexpected_fields(self) -> None:
        response = self.client.get("/status")
        self.assertEqual(set(response.json().keys()), {"ok"})
