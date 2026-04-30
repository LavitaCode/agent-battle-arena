"""SQLite-backed store for the public alpha battle domain."""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional
from uuid import uuid4

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover - exercised only when Postgres is configured without deps.
    psycopg = None
    dict_row = None

from ..core.config import settings
from ..models import (
    AccessInvite,
    AgentProfile,
    AgentProfileCreate,
    AgentProfileUpdate,
    AgentTemplate,
    Battle,
    BattleDetail,
    BattleParticipant,
    BattleResult,
    BattleRunBundle,
    BattleReplayBundle,
    LeaderboardEntry,
    PostMortem,
    ReplayEvent,
    Run,
    SessionUserResponse,
    User,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


ALPHA_SCHEMA_MIGRATIONS: tuple[dict[str, str], ...] = (
    {
        "version": "1",
        "name": "initial_alpha_schema",
        "sql": """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                github_login TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                role TEXT NOT NULL,
                alpha_status TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS invites (
                code TEXT PRIMARY KEY,
                email_or_login TEXT NOT NULL,
                status TEXT NOT NULL,
                expires_at TEXT,
                used_by_user_id TEXT
            );
            CREATE TABLE IF NOT EXISTS auth_states (
                state TEXT PRIMARY KEY,
                github_login TEXT NOT NULL,
                invite_code TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS agent_templates (
                id TEXT PRIMARY KEY,
                payload TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS agent_profiles (
                id TEXT PRIMARY KEY,
                owner_user_id TEXT,
                template_id TEXT,
                visibility TEXT NOT NULL,
                version INTEGER NOT NULL,
                payload TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS battles (
                id TEXT PRIMARY KEY,
                quest_id TEXT NOT NULL,
                status TEXT NOT NULL,
                created_by_user_id TEXT NOT NULL,
                battle_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT
            );
            CREATE TABLE IF NOT EXISTS battle_participants (
                id TEXT PRIMARY KEY,
                battle_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                agent_profile_id TEXT NOT NULL,
                seat TEXT NOT NULL,
                submission_status TEXT NOT NULL,
                workspace_files TEXT NOT NULL,
                run_id TEXT,
                joined_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS battle_results (
                battle_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS battle_run_bundles (
                participant_id TEXT PRIMARY KEY,
                battle_id TEXT NOT NULL,
                payload TEXT NOT NULL
            );
            """,
    },
)


class AlphaStore:
    """Persist public alpha data in SQLite locally or PostgreSQL/Neon in alpha."""

    def __init__(self, db_path: str, database_url: str = "") -> None:
        self._database_url = database_url
        self._backend = "postgres" if database_url.startswith(("postgres://", "postgresql://")) else "sqlite"
        self._db_path = Path(db_path)
        if self._backend == "sqlite":
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
        elif psycopg is None:
            raise RuntimeError("PostgreSQL storage requires psycopg. Install requirements.txt first.")
        self._initialize()
        self.seed_defaults()

    @contextmanager
    def _connect(self) -> Iterator["_ConnectionAdapter"]:
        if self._backend == "postgres":
            connection = psycopg.connect(self._database_url, row_factory=dict_row)  # type: ignore[union-attr]
            adapter = _ConnectionAdapter(connection, self._backend)
        else:
            connection = sqlite3.connect(self._db_path)
            connection.row_factory = sqlite3.Row
            adapter = _ConnectionAdapter(connection, self._backend)
        try:
            yield adapter
            connection.commit()
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    applied_at TEXT NOT NULL
                );
                """
            )
            applied = {
                int(row["version"])
                for row in connection.execute("SELECT version FROM schema_migrations").fetchall()
            }
            for migration in ALPHA_SCHEMA_MIGRATIONS:
                version = int(migration["version"])
                if version in applied:
                    continue
                connection.executescript(migration["sql"])
                connection.execute(
                    "INSERT INTO schema_migrations (version, name, applied_at) VALUES (?, ?, ?)",
                    (version, migration["name"], _utcnow().isoformat()),
                )

    def seed_defaults(self) -> None:
        templates = [
            AgentTemplate(
                id="buildknight",
                name="BuildKnight",
                archetype="architect",
                description="Equilibrado, orientado a requisitos e contratos.",
                recommended_for=["feature delivery", "API contracts", "full flow"],
                locked_fields=["constraints.allow_external_network"],
                default_profile_payload={
                    "name": "BuildKnight",
                    "archetype": "architect",
                    "planning_style": "tests_first",
                    "preferred_stack": ["python", "fastapi", "angular"],
                    "engineering_principles": [
                        "Preservar requisitos",
                        "Preferir simplicidade testavel",
                    ],
                    "modules": ["api_design", "test_debugging"],
                    "constraints": {
                        "allow_dependency_install": True,
                        "allow_external_network": False,
                        "allow_schema_change": True,
                        "max_runtime_minutes": 20,
                    },
                    "memory": {"slots": ["Ler testes antes de editar"]},
                    "limits": {"max_files_edited": 25, "max_runs": 10},
                },
                editable_sections=["name", "planning_style", "memory", "modules"],
                tips=["Comece pelos testes visiveis.", "Evite expandir o escopo cedo demais."],
            ),
            AgentTemplate(
                id="speedster",
                name="Speedster",
                archetype="speedrunner",
                description="Fecha escopo rapido e entrega a menor solucao funcional.",
                recommended_for=["quick bugfix", "time pressure", "small contracts"],
                locked_fields=["constraints.allow_external_network"],
                default_profile_payload={
                    "name": "Speedster",
                    "archetype": "speedrunner",
                    "planning_style": "simplest_possible",
                    "preferred_stack": ["python", "fastapi"],
                    "engineering_principles": ["Entregar rapido sem quebrar requisitos"],
                    "modules": ["api_design"],
                    "constraints": {
                        "allow_dependency_install": True,
                        "allow_external_network": False,
                        "allow_schema_change": True,
                        "max_runtime_minutes": 15,
                    },
                    "memory": {"slots": ["Focar em passar visiveis primeiro"]},
                    "limits": {"max_files_edited": 12, "max_runs": 8},
                },
                editable_sections=["name", "planning_style", "memory"],
                tips=["Otimo para contracts pequenos.", "Nao refatore o que nao precisa."],
            ),
            AgentTemplate(
                id="debugger",
                name="Debugger",
                archetype="debugger",
                description="Focado em localizar regressao e cobrir edge cases.",
                recommended_for=["bugfix", "regression hunting", "test-driven quests"],
                locked_fields=["constraints.allow_external_network"],
                default_profile_payload={
                    "name": "Debugger",
                    "archetype": "debugger",
                    "planning_style": "tests_first",
                    "preferred_stack": ["python"],
                    "engineering_principles": ["Reproduzir antes de corrigir"],
                    "modules": ["test_debugging", "root_cause_analysis"],
                    "constraints": {
                        "allow_dependency_install": True,
                        "allow_external_network": False,
                        "allow_schema_change": True,
                        "max_runtime_minutes": 20,
                    },
                    "memory": {"slots": ["Capturar a menor reproducao possivel"]},
                    "limits": {"max_files_edited": 18, "max_runs": 8},
                },
                editable_sections=["name", "memory", "modules"],
                tips=["Leia falhas escondidas com humildade.", "Preserve contratos existentes."],
            ),
            AgentTemplate(
                id="refiner",
                name="Refiner",
                archetype="refiner",
                description="Busca robustez, clareza e acabamento sem perder score.",
                recommended_for=["stability", "cleanup", "quality pass"],
                locked_fields=["constraints.allow_external_network"],
                default_profile_payload={
                    "name": "Refiner",
                    "archetype": "refiner",
                    "planning_style": "quality_first",
                    "preferred_stack": ["python", "fastapi"],
                    "engineering_principles": ["Melhorar sem expandir risco"],
                    "modules": ["refactoring", "test_debugging"],
                    "constraints": {
                        "allow_dependency_install": True,
                        "allow_external_network": False,
                        "allow_schema_change": True,
                        "max_runtime_minutes": 20,
                    },
                    "memory": {"slots": ["Manter diff pequeno e explicavel"]},
                    "limits": {"max_files_edited": 16, "max_runs": 6},
                },
                editable_sections=["name", "planning_style", "memory"],
                tips=["Ideal para quests de consistencia.", "Evite reescrever demais."],
            ),
        ]
        with self._connect() as connection:
            for template in templates:
                connection.execute(
                    "INSERT OR IGNORE INTO agent_templates (id, payload) VALUES (?, ?)",
                    (template.id, json.dumps(template.model_dump(mode="json"))),
                )
            connection.execute(
                """
                INSERT OR IGNORE INTO invites (code, email_or_login, status, expires_at, used_by_user_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    settings.DEFAULT_ALPHA_INVITE_CODE,
                    "*",
                    "active",
                    None,
                    None,
                ),
            )

    def get_schema_version(self) -> int:
        with self._connect() as connection:
            row = connection.execute("SELECT MAX(version) AS version FROM schema_migrations").fetchone()
        return int(row["version"] or 0)

    def create_auth_state(self, github_login: Optional[str], invite_code: str) -> str:
        state = uuid4().hex
        created_at = _utcnow().isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO auth_states (state, github_login, invite_code, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (state, github_login or "", invite_code, created_at),
            )
        return state

    def get_auth_state(self, state: str) -> Optional[dict[str, str]]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT state, github_login, invite_code FROM auth_states WHERE state = ?",
                (state,),
            ).fetchone()
        if row is None:
            return None
        return dict(row)

    def consume_auth_state(self, state: str) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM auth_states WHERE state = ?", (state,))

    def validate_invite(self, invite_code: str, github_login: str) -> AccessInvite:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT code, email_or_login, status, expires_at, used_by_user_id FROM invites WHERE code = ?",
                (invite_code,),
            ).fetchone()
        if row is None:
            raise ValueError("Invite not found")
        invite = AccessInvite(
            code=row["code"],
            email_or_login=row["email_or_login"],
            status=row["status"],
            expires_at=datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None,
            used_by_user_id=row["used_by_user_id"],
        )
        if invite.status != "active":
            raise ValueError("Invite is not active")
        if invite.email_or_login not in {"*", github_login}:
            raise ValueError("Invite does not match this GitHub login")
        if invite.expires_at and invite.expires_at < _utcnow():
            raise ValueError("Invite expired")
        return invite

    def mark_invite_used(self, code: str, user_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE invites SET status = ?, used_by_user_id = ? WHERE code = ?",
                ("used", user_id, code),
            )

    def record_invite_usage(self, code: str, user_id: str) -> None:
        """Record invite usage while keeping the shared local alpha invite reusable."""
        with self._connect() as connection:
            if code == settings.DEFAULT_ALPHA_INVITE_CODE:
                connection.execute(
                    "UPDATE invites SET used_by_user_id = ? WHERE code = ?",
                    (user_id, code),
                )
            else:
                connection.execute(
                    "UPDATE invites SET status = ?, used_by_user_id = ? WHERE code = ?",
                    ("used", user_id, code),
                )

    def get_invite_status(self, code: str) -> str:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT status FROM invites WHERE code = ?",
                (code,),
            ).fetchone()
        return row["status"] if row else "missing"

    def upsert_user(self, github_login: str) -> User:
        display_name = github_login
        created_at = _utcnow()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, github_login, display_name, role, alpha_status, created_at FROM users WHERE github_login = ?",
                (github_login,),
            ).fetchone()
            if row is None:
                user = User(
                    id=f"user-{uuid4().hex[:10]}",
                    github_login=github_login,
                    display_name=display_name,
                    role="alpha_user",
                    alpha_status="approved",
                    created_at=created_at,
                )
                connection.execute(
                    """
                    INSERT INTO users (id, github_login, display_name, role, alpha_status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user.id,
                        user.github_login,
                        user.display_name,
                        user.role,
                        user.alpha_status,
                        user.created_at.isoformat(),
                    ),
                )
                return user
        return self.get_user_by_login(github_login)

    def get_user_by_login(self, github_login: str) -> User:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, github_login, display_name, role, alpha_status, created_at FROM users WHERE github_login = ?",
                (github_login,),
            ).fetchone()
        if row is None:
            raise ValueError("User not found")
        return User(
            id=row["id"],
            github_login=row["github_login"],
            display_name=row["display_name"],
            role=row["role"],
            alpha_status=row["alpha_status"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, github_login, display_name, role, alpha_status, created_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        if row is None:
            return None
        return User(
            id=row["id"],
            github_login=row["github_login"],
            display_name=row["display_name"],
            role=row["role"],
            alpha_status=row["alpha_status"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def create_session(self, user_id: str) -> str:
        token = uuid4().hex
        created_at = _utcnow()
        expires_at = created_at + timedelta(hours=settings.SESSION_TTL_HOURS)
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO sessions (token, user_id, expires_at, created_at) VALUES (?, ?, ?, ?)",
                (token, user_id, expires_at.isoformat(), created_at.isoformat()),
            )
        return token

    def get_user_by_session(self, token: Optional[str]) -> Optional[User]:
        if not token:
            return None
        with self._connect() as connection:
            row = connection.execute(
                "SELECT user_id, expires_at FROM sessions WHERE token = ?",
                (token,),
            ).fetchone()
        if row is None:
            return None
        if datetime.fromisoformat(row["expires_at"]) < _utcnow():
            return None
        return self.get_user_by_id(row["user_id"])

    def list_templates(self) -> List[AgentTemplate]:
        with self._connect() as connection:
            rows = connection.execute("SELECT payload FROM agent_templates ORDER BY id").fetchall()
        return [AgentTemplate(**json.loads(row["payload"])) for row in rows]

    def get_template(self, template_id: str) -> Optional[AgentTemplate]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM agent_templates WHERE id = ?",
                (template_id,),
            ).fetchone()
        if row is None:
            return None
        return AgentTemplate(**json.loads(row["payload"]))

    def create_profile(self, owner_user_id: str, profile_in: AgentProfileCreate) -> AgentProfile:
        profile = AgentProfile(**profile_in.model_dump())
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO agent_profiles (id, owner_user_id, template_id, visibility, version, payload)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    profile.id,
                    owner_user_id,
                    profile.template_id,
                    profile.visibility,
                    profile.version,
                    json.dumps(profile.model_dump(mode="json")),
                ),
            )
        return profile

    def list_profiles_for_user(self, owner_user_id: str) -> List[AgentProfile]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM agent_profiles WHERE owner_user_id = ? ORDER BY id",
                (owner_user_id,),
            ).fetchall()
        return [AgentProfile(**json.loads(row["payload"])) for row in rows]

    def get_profile(self, profile_id: str) -> Optional[AgentProfile]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM agent_profiles WHERE id = ?",
                (profile_id,),
            ).fetchone()
        if row is None:
            return None
        return AgentProfile(**json.loads(row["payload"]))

    def update_profile(self, profile_id: str, user_id: str, profile_in: AgentProfileUpdate) -> AgentProfile:
        current = self.get_profile(profile_id)
        if current is None:
            raise ValueError("Profile not found")
        if current.owner_user_id != user_id:
            raise ValueError("You do not own this profile")
        next_version = (profile_in.version or current.version) + 1
        updated = current.model_copy(
            update={**profile_in.model_dump(exclude_none=True), "version": next_version}
        )
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE agent_profiles
                SET template_id = ?, visibility = ?, version = ?, payload = ?
                WHERE id = ?
                """,
                (
                    updated.template_id,
                    updated.visibility,
                    updated.version,
                    json.dumps(updated.model_dump(mode="json")),
                    profile_id,
                ),
            )
        return updated

    def create_battle(self, created_by_user_id: str, quest_id: str) -> Battle:
        now = _utcnow()
        battle = Battle(
            id=f"battle-{uuid4().hex[:10]}",
            quest_id=quest_id,
            status="waiting_for_opponent",
            created_by_user_id=created_by_user_id,
            battle_type="async_1v1",
            created_at=now,
            started_at=None,
            finished_at=None,
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO battles (id, quest_id, status, created_by_user_id, battle_type, created_at, started_at, finished_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    battle.id,
                    battle.quest_id,
                    battle.status,
                    battle.created_by_user_id,
                    battle.battle_type,
                    battle.created_at.isoformat(),
                    None,
                    None,
                ),
            )
        return battle

    def get_battle(self, battle_id: str) -> Optional[Battle]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, quest_id, status, created_by_user_id, battle_type, created_at, started_at, finished_at
                FROM battles WHERE id = ?
                """,
                (battle_id,),
            ).fetchone()
        if row is None:
            return None
        return Battle(
            id=row["id"],
            quest_id=row["quest_id"],
            status=row["status"],
            created_by_user_id=row["created_by_user_id"],
            battle_type=row["battle_type"],
            created_at=datetime.fromisoformat(row["created_at"]),
            started_at=datetime.fromisoformat(row["started_at"]) if row["started_at"] else None,
            finished_at=datetime.fromisoformat(row["finished_at"]) if row["finished_at"] else None,
        )

    def list_battles(self) -> List[Battle]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, quest_id, status, created_by_user_id, battle_type, created_at, started_at, finished_at
                FROM battles ORDER BY created_at DESC
                """
            ).fetchall()
        return [
            Battle(
                id=row["id"],
                quest_id=row["quest_id"],
                status=row["status"],
                created_by_user_id=row["created_by_user_id"],
                battle_type=row["battle_type"],
                created_at=datetime.fromisoformat(row["created_at"]),
                started_at=datetime.fromisoformat(row["started_at"]) if row["started_at"] else None,
                finished_at=datetime.fromisoformat(row["finished_at"]) if row["finished_at"] else None,
            )
            for row in rows
        ]

    def create_or_replace_participant(
        self,
        battle_id: str,
        user_id: str,
        agent_profile_id: str,
        seat: str,
        workspace_files: Dict[str, str],
    ) -> BattleParticipant:
        now = _utcnow()
        existing = self.get_participant_by_user(battle_id, user_id)
        participant = BattleParticipant(
            id=existing.id if existing else f"participant-{uuid4().hex[:10]}",
            battle_id=battle_id,
            user_id=user_id,
            agent_profile_id=agent_profile_id,
            seat=seat,
            submission_status="ready" if workspace_files else "joined",
            workspace_files=workspace_files,
            run_id=existing.run_id if existing else None,
            joined_at=existing.joined_at if existing else now,
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO battle_participants
                (id, battle_id, user_id, agent_profile_id, seat, submission_status, workspace_files, run_id, joined_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    participant.id,
                    participant.battle_id,
                    participant.user_id,
                    participant.agent_profile_id,
                    participant.seat,
                    participant.submission_status,
                    json.dumps(participant.workspace_files),
                    participant.run_id,
                    participant.joined_at.isoformat(),
                ),
            )
        return participant

    def get_participant_by_user(self, battle_id: str, user_id: str) -> Optional[BattleParticipant]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, battle_id, user_id, agent_profile_id, seat, submission_status, workspace_files, run_id, joined_at
                FROM battle_participants WHERE battle_id = ? AND user_id = ?
                """,
                (battle_id, user_id),
            ).fetchone()
        return self._participant_from_row(row)

    def get_participants(self, battle_id: str) -> List[BattleParticipant]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, battle_id, user_id, agent_profile_id, seat, submission_status, workspace_files, run_id, joined_at
                FROM battle_participants WHERE battle_id = ? ORDER BY seat
                """,
                (battle_id,),
            ).fetchall()
        return [self._participant_from_row(row) for row in rows if row is not None]

    def update_participant_submission(
        self, battle_id: str, user_id: str, workspace_files: Dict[str, str]
    ) -> BattleParticipant:
        participant = self.get_participant_by_user(battle_id, user_id)
        if participant is None:
            raise ValueError("Participant not found")
        updated = participant.model_copy(
            update={
                "workspace_files": workspace_files,
                "submission_status": "ready" if workspace_files else "joined",
            }
        )
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE battle_participants
                SET workspace_files = ?, submission_status = ?
                WHERE id = ?
                """,
                (
                    json.dumps(updated.workspace_files),
                    updated.submission_status,
                    updated.id,
                ),
            )
        return updated

    def update_participant_run(self, participant_id: str, run_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE battle_participants SET run_id = ?, submission_status = ? WHERE id = ?",
                (run_id, "completed", participant_id),
            )

    def update_battle_status(self, battle_id: str, status: str) -> Battle:
        battle = self.get_battle(battle_id)
        if battle is None:
            raise ValueError("Battle not found")
        now = _utcnow()
        started_at = battle.started_at
        finished_at = battle.finished_at
        if status == "running" and started_at is None:
            started_at = now
        if status in {"completed", "failed"}:
            finished_at = now
        updated = battle.model_copy(
            update={"status": status, "started_at": started_at, "finished_at": finished_at}
        )
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE battles SET status = ?, started_at = ?, finished_at = ? WHERE id = ?
                """,
                (
                    updated.status,
                    updated.started_at.isoformat() if updated.started_at else None,
                    updated.finished_at.isoformat() if updated.finished_at else None,
                    battle_id,
                ),
            )
        return updated

    def save_battle_result(self, result: BattleResult) -> BattleResult:
        with self._connect() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO battle_results (battle_id, payload) VALUES (?, ?)",
                (result.battle_id, json.dumps(result.model_dump(mode="json"))),
            )
        return result

    def get_battle_result(self, battle_id: str) -> Optional[BattleResult]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM battle_results WHERE battle_id = ?",
                (battle_id,),
            ).fetchone()
        if row is None:
            return None
        return BattleResult(**json.loads(row["payload"]))

    def save_battle_run_bundle(self, battle_id: str, bundle: BattleRunBundle) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO battle_run_bundles (participant_id, battle_id, payload)
                VALUES (?, ?, ?)
                """,
                (
                    bundle.participant_id,
                    battle_id,
                    json.dumps(bundle.model_dump(mode="json")),
                ),
            )

    def get_battle_replay_bundle(self, battle_id: str) -> BattleReplayBundle:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM battle_run_bundles WHERE battle_id = ? ORDER BY participant_id",
                (battle_id,),
            ).fetchall()
        bundles = [BattleRunBundle(**json.loads(row["payload"])) for row in rows]
        return BattleReplayBundle(battle_id=battle_id, runs=bundles)

    def get_battle_detail(self, battle_id: str) -> Optional[BattleDetail]:
        battle = self.get_battle(battle_id)
        if battle is None:
            return None
        return BattleDetail(
            battle=battle,
            participants=self.get_participants(battle_id),
            result=self.get_battle_result(battle_id),
        )

    def get_profile_owner(self, profile_id: str) -> Optional[str]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT owner_user_id FROM agent_profiles WHERE id = ?",
                (profile_id,),
            ).fetchone()
        return row["owner_user_id"] if row else None

    def list_leaderboard(self) -> List[LeaderboardEntry]:
        battles = [battle for battle in self.list_battles() if battle.status == "completed"]
        stats: dict[str, dict[str, Any]] = {}
        for battle in battles:
            result = self.get_battle_result(battle.id)
            if result is None:
                continue
            participants = self.get_participants(battle.id)
            for participant in participants:
                user = self.get_user_by_id(participant.user_id)
                if user is None:
                    continue
                current = stats.setdefault(
                    user.id,
                    {
                        "user": user,
                        "wins": 0,
                        "losses": 0,
                        "ties": 0,
                        "best_score": 0.0,
                    },
                )
                bundle = self.get_battle_replay_bundle(battle.id)
                participant_bundle = next(
                    (item for item in bundle.runs if item.participant_id == participant.id), None
                )
                if participant_bundle:
                    current["best_score"] = max(
                        current["best_score"],
                        participant_bundle.run.summary.technical_score,
                    )
                if result.winner_participant_id is None:
                    current["ties"] += 1
                elif result.winner_participant_id == participant.id:
                    current["wins"] += 1
                else:
                    current["losses"] += 1
        leaderboard = [
            LeaderboardEntry(
                user_id=data["user"].id,
                github_login=data["user"].github_login,
                display_name=data["user"].display_name,
                wins=data["wins"],
                losses=data["losses"],
                ties=data["ties"],
                best_score=data["best_score"],
            )
            for data in stats.values()
        ]
        return sorted(
            leaderboard,
            key=lambda item: (-item.wins, item.losses, -item.best_score, item.github_login),
        )

    def _participant_from_row(self, row: Optional[Any]) -> Optional[BattleParticipant]:
        if row is None:
            return None
        return BattleParticipant(
            id=row["id"],
            battle_id=row["battle_id"],
            user_id=row["user_id"],
            agent_profile_id=row["agent_profile_id"],
            seat=row["seat"],
            submission_status=row["submission_status"],
            workspace_files=json.loads(row["workspace_files"]),
            run_id=row["run_id"],
            joined_at=datetime.fromisoformat(row["joined_at"]),
        )


class _ConnectionAdapter:
    """Normalize the small SQL dialect differences used by AlphaStore."""

    def __init__(self, connection: Any, backend: str) -> None:
        self._connection = connection
        self._backend = backend

    def execute(self, query: str, params: Any = ()) -> Any:
        return self._connection.execute(self._rewrite(query), params)

    def executescript(self, script: str) -> None:
        if self._backend == "sqlite":
            self._connection.executescript(script)
            return
        for statement in script.split(";"):
            sql = statement.strip()
            if sql:
                self.execute(sql)

    def _rewrite(self, query: str) -> str:
        if self._backend == "sqlite":
            return query
        rewritten = query
        rewritten = rewritten.replace("?", "%s")
        rewritten = rewritten.replace(
            "INSERT OR IGNORE INTO agent_templates (id, payload) VALUES (%s, %s)",
            "INSERT INTO agent_templates (id, payload) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
        )
        rewritten = rewritten.replace(
            """
                INSERT OR IGNORE INTO invites (code, email_or_login, status, expires_at, used_by_user_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
            """
                INSERT INTO invites (code, email_or_login, status, expires_at, used_by_user_id)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (code) DO NOTHING
                """,
        )
        rewritten = rewritten.replace(
            """
                INSERT OR REPLACE INTO agent_profiles (id, owner_user_id, template_id, visibility, version, payload)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
            """
                INSERT INTO agent_profiles (id, owner_user_id, template_id, visibility, version, payload)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    owner_user_id = EXCLUDED.owner_user_id,
                    template_id = EXCLUDED.template_id,
                    visibility = EXCLUDED.visibility,
                    version = EXCLUDED.version,
                    payload = EXCLUDED.payload
                """,
        )
        rewritten = rewritten.replace(
            """
                INSERT OR REPLACE INTO battle_participants
                (id, battle_id, user_id, agent_profile_id, seat, submission_status, workspace_files, run_id, joined_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
            """
                INSERT INTO battle_participants
                (id, battle_id, user_id, agent_profile_id, seat, submission_status, workspace_files, run_id, joined_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    battle_id = EXCLUDED.battle_id,
                    user_id = EXCLUDED.user_id,
                    agent_profile_id = EXCLUDED.agent_profile_id,
                    seat = EXCLUDED.seat,
                    submission_status = EXCLUDED.submission_status,
                    workspace_files = EXCLUDED.workspace_files,
                    run_id = EXCLUDED.run_id,
                    joined_at = EXCLUDED.joined_at
                """,
        )
        rewritten = rewritten.replace(
            "INSERT OR REPLACE INTO battle_results (battle_id, payload) VALUES (%s, %s)",
            """
            INSERT INTO battle_results (battle_id, payload) VALUES (%s, %s)
            ON CONFLICT (battle_id) DO UPDATE SET payload = EXCLUDED.payload
            """,
        )
        rewritten = rewritten.replace(
            """
                INSERT OR REPLACE INTO battle_run_bundles (participant_id, battle_id, payload)
                VALUES (%s, %s, %s)
                """,
            """
                INSERT INTO battle_run_bundles (participant_id, battle_id, payload)
                VALUES (%s, %s, %s)
                ON CONFLICT (participant_id) DO UPDATE SET
                    battle_id = EXCLUDED.battle_id,
                    payload = EXCLUDED.payload
                """,
        )
        return rewritten
