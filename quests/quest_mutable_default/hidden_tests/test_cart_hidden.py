import unittest

from fastapi.testclient import TestClient

from app.main import app


class CartHiddenTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_empty_items_returns_empty_cart(self) -> None:
        response = self.client.post("/cart/add", json={"items": []})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["cart"], [])

    def test_three_sequential_requests_are_independent(self) -> None:
        for item in ["x", "y", "z"]:
            response = self.client.post("/cart/add", json={"items": [item]})
            self.assertEqual(response.json()["cart"], [item])
