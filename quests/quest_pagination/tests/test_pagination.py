import unittest

from fastapi.testclient import TestClient

from app.main import app


class PaginationQuestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_default_page_returns_10_items(self) -> None:
        response = self.client.get("/products")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["items"]), 10)

    def test_response_contains_pagination_metadata(self) -> None:
        response = self.client.get("/products")
        data = response.json()
        for key in ("total", "page", "page_size", "pages"):
            self.assertIn(key, data, msg=f"Missing field: {key}")

    def test_page_size_param_is_respected(self) -> None:
        response = self.client.get("/products", params={"page_size": 5})
        self.assertEqual(len(response.json()["items"]), 5)

    def test_page_beyond_range_returns_empty_items(self) -> None:
        response = self.client.get("/products", params={"page": 999})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items"], [])
