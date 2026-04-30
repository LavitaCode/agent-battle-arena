import unittest

from fastapi.testclient import TestClient

from app.main import app


class HelloWorldQuestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_get_hello_returns_expected_payload(self) -> None:
        response = self.client.get("/hello")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Hello, World!"})

    def test_get_hello_returns_json_content_type(self) -> None:
        response = self.client.get("/hello")
        self.assertIn("application/json", response.headers["content-type"])
