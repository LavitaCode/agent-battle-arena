"""Unit tests for multi-language Docker runner image selection."""
import unittest
from unittest.mock import patch, MagicMock

from backend.app.sandbox.runner import DockerSandboxProvider
from backend.app.models.quest import Quest


def _make_quest(language: str = "python") -> Quest:
    return Quest(
        id="test-quest",
        title="Test Quest",
        description="A test quest",
        language=language,
    )


class MultiLangRunnerImageSelectionTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.provider = DockerSandboxProvider()

    def test_python_quest_uses_python_image(self) -> None:
        quest = _make_quest("python")
        with patch("backend.app.sandbox.runner.settings") as mock_settings:
            mock_settings.RUNNER_IMAGE_PYTHON = "cqa-runner-python:latest"
            mock_settings.RUNNER_IMAGE_JAVASCRIPT = "cqa-runner-javascript:latest"
            mock_settings.RUNNER_IMAGE_GO = "cqa-runner-go:latest"
            mock_settings.RUNNER_IMAGE_RUST = "cqa-runner-rust:latest"
            image = self.provider._runner_image(quest)
        self.assertEqual(image, "cqa-runner-python:latest")

    def test_javascript_quest_uses_javascript_image(self) -> None:
        quest = _make_quest("javascript")
        with patch("backend.app.sandbox.runner.settings") as mock_settings:
            mock_settings.RUNNER_IMAGE_PYTHON = "cqa-runner-python:latest"
            mock_settings.RUNNER_IMAGE_JAVASCRIPT = "cqa-runner-javascript:latest"
            mock_settings.RUNNER_IMAGE_GO = "cqa-runner-go:latest"
            mock_settings.RUNNER_IMAGE_RUST = "cqa-runner-rust:latest"
            image = self.provider._runner_image(quest)
        self.assertEqual(image, "cqa-runner-javascript:latest")

    def test_go_quest_uses_go_image(self) -> None:
        quest = _make_quest("go")
        with patch("backend.app.sandbox.runner.settings") as mock_settings:
            mock_settings.RUNNER_IMAGE_PYTHON = "cqa-runner-python:latest"
            mock_settings.RUNNER_IMAGE_JAVASCRIPT = "cqa-runner-javascript:latest"
            mock_settings.RUNNER_IMAGE_GO = "cqa-runner-go:latest"
            mock_settings.RUNNER_IMAGE_RUST = "cqa-runner-rust:latest"
            image = self.provider._runner_image(quest)
        self.assertEqual(image, "cqa-runner-go:latest")

    def test_rust_quest_uses_rust_image(self) -> None:
        quest = _make_quest("rust")
        with patch("backend.app.sandbox.runner.settings") as mock_settings:
            mock_settings.RUNNER_IMAGE_PYTHON = "cqa-runner-python:latest"
            mock_settings.RUNNER_IMAGE_JAVASCRIPT = "cqa-runner-javascript:latest"
            mock_settings.RUNNER_IMAGE_GO = "cqa-runner-go:latest"
            mock_settings.RUNNER_IMAGE_RUST = "cqa-runner-rust:latest"
            image = self.provider._runner_image(quest)
        self.assertEqual(image, "cqa-runner-rust:latest")

    def test_unknown_language_falls_back_to_python(self) -> None:
        quest = _make_quest("cobol")
        with patch("backend.app.sandbox.runner.settings") as mock_settings:
            mock_settings.RUNNER_IMAGE_PYTHON = "cqa-runner-python:latest"
            mock_settings.RUNNER_IMAGE_JAVASCRIPT = "cqa-runner-javascript:latest"
            mock_settings.RUNNER_IMAGE_GO = "cqa-runner-go:latest"
            mock_settings.RUNNER_IMAGE_RUST = "cqa-runner-rust:latest"
            image = self.provider._runner_image(quest)
        self.assertEqual(image, "cqa-runner-python:latest")

    def test_language_field_defaults_to_python(self) -> None:
        quest = Quest(
            id="default-quest",
            title="Default Quest",
            description="No language specified",
        )
        self.assertEqual(quest.language, "python")


if __name__ == "__main__":
    unittest.main()
