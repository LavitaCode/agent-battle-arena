import unittest

from fastapi.testclient import TestClient

from app.main import app


class ProfileSettingsVisibleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_profile_settings_returns_created(self) -> None:
        response = self.client.post(
            "/profile/settings",
            json={"theme": "dark", "notifications": True},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"status": "saved"})
