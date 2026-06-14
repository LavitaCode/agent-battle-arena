import unittest

from fastapi.testclient import TestClient

from app.main import app


class OrdersQuestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_valid_order_returns_201(self) -> None:
        response = self.client.post(
            "/orders", json={"product": "widget", "price": 9.99}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["product"], "widget")

    def test_missing_product_returns_422(self) -> None:
        response = self.client.post("/orders", json={"price": 9.99})
        self.assertEqual(response.status_code, 422)

    def test_missing_price_returns_422(self) -> None:
        response = self.client.post("/orders", json={"product": "widget"})
        self.assertEqual(response.status_code, 422)
