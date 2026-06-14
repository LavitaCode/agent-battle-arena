import unittest

from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app


class RetryHiddenTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        main_module._upstream_caller = None

    def test_exactly_three_attempts_are_made(self) -> None:
        call_count = [0]

        def count_and_fail() -> dict:
            call_count[0] += 1
            raise RuntimeError("always down")

        main_module._upstream_caller = count_and_fail
        self.client.get("/fetch")
        self.assertEqual(call_count[0], 3)

    def test_success_on_second_attempt_returns_200(self) -> None:
        attempts = [0]

        def fail_once() -> dict:
            attempts[0] += 1
            if attempts[0] == 1:
                raise RuntimeError("first fail")
            return {"data": "ok"}

        main_module._upstream_caller = fail_once
        response = self.client.get("/fetch")
        self.assertEqual(response.status_code, 200)
