"""Tests for LLM executor infrastructure (no real API calls)."""
import json
import unittest
from unittest.mock import MagicMock, patch

from backend.app.executors.base import AgentExecutor
from backend.app.executors.prompt import build_user_prompt, parse_response, SYSTEM_PROMPT
from backend.app.executors.registry import get_executor
from backend.app.executors.ollama_executor import OllamaExecutor
from backend.app.executors.claude_executor import ClaudeExecutor
from backend.app.executors.openai_executor import OpenAIExecutor


# ---------------------------------------------------------------------------
# Prompt helpers
# ---------------------------------------------------------------------------

class PromptHelpersTest(unittest.TestCase):
    def _make_quest(self):
        q = MagicMock()
        q.title = "Hello World API"
        q.description = "Build a simple API."
        q.requirements = ["Return JSON", "Status 200"]
        q.forbidden_actions = ["No hardcoding"]
        return q

    def test_build_user_prompt_contains_title(self):
        q = self._make_quest()
        prompt = build_user_prompt(q, {"app/main.py": "# starter"})
        self.assertIn("Hello World API", prompt)

    def test_build_user_prompt_contains_starter_file(self):
        q = self._make_quest()
        prompt = build_user_prompt(q, {"app/main.py": "# starter code"})
        self.assertIn("# starter code", prompt)

    def test_parse_response_valid_json(self):
        raw = json.dumps({"workspace_files": {"app/main.py": "print('hi')"}})
        result = parse_response(raw)
        self.assertEqual(result, {"app/main.py": "print('hi')"})

    def test_parse_response_strips_markdown_fences(self):
        raw = "```json\n" + json.dumps({"workspace_files": {"f.py": "x=1"}}) + "\n```"
        result = parse_response(raw)
        self.assertEqual(result, {"f.py": "x=1"})

    def test_parse_response_returns_empty_on_invalid_json(self):
        self.assertEqual(parse_response("not json at all"), {})

    def test_parse_response_returns_empty_on_missing_key(self):
        self.assertEqual(parse_response('{"other": "stuff"}'), {})

    def test_parse_response_rejects_non_string_values(self):
        raw = json.dumps({"workspace_files": {"f.py": 42}})
        self.assertEqual(parse_response(raw), {})


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class ExecutorRegistryTest(unittest.TestCase):
    def test_unknown_executor_returns_none(self):
        self.assertIsNone(get_executor("nonexistent"))

    def test_claude_without_api_key_returns_none(self):
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": ""}):
            self.assertIsNone(get_executor("claude"))

    def test_openai_without_api_key_returns_none(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}):
            self.assertIsNone(get_executor("openai"))

    def test_ollama_always_returns_executor(self):
        executor = get_executor("ollama")
        self.assertIsNotNone(executor)
        self.assertEqual(executor.name, "ollama")

    def test_claude_with_api_key_returns_executor(self):
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
            executor = get_executor("claude")
        self.assertIsNotNone(executor)
        self.assertEqual(executor.name, "claude")


# ---------------------------------------------------------------------------
# Executor: Claude (mocked SDK)
# ---------------------------------------------------------------------------

class ClaudeExecutorTest(unittest.TestCase):
    def _make_quest(self):
        q = MagicMock()
        q.id = "quest_hello_world"
        q.title = "Hello"
        q.description = "desc"
        q.requirements = []
        q.forbidden_actions = []
        return q

    def test_returns_empty_without_api_key(self):
        ex = ClaudeExecutor(api_key="")
        result = ex.execute(self._make_quest(), {})
        self.assertEqual(result, {})

    def test_calls_api_and_parses_response(self):
        valid_response = json.dumps({"workspace_files": {"app/main.py": "code"}})
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text=valid_response)]
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_msg

        mock_anthropic = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            ex = ClaudeExecutor(api_key="sk-test")
            result = ex.execute(self._make_quest(), {"app/main.py": "# starter"})

        self.assertEqual(result, {"app/main.py": "code"})

    def test_returns_empty_on_exception(self):
        mock_anthropic = MagicMock()
        mock_anthropic.Anthropic.side_effect = RuntimeError("boom")
        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            ex = ClaudeExecutor(api_key="sk-test")
            result = ex.execute(self._make_quest(), {})
        self.assertEqual(result, {})


# ---------------------------------------------------------------------------
# Executor: Ollama (mocked urllib)
# ---------------------------------------------------------------------------

class OllamaExecutorTest(unittest.TestCase):
    def _make_quest(self):
        q = MagicMock()
        q.id = "quest_hello_world"
        q.title = "Hello"
        q.description = "desc"
        q.requirements = []
        q.forbidden_actions = []
        return q

    def _mock_response(self, content: str):
        body = json.dumps({"message": {"content": content}}).encode()
        mock = MagicMock()
        mock.read.return_value = body
        mock.__enter__ = lambda s: s
        mock.__exit__ = MagicMock(return_value=False)
        return mock

    def test_returns_parsed_workspace_files(self):
        valid = json.dumps({"workspace_files": {"app/main.py": "code"}})
        with patch("backend.app.executors.ollama_executor.urlopen", return_value=self._mock_response(valid)):
            ex = OllamaExecutor()
            result = ex.execute(self._make_quest(), {})
        self.assertEqual(result, {"app/main.py": "code"})

    def test_returns_empty_when_unreachable(self):
        from urllib.error import URLError
        with patch("backend.app.executors.ollama_executor.urlopen", side_effect=URLError("refused")):
            ex = OllamaExecutor()
            result = ex.execute(self._make_quest(), {})
        self.assertEqual(result, {})
