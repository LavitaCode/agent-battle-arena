import unittest

from fastapi.testclient import TestClient

from app.main import app


class PaginationHiddenTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_page_size_above_100_returns_422(self) -> None:
        response = self.client.get("/products", params={"page_size": 101})
        self.assertEqual(response.status_code, 422)

    def test_page_zero_returns_422(self) -> None:
        response = self.client.get("/products", params={"page": 0})
        self.assertEqual(response.status_code, 422)

    def test_second_page_contains_different_items(self) -> None:
        page1 = self.client.get("/products", params={"page": 1, "page_size": 10}).json()
        page2 = self.client.get("/products", params={"page": 2, "page_size": 10}).json()
        ids_p1 = {i["id"] for i in page1["items"]}
        ids_p2 = {i["id"] for i in page2["items"]}
        self.assertTrue(ids_p1.isdisjoint(ids_p2))

    def test_total_reflects_full_dataset(self) -> None:
        response = self.client.get("/products")
        self.assertEqual(response.json()["total"], 50)
