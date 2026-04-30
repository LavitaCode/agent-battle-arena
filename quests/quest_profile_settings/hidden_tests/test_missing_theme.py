import unittest

from fastapi.testclient import TestClient

from app.main import app


class ProfileSettingsHiddenTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_missing_theme_is_rejected(self) -> None:
        response = self.client.post("/profile/settings", json={"notifications": True})
        self.assertEqual(response.status_code, 422)
