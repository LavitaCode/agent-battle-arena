"""PostgreSQL integration tests for AlphaStore.

These tests run only when CQA_DATABASE_URL points to a real PostgreSQL instance.
In CI the database is provided by the postgres service container.
Locally they are skipped unless the env var is set.
"""
import os
import unittest
from uuid import uuid4

from backend.app.services.alpha_store import AlphaStore

_PG_URL = os.getenv("CQA_DATABASE_URL", "")
_SKIP_REASON = "CQA_DATABASE_URL not set — skipping PostgreSQL integration tests"


def _pg_url() -> str:
    return _PG_URL


@unittest.skipUnless(
    _PG_URL.startswith(("postgres://", "postgresql://")),
    _SKIP_REASON,
)
class PostgresAlphaStoreTestCase(unittest.TestCase):
    """Smoke-test AlphaStore against a live PostgreSQL database."""

    def setUp(self) -> None:
        self.store = AlphaStore(db_path="/tmp/unused.sqlite3", database_url=_pg_url())
        self._suffix = uuid4().hex[:8]

    # ------------------------------------------------------------------
    # Auth flow
    # ------------------------------------------------------------------

    def test_create_and_resolve_auth_state(self) -> None:
        login = f"user_{self._suffix}"
        state = self.store.create_auth_state(login, "ALPHA-ACCESS")
        self.assertIsNotNone(state)
        resolved = self.store.get_auth_state(state)
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved["github_login"], login)

    def test_consume_auth_state_removes_it(self) -> None:
        login = f"ghost_{self._suffix}"
        state = self.store.create_auth_state(login, "ALPHA-ACCESS")
        self.store.consume_auth_state(state)
        self.assertIsNone(self.store.get_auth_state(state))

    # ------------------------------------------------------------------
    # User upsert
    # ------------------------------------------------------------------

    def test_upsert_user_twice_returns_same_id(self) -> None:
        login = f"dup_{self._suffix}"
        u1 = self.store.upsert_user(login)
        u2 = self.store.upsert_user(login)
        self.assertEqual(u1.id, u2.id)

    # ------------------------------------------------------------------
    # Battle lifecycle
    # ------------------------------------------------------------------

    def test_full_battle_lifecycle(self) -> None:
        user_a = self.store.upsert_user(f"player_a_{self._suffix}")
        user_b = self.store.upsert_user(f"player_b_{self._suffix}")

        battle = self.store.create_battle(user_a.id, "quest_hello_world")
        self.assertEqual(battle.status, "open")

        self.store.create_or_replace_participant(
            battle.id, user_a.id, "profile-a", "left", {}
        )
        self.store.create_or_replace_participant(
            battle.id, user_b.id, "profile-b", "right", {}
        )
        self.store.update_battle_status(battle.id, "completed")

        refreshed = self.store.get_battle(battle.id)
        self.assertEqual(refreshed.status, "completed")

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def test_session_create_and_retrieve(self) -> None:
        user = self.store.upsert_user(f"session_user_{self._suffix}")
        token = self.store.create_session(user.id)
        self.assertIsNotNone(token)
        fetched = self.store.get_user_by_session(token)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.id, user.id)

    # ------------------------------------------------------------------
    # Backend flag
    # ------------------------------------------------------------------

    def test_store_reports_postgres_backend(self) -> None:
        self.assertEqual(self.store._backend, "postgres")
