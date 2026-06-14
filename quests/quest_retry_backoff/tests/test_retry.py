import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app


class RetryQuestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        main_module._upstream_caller = None

    def test_healthy_upstream_returns_200(self) -> None:
        response = self.client.get("/fetch")
        self.assertEqual(response.status_code, 200)

    def test_always_failing_upstream_returns_503(self) -> None:
        call_count = 0

        def always_fail() -> dict:
            nonlocal call_count
            call_count += 1
            raise RuntimeError("upstream down")

        main_module._upstream_caller = always_fail
        response = self.client.get("/fetch")
        self.assertEqual(response.status_code, 503)

    def test_upstream_succeeds_on_third_attempt(self) -> None:
        attempts = [0]

        def fail_twice() -> dict:
            attempts[0] += 1
            if attempts[0] < 3:
                raise RuntimeError("transient")
            return {"data": "recovered"}

        main_module._upstream_caller = fail_twice
        response = self.client.get("/fetch")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], "recovered")
