"""Services for the public alpha 1v1 battle flow."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Optional
from urllib.parse import urlencode

import httpx

from ..core.config import settings
from ..models import (
    AgentProfile,
    AgentProfileCreate,
    AgentProfileUpdate,
    AgentTemplate,
    Battle,
    BattleCreate,
    BattleDetail,
    BattleJoin,
    BattleParticipantSubmission,
    BattleResult,
    BattleRunBundle,
    InviteValidationResponse,
    Quest,
    ReplayEvent,
    Run,
    SessionUserResponse,
    User,
)
from ..repositories.in_memory import (
    InMemoryPostMortemRepository,
    InMemoryRankingRepository,
    InMemoryReplayEventRepository,
)
from ..sandbox.runner import SandboxRunner
from .alpha_store import AlphaStore
from .battle_worker import InProcessBattleWorker
from .execution_service import ExecutionService
from .quest_service import QuestService


class PublicAlphaService:
    """Orchestrate auth, templates, profiles and 1v1 battles for the alpha."""

    def __init__(
        self,
        store: AlphaStore,
        quest_service: QuestService,
        sandbox_runner: SandboxRunner,
        battle_worker: Optional[InProcessBattleWorker] = None,
    ) -> None:
        self._store = store
        self._quest_service = quest_service
        self._sandbox_runner = sandbox_runner
        self._battle_worker = battle_worker or InProcessBattleWorker(self._run_battle)

    def start_auth(self, github_login: Optional[str], invite_code: str) -> tuple[str, str]:
        if settings.ENABLE_MOCK_GITHUB_AUTH and not github_login:
            raise ValueError("GitHub login is required when mock GitHub auth is enabled")
        if settings.ALPHA_REQUIRE_INVITE and settings.ENABLE_MOCK_GITHUB_AUTH:
            self._store.validate_invite(invite_code, github_login or "")
        elif settings.ALPHA_REQUIRE_INVITE and self._store.get_invite_status(invite_code) != "active":
            raise ValueError("Invite is not active")
        state = self._store.create_auth_state(github_login, invite_code)
        return state, self._build_authorization_url(state, github_login)

    def finish_auth(
        self,
        state: str,
        github_login: Optional[str] = None,
        code: Optional[str] = None,
    ) -> tuple[User, str]:
        auth_state = self._store.get_auth_state(state)
        if auth_state is None:
            raise ValueError("Invalid auth state")
        resolved_login = self._resolve_github_login(auth_state, github_login, code)
        if settings.ALPHA_REQUIRE_INVITE:
            invite = self._store.validate_invite(auth_state["invite_code"], resolved_login)
        else:
            invite = None
        user = self._store.upsert_user(resolved_login)
        if invite is not None:
            self._store.record_invite_usage(invite.code, user.id)
        token = self._store.create_session(user.id)
        self._store.consume_auth_state(state)
        return user, token

    def get_session_user(self, token: Optional[str]) -> SessionUserResponse:
        user = self._store.get_user_by_session(token)
        return SessionUserResponse(authenticated=user is not None, user=user)

    def validate_invite(self, code: str, github_login: str) -> InviteValidationResponse:
        try:
            self._store.validate_invite(code, github_login)
        except ValueError as exc:
            return InviteValidationResponse(valid=False, status=str(exc))
        return InviteValidationResponse(valid=True, status=self._store.get_invite_status(code))

    def list_templates(self) -> list[AgentTemplate]:
        return self._store.list_templates()

    def create_profile_from_payload(
        self, user: User, profile_in: AgentProfileCreate
    ) -> AgentProfile:
        owned = profile_in.model_copy(
            update={
                "owner_user_id": user.id,
                "visibility": profile_in.visibility or "private",
                "version": profile_in.version or 1,
            }
        )
        return self._store.create_profile(user.id, owned)

    def create_profile_from_template(
        self, user: User, template_id: str, name_suffix: Optional[str] = None
    ) -> AgentProfile:
        template = self._store.get_template(template_id)
        if template is None:
            raise ValueError("Template not found")
        payload = dict(template.default_profile_payload)
        payload.update(
            {
                "id": f"{template.id}-{user.github_login}",
                "name": name_suffix or payload.get("name") or template.name,
                "template_id": template.id,
                "owner_user_id": user.id,
                "visibility": "private",
                "version": 1,
            }
        )
        return self._store.create_profile(user.id, AgentProfileCreate(**payload))

    def list_profiles_for_user(self, user: User) -> list[AgentProfile]:
        profiles = self._store.list_profiles_for_user(user.id)
        if profiles:
            return profiles
        seeded = []
        for template in self.list_templates():
            seeded.append(self.create_profile_from_template(user, template.id, template.name))
        return seeded

    def update_profile(self, profile_id: str, user: User, profile_in: AgentProfileUpdate) -> AgentProfile:
        return self._store.update_profile(profile_id, user.id, profile_in)

    def list_battles(self) -> list[Battle]:
        return self._store.list_battles()

    def get_battle_detail(self, battle_id: str) -> BattleDetail:
        detail = self._store.get_battle_detail(battle_id)
        if detail is None:
            raise ValueError("Battle not found")
        return detail

    def create_battle(self, user: User, battle_in: BattleCreate) -> BattleDetail:
        self._assert_quest_exists(battle_in.quest_id)
        self._assert_profile_ownership(user.id, battle_in.agent_profile_id)
        battle = self._store.create_battle(user.id, battle_in.quest_id)
        self._store.create_or_replace_participant(
            battle.id,
            user.id,
            battle_in.agent_profile_id,
            "left",
            battle_in.workspace_files,
        )
        return self.get_battle_detail(battle.id)

    def join_battle(self, battle_id: str, user: User, battle_in: BattleJoin) -> BattleDetail:
        self._assert_profile_ownership(user.id, battle_in.agent_profile_id)
        battle = self._store.get_battle(battle_id)
        if battle is None:
            raise ValueError("Battle not found")
        participants = self._store.get_participants(battle_id)
        if len(participants) >= 2 and self._store.get_participant_by_user(battle_id, user.id) is None:
            raise ValueError("Battle already has two participants")
        existing = self._store.get_participant_by_user(battle_id, user.id)
        seat = existing.seat if existing else ("right" if any(p.seat == "left" for p in participants) else "left")
        self._store.create_or_replace_participant(
            battle_id,
            user.id,
            battle_in.agent_profile_id,
            seat,
            battle_in.workspace_files,
        )
        if len(self._store.get_participants(battle_id)) == 2:
            self._store.update_battle_status(battle_id, "ready")
        return self.get_battle_detail(battle_id)

    def submit_for_battle(
        self, battle_id: str, user: User, submission: BattleParticipantSubmission
    ) -> BattleDetail:
        self._store.update_participant_submission(battle_id, user.id, submission.workspace_files)
        participants = self._store.get_participants(battle_id)
        if len(participants) == 2 and all(item.submission_status == "ready" for item in participants):
            self._store.update_battle_status(battle_id, "ready")
        return self.get_battle_detail(battle_id)

    def start_battle(self, battle_id: str, user: User) -> BattleDetail:
        detail = self.get_battle_detail(battle_id)
        if detail.battle.created_by_user_id != user.id and user.role != "admin":
            raise ValueError("Only the creator can start this battle")
        if detail.battle.status != "ready":
            raise ValueError("Battle is not ready to start")
        if len(detail.participants) != 2:
            raise ValueError("Battle needs exactly two participants")
        if not all(item.submission_status == "ready" for item in detail.participants):
            raise ValueError("Both participants must submit before starting")
        self._store.update_battle_status(battle_id, "queued")
        self._battle_worker.enqueue(battle_id)
        return self.get_battle_detail(battle_id)

    def get_battle_result(self, battle_id: str) -> BattleResult:
        result = self._store.get_battle_result(battle_id)
        if result is None:
            raise ValueError("Battle result not available yet")
        return result

    def get_battle_replay(self, battle_id: str):
        return self._store.get_battle_replay_bundle(battle_id)

    def list_leaderboard(self):
        return self._store.list_leaderboard()

    def _build_authorization_url(self, state: str, github_login: Optional[str]) -> str:
        if settings.ENABLE_MOCK_GITHUB_AUTH:
            return (
                f"{settings.API_V1_PREFIX}/auth/github/callback?"
                f"{urlencode({'state': state, 'github_login': github_login or ''})}"
            )
        if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
            raise ValueError("GitHub OAuth credentials are not configured")
        query = urlencode(
            {
                "client_id": settings.GITHUB_CLIENT_ID,
                "redirect_uri": settings.GITHUB_REDIRECT_URI,
                "scope": settings.GITHUB_OAUTH_SCOPE,
                "state": state,
            }
        )
        return f"{settings.GITHUB_AUTHORIZE_URL}?{query}"

    def _resolve_github_login(
        self,
        auth_state: dict[str, str],
        github_login: Optional[str],
        code: Optional[str],
    ) -> str:
        if settings.ENABLE_MOCK_GITHUB_AUTH:
            resolved_login = github_login or auth_state["github_login"]
            if not resolved_login:
                raise ValueError("GitHub login is required when mock GitHub auth is enabled")
            if auth_state["github_login"] and auth_state["github_login"] != resolved_login:
                raise ValueError("GitHub login does not match the auth state")
            return resolved_login
        if not code:
            raise ValueError("GitHub OAuth code is required")
        return self._fetch_github_login(code)

    def _fetch_github_login(self, code: str) -> str:
        token_response = httpx.post(
            settings.GITHUB_TOKEN_URL,
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GITHUB_REDIRECT_URI,
            },
            headers={"Accept": "application/json"},
            timeout=10,
        )
        token_response.raise_for_status()
        token_payload = token_response.json()
        access_token = token_payload.get("access_token")
        if not access_token:
            raise ValueError("GitHub OAuth token response did not include an access token")
        user_response = httpx.get(
            settings.GITHUB_USER_URL,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {access_token}",
            },
            timeout=10,
        )
        user_response.raise_for_status()
        github_login = user_response.json().get("login")
        if not github_login:
            raise ValueError("GitHub user response did not include a login")
        return github_login

    def _run_battle(self, battle_id: str) -> None:
        try:
            detail = self.get_battle_detail(battle_id)
            quest = self._assert_quest_exists(detail.battle.quest_id)
            self._store.update_battle_status(battle_id, "running")
            bundles: list[BattleRunBundle] = []
            for index, participant in enumerate(detail.participants, start=1):
                profile = self._store.get_profile(participant.agent_profile_id)
                if profile is None:
                    raise ValueError("Profile not found during battle execution")
                run = Run(
                    id=f"{battle_id}-run-{participant.seat}",
                    quest_id=quest.id,
                    agent_profile_id=profile.id,
                    workspace_files=participant.workspace_files,
                    status="created",
                    sandbox_id=None,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                replay_repository = InMemoryReplayEventRepository()
                post_mortem_repository = InMemoryPostMortemRepository()
                ranking_repository = InMemoryRankingRepository()
                execution_service = ExecutionService(
                    replay_repository,
                    post_mortem_repository,
                    ranking_repository,
                    self._sandbox_runner,
                )
                executed_run = execution_service.execute(run, quest, profile, index)
                post_mortem = post_mortem_repository.get_by_run(executed_run.id)
                if post_mortem is None:
                    raise ValueError("Post-mortem missing after execution")
                bundle = BattleRunBundle(
                    participant_id=participant.id,
                    run=executed_run,
                    replay=replay_repository.list_by_run(executed_run.id),
                    post_mortem=post_mortem,
                )
                self._store.save_battle_run_bundle(battle_id, bundle)
                self._store.update_participant_run(participant.id, executed_run.id)
                bundles.append(bundle)
            result = self._build_result(battle_id, bundles)
            self._store.save_battle_result(result)
            self._store.update_battle_status(battle_id, "completed")
        except Exception:
            self._store.update_battle_status(battle_id, "failed")
            raise

    def _build_result(self, battle_id: str, bundles: list[BattleRunBundle]) -> BattleResult:
        left = next(bundle for bundle in bundles if bundle.run.id.endswith("left"))
        right = next(bundle for bundle in bundles if bundle.run.id.endswith("right"))
        left_score = left.run.summary.technical_score
        right_score = right.run.summary.technical_score
        if left_score > right_score:
            winner = left.participant_id
            reason = "higher_technical_score"
            summary = "Seat left venceu por maior technical score."
        elif right_score > left_score:
            winner = right.participant_id
            reason = "higher_technical_score"
            summary = "Seat right venceu por maior technical score."
        else:
            left_passed = sum(item.passed for item in left.run.summary.suites)
            right_passed = sum(item.passed for item in right.run.summary.suites)
            if left_passed > right_passed:
                winner = left.participant_id
                reason = "more_passed_tests"
                summary = "Seat left venceu no tie-break por mais testes passados."
            elif right_passed > left_passed:
                winner = right.participant_id
                reason = "more_passed_tests"
                summary = "Seat right venceu no tie-break por mais testes passados."
            else:
                left_duration = left.run.summary.duration_ms or 10**9
                right_duration = right.run.summary.duration_ms or 10**9
                if left_duration < right_duration:
                    winner = left.participant_id
                    reason = "lower_duration_ms"
                    summary = "Seat left venceu no tie-break por menor duracao."
                elif right_duration < left_duration:
                    winner = right.participant_id
                    reason = "lower_duration_ms"
                    summary = "Seat right venceu no tie-break por menor duracao."
                else:
                    winner = None
                    reason = "explicit_tie"
                    summary = "Battle terminou empatada pelos criterios tecnicos do MVP."
        return BattleResult(
            battle_id=battle_id,
            winner_participant_id=winner,
            score_left=left_score,
            score_right=right_score,
            tie_break_reason=reason,
            summary=summary,
        )

    def _assert_quest_exists(self, quest_id: str) -> Quest:
        quest = self._quest_service.get_quest(quest_id)
        if quest is None:
            raise ValueError("Quest not found")
        return quest

    def _assert_profile_ownership(self, user_id: str, profile_id: str) -> None:
        owner = self._store.get_profile_owner(profile_id)
        if owner != user_id:
            raise ValueError("Profile does not belong to the authenticated user")
