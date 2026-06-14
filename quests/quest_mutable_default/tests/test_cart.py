import unittest

from fastapi.testclient import TestClient

from app.main import app


class CartQuestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_single_request_returns_submitted_items(self) -> None:
        response = self.client.post("/cart/add", json={"items": ["apple", "banana"]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["cart"], ["apple", "banana"])

    def test_second_request_does_not_accumulate_first(self) -> None:
        self.client.post("/cart/add", json={"items": ["apple"]})
        response = self.client.post("/cart/add", json={"items": ["mango"]})
        self.assertEqual(response.json()["cart"], ["mango"])
