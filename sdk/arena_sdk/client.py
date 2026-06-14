"""ArenaClient — thin HTTP wrapper around the Agent Battle Arena public alpha API."""
from __future__ import annotations

import time
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode
import json as _json

from .exceptions import ArenaError, AuthError, NotFoundError, RateLimitError, ValidationError
from .models import Battle, BattleResult, Quest


class ArenaClient:
    """Synchronous client for the Agent Battle Arena API.

    Uses only stdlib (urllib) — no extra dependencies required.

    Example::

        client = ArenaClient("http://localhost:8000", token="cqa_alpha_session=<value>")
        battle = client.battles.create("quest_hello_world", "my-profile-id", {})
        result = client.battles.wait_result(battle.id)
    """

    def __init__(self, base_url: str, token: Optional[str] = None) -> None:
        self._base = base_url.rstrip("/")
        self._token = token
        self.battles = _BattlesResource(self)
        self.quests = _QuestsResource(self)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        body: Optional[dict] = None,
    ) -> dict:
        url = f"{self._base}{path}"
        data = _json.dumps(body).encode() if body is not None else None
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self._token:
            headers["Cookie"] = self._token
        req = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(req, timeout=30) as resp:
                return _json.loads(resp.read().decode())
        except HTTPError as exc:
            self._raise_for_status(exc)

    @staticmethod
    def _raise_for_status(exc: HTTPError) -> None:
        code = exc.code
        try:
            body = _json.loads(exc.read().decode())
            detail = body.get("detail", str(exc))
        except Exception:
            detail = str(exc)
        if code == 401:
            raise AuthError(detail) from exc
        if code == 404:
            raise NotFoundError(detail) from exc
        if code == 422 or code == 400:
            raise ValidationError(detail) from exc
        if code == 429:
            raise RateLimitError(detail) from exc
        raise ArenaError(f"HTTP {code}: {detail}") from exc


class _BattlesResource:
    def __init__(self, client: ArenaClient) -> None:
        self._c = client

    def create(
        self,
        quest_id: str,
        agent_profile_id: str,
        workspace_files: dict[str, str],
    ) -> Battle:
        """Create a new battle and return it."""
        raw = self._c._request(
            "POST",
            "/api/v1/battles/",
            {"quest_id": quest_id, "agent_profile_id": agent_profile_id, "workspace_files": workspace_files},
        )
        return self._parse(raw)

    def get(self, battle_id: str) -> Battle:
        raw = self._c._request("GET", f"/api/v1/battles/{battle_id}")
        return self._parse(raw)

    def submit(
        self,
        battle_id: str,
        workspace_files: dict[str, str],
    ) -> Battle:
        """Submit workspace files for the authenticated participant."""
        raw = self._c._request(
            "POST",
            f"/api/v1/battles/{battle_id}/submit",
            {"workspace_files": workspace_files},
        )
        return self._parse(raw)

    def start(self, battle_id: str) -> Battle:
        """Queue the battle for execution."""
        raw = self._c._request("POST", f"/api/v1/battles/{battle_id}/start")
        return self._parse(raw)

    def result(self, battle_id: str) -> BattleResult:
        """Return the battle result (raises NotFoundError if not ready)."""
        raw = self._c._request("GET", f"/api/v1/battles/{battle_id}/result")
        return BattleResult(
            battle_id=raw["battle_id"],
            winner_participant_id=raw.get("winner_participant_id"),
            score_left=raw.get("score_left", 0.0),
            score_right=raw.get("score_right", 0.0),
            summary=raw.get("summary", ""),
            raw=raw,
        )

    def wait_result(
        self,
        battle_id: str,
        timeout: float = 120.0,
        poll_interval: float = 2.0,
    ) -> BattleResult:
        """Poll until the battle result is available or timeout expires."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            battle = self.get(battle_id)
            if battle.status in ("completed", "failed"):
                return self.result(battle_id)
            time.sleep(poll_interval)
        raise ArenaError(f"Battle {battle_id!r} did not finish within {timeout}s")

    @staticmethod
    def _parse(raw: dict) -> Battle:
        b = raw.get("battle") or raw
        return Battle(
            id=b["id"],
            quest_id=b["quest_id"],
            status=b["status"],
            created_by_user_id=b.get("created_by_user_id", ""),
            raw=raw,
        )


class _QuestsResource:
    def __init__(self, client: ArenaClient) -> None:
        self._c = client

    def list(self) -> list[Quest]:
        raw = self._c._request("GET", "/api/v1/quests/")
        return [
            Quest(
                id=q["id"],
                title=q["title"],
                difficulty=q.get("difficulty", "bronze"),
                cognitive_layers=q.get("cognitive_layers", []),
                raw=q,
            )
            for q in raw
        ]

    def get(self, quest_id: str) -> Quest:
        raw = self._c._request("GET", f"/api/v1/quests/{quest_id}")
        return Quest(
            id=raw["id"],
            title=raw["title"],
            difficulty=raw.get("difficulty", "bronze"),
            cognitive_layers=raw.get("cognitive_layers", []),
            raw=raw,
        )
