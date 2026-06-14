"""Unit tests for ArenaClient using urllib mock (no server required)."""
import json
import unittest
from io import BytesIO
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from arena_sdk import ArenaClient, AuthError, NotFoundError, RateLimitError, ValidationError
from arena_sdk.models import Battle, BattleResult, Quest


def _mock_response(data: dict, status: int = 200):
    body = json.dumps(data).encode()
    mock = MagicMock()
    mock.read.return_value = body
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    return mock


def _http_error(code: int, detail: str = "error"):
    body = json.dumps({"detail": detail}).encode()
    return HTTPError(url="http://test", code=code, msg="", hdrs={}, fp=BytesIO(body))


class ArenaClientBattlesTest(unittest.TestCase):
    def setUp(self):
        self.client = ArenaClient("http://localhost:8000", token="session=tok")

    def test_battles_create_returns_battle(self):
        raw = {"id": "b1", "quest_id": "quest_hello_world", "status": "open", "created_by_user_id": "u1"}
        with patch("arena_sdk.client.urlopen", return_value=_mock_response(raw)):
            battle = self.client.battles.create("quest_hello_world", "p1", {})
        self.assertIsInstance(battle, Battle)
        self.assertEqual(battle.id, "b1")
        self.assertEqual(battle.status, "open")

    def test_battles_result_returns_battle_result(self):
        raw = {
            "battle_id": "b1",
            "winner_participant_id": "p-left",
            "score_left": 85.0,
            "score_right": 70.0,
            "summary": "left won",
        }
        with patch("arena_sdk.client.urlopen", return_value=_mock_response(raw)):
            result = self.client.battles.result("b1")
        self.assertIsInstance(result, BattleResult)
        self.assertEqual(result.winner_participant_id, "p-left")
        self.assertAlmostEqual(result.score_left, 85.0)

    def test_wait_result_polls_until_completed(self):
        open_raw = {"id": "b1", "quest_id": "q", "status": "running", "created_by_user_id": "u"}
        done_raw = {"id": "b1", "quest_id": "q", "status": "completed", "created_by_user_id": "u"}
        result_raw = {"battle_id": "b1", "winner_participant_id": None, "score_left": 0, "score_right": 0, "summary": "tie"}
        responses = [open_raw, done_raw, result_raw]
        idx = [0]

        def fake_urlopen(req, timeout=30):
            r = responses[idx[0]]
            idx[0] += 1
            return _mock_response(r)

        with patch("arena_sdk.client.urlopen", side_effect=fake_urlopen):
            with patch("arena_sdk.client.time.sleep"):
                result = self.client.battles.wait_result("b1", timeout=60, poll_interval=0.01)
        self.assertIsInstance(result, BattleResult)

    def test_raises_auth_error_on_401(self):
        with patch("arena_sdk.client.urlopen", side_effect=_http_error(401, "unauthorized")):
            with self.assertRaises(AuthError):
                self.client.battles.get("b1")

    def test_raises_not_found_on_404(self):
        with patch("arena_sdk.client.urlopen", side_effect=_http_error(404, "not found")):
            with self.assertRaises(NotFoundError):
                self.client.battles.get("missing")

    def test_raises_rate_limit_on_429(self):
        with patch("arena_sdk.client.urlopen", side_effect=_http_error(429, "slow down")):
            with self.assertRaises(RateLimitError):
                self.client.battles.create("q", "p", {})

    def test_raises_validation_error_on_422(self):
        with patch("arena_sdk.client.urlopen", side_effect=_http_error(422, "bad payload")):
            with self.assertRaises(ValidationError):
                self.client.battles.create("q", "p", {})


class ArenaClientQuestsTest(unittest.TestCase):
    def setUp(self):
        self.client = ArenaClient("http://localhost:8000")

    def test_quests_list_returns_quest_objects(self):
        raw = [
            {"id": "quest_hello_world", "title": "Hello World", "difficulty": "bronze", "cognitive_layers": ["C1", "C2"]},
            {"id": "quest_pagination", "title": "Pagination", "difficulty": "silver", "cognitive_layers": ["C3", "C5"]},
        ]
        with patch("arena_sdk.client.urlopen", return_value=_mock_response(raw)):
            quests = self.client.quests.list()
        self.assertEqual(len(quests), 2)
        self.assertIsInstance(quests[0], Quest)
        self.assertEqual(quests[0].cognitive_layers, ["C1", "C2"])

    def test_quests_get_returns_single_quest(self):
        raw = {"id": "quest_hello_world", "title": "Hello World", "difficulty": "bronze", "cognitive_layers": []}
        with patch("arena_sdk.client.urlopen", return_value=_mock_response(raw)):
            q = self.client.quests.get("quest_hello_world")
        self.assertEqual(q.id, "quest_hello_world")
