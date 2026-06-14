import unittest

from fastapi.testclient import TestClient

from app.main import app


class OrdersHiddenTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_empty_body_returns_422(self) -> None:
        response = self.client.post("/orders", json={})
        self.assertEqual(response.status_code, 422)

    def test_price_must_be_numeric(self) -> None:
        response = self.client.post(
            "/orders", json={"product": "widget", "price": "free"}
        )
        self.assertEqual(response.status_code, 422)

    def test_valid_order_contains_status_created(self) -> None:
        response = self.client.post(
            "/orders", json={"product": "gadget", "price": 19.99}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "created")
