"""Execution service for the Sprint 2 local pipeline."""
from datetime import datetime, timezone
from typing import List

from ..models import (
    AgentProfile,
    PostMortem,
    Quest,
    RankingEntry,
    ReplayEvent,
    Run,
    RunSuiteResult,
    RunSummary,
)
from ..repositories.base import PostMortemRepository, RankingRepository, ReplayEventRepository
from ..sandbox.runner import SandboxRunner


class ExecutionService:
    """Run a minimal deterministic evaluation pipeline for a quest run."""

    def __init__(
        self,
        replay_repository: ReplayEventRepository,
        post_mortem_repository: PostMortemRepository,
        ranking_repository: RankingRepository,
        sandbox_runner: SandboxRunner,
    ) -> None:
        self._replay_repository = replay_repository
        self._post_mortem_repository = post_mortem_repository
        self._ranking_repository = ranking_repository
        self._sandbox_runner = sandbox_runner

    def execute(self, run: Run, quest: Quest, profile: AgentProfile, completed_runs: int) -> Run:
        """Generate summary, replay, post-mortem and ranking for a run."""
        sandbox_result = self._sandbox_runner.run(run, quest)
        visible_count = sandbox_result.visible_count
        hidden_count = sandbox_result.hidden_count
        total_tests = visible_count + hidden_count
        passed_tests = sandbox_result.passed_tests
        failed_tests = sandbox_result.failed_tests

        visible_suite = RunSuiteResult(
            suite="visible",
            passed=sandbox_result.visible_passed,
            failed=sandbox_result.visible_failed,
            duration_ms=max(300, sandbox_result.duration_ms - 150),
        )
        hidden_suite = RunSuiteResult(
            suite="hidden",
            passed=sandbox_result.hidden_passed,
            failed=sandbox_result.hidden_failed,
            duration_ms=150 if hidden_count else 0,
        )
        suites: List[RunSuiteResult] = [visible_suite]
        if hidden_count:
            suites.append(hidden_suite)

        technical_score = round((passed_tests / max(total_tests, 1)) * 100, 2)
        total_score = technical_score
        notes = [
            f"Quest '{quest.title}' executada com o perfil '{profile.name}'.",
            f"Quest executada via provider '{sandbox_result.provider}'.",
            "Politica de hardening ativa: rede externa desabilitada e limite de runtime validado.",
        ]
        notes.extend(sandbox_result.notes)
        if sandbox_result.changed_files:
            notes.append(
                f"Arquivos sobrescritos antes da execucao: {', '.join(sandbox_result.changed_files)}."
            )
        if sandbox_result.hidden_failed:
            notes.append("Hidden tests ainda representam risco e reduzem o score final.")
        else:
            notes.append("Hidden tests executaram sem falhas nesta run.")

        summary = RunSummary(
            technical_score=technical_score,
            total_score=total_score,
            duration_ms=sandbox_result.duration_ms,
            suites=suites,
            notes=notes,
            artifacts=sandbox_result.artifacts,
        )
        now = datetime.now(timezone.utc)
        updated_run = run.model_copy(
            update={
                "status": "completed",
                "sandbox_id": sandbox_result.sandbox_id,
                "updated_at": now,
                "summary": summary,
            }
        )

        events = self._build_events(updated_run, quest, profile, passed_tests, failed_tests)
        self._replay_repository.create_many(events)

        strengths = [
            f"Perfil {profile.archetype} alinhado ao stack preferido.",
            "Run produziu timeline, score e artefatos reais do subprocesso de execucao.",
        ]
        failures = []
        if sandbox_result.hidden_failed:
            failures.append("Hidden tests permanecem sem cobertura completa no pipeline minimo.")
        suggestions = [
            "Expandir a cobertura das quests com suites adicionais e cenarios mais complexos.",
            "Expandir o perfil com heuristicas mais especificas por tipo de quest.",
        ]
        if profile.planning_style == "tests_first":
            strengths.append("A estrategia tests_first combina bem com quests guiadas por contrato.")
        else:
            suggestions.append("Considerar um planejamento orientado a testes para reduzir risco.")

        post_mortem = PostMortem(
            id=f"pm-{run.id}",
            run_id=run.id,
            final_score=technical_score,
            tests_passed=passed_tests,
            tests_failed=failed_tests,
            claude_analysis=(
                "A run concluiu o fluxo minimo com avaliacao deterministica, gerando sinais "
                "suficientes para iteracao do produto. Agora a execucao ja passa por um "
                "workspace temporario e um subprocesso isolado."
            ),
            strengths=strengths,
            failures=failures,
            suggestions=suggestions,
        )
        self._post_mortem_repository.save(post_mortem)

        ranking_entry = RankingEntry(
            quest_id=quest.id,
            run_id=run.id,
            agent_profile_id=profile.id,
            score=technical_score,
            completed_runs=completed_runs,
        )
        self._ranking_repository.record(ranking_entry)
        return updated_run

    def _build_events(
        self,
        run: Run,
        quest: Quest,
        profile: AgentProfile,
        passed_tests: int,
        failed_tests: int,
    ) -> List[ReplayEvent]:
        now = datetime.now(timezone.utc)
        base_payload = {"quest_id": quest.id, "agent_profile_id": profile.id}
        events = [
            ReplayEvent(
                id=f"{run.id}-evt-1",
                run_id=run.id,
                type="QUEST_SELECTED",
                message=f"Claude anunciou a quest {quest.title}.",
                timestamp=now,
                payload=base_payload,
            ),
            ReplayEvent(
                id=f"{run.id}-evt-2",
                run_id=run.id,
                type="SANDBOX_READY",
                message=f"Workspace local preparado para o perfil {profile.name}.",
                timestamp=now,
                payload={"sandbox_id": run.sandbox_id, **base_payload},
            ),
        ]
        if run.workspace_files:
            events.append(
                ReplayEvent(
                    id=f"{run.id}-evt-3",
                    run_id=run.id,
                    type="FILE_CHANGED",
                    message=f"{len(run.workspace_files)} arquivo(s) sobrescrito(s) no workspace antes dos testes.",
                    timestamp=now,
                    payload={"files": list(run.workspace_files.keys()), **base_payload},
                )
            )
            test_event_id = f"{run.id}-evt-4"
            finish_event_id = f"{run.id}-evt-5"
        else:
            test_event_id = f"{run.id}-evt-3"
            finish_event_id = f"{run.id}-evt-4"
        events.extend(
            [
                ReplayEvent(
                    id=test_event_id,
                    run_id=run.id,
                    type="TEST_RUN_COMPLETED",
                    message="Suites da quest consolidadas apos execucao em sandbox temporario.",
                    timestamp=now,
                    payload={"passed": passed_tests, "failed": failed_tests, **base_payload},
                ),
                ReplayEvent(
                    id=finish_event_id,
                    run_id=run.id,
                    type="MATCH_FINISHED",
                    message=f"Run concluida com score tecnico {run.summary.technical_score}.",
                    timestamp=now,
                    payload={"technical_score": run.summary.technical_score, **base_payload},
                ),
            ]
        )
        return events
