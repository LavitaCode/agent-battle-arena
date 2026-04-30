import unittest

from fastapi.testclient import TestClient

from app.main import app


class HelloWorldHiddenTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_only_message_key_is_returned(self) -> None:
        response = self.client.get("/hello")
        self.assertEqual(list(response.json().keys()), ["message"])
