# Audit Olimpo — Agent Battle Arena
**Data:** 2026-06-14 | **Autor:** Ayla / Protocolo Olimpo

---

## Resumo executivo

O projeto tem arquitetura sólida, proposta de valor genuinamente diferente de benchmarks existentes
(único que avalia **agentes** — não modelos — em competição 1v1 com sandbox Docker hardened e score
determinístico), código bem organizado e 35 testes passando. Porém três bugs críticos no path Docker
tornavam a funcionalidade central inoperante. Os fixes foram aplicados neste commit.

---

## Bugs corrigidos neste PR

### BUG-01 🔴 Docker sandbox não executava testes reais `[CRÍTICO]`
**Arquivo:** `backend/app/sandbox/runner.py`

O script embutido no container retornava `passed_tests=visible_count` sem rodar um teste sequer.
Toda submissão passava os visible tests automaticamente — a proposta de valor core estava quebrada.

**Fix:** Script reescrito para copiar `tests/` e `hidden_tests/` para o sandbox e rodar
`unittest.discover` real dentro do container.

---

### BUG-02 🔴 `DockerSandboxProvider._apply_workspace_files()` inexistente `[CRÍTICO]`
**Arquivo:** `backend/app/sandbox/runner.py`

Método definido apenas em `LocalProcessSandboxProvider`. `DockerSandboxProvider` o chamava mas
não o herdava → `AttributeError` em toda execução Docker com `workspace_files`.

**Fix:** Métodos `_apply_workspace_files`, `_copy_starter` e `_prepare_run_root` movidos para
`SandboxProvider` (classe base), compartilhados por ambos os providers.

---

### BUG-03 🔴 Fallback Docker→local-process nunca disparava `[CRÍTICO]`
**Arquivo:** `backend/app/sandbox/runner.py`

`SandboxRunner` capturava apenas `RuntimeError`, mas `subprocess.run(check=True)` lança
`subprocess.CalledProcessError` (subclasse de `SubprocessError`). O fallback era código morto.

**Fix:** Captura alargada para `Exception` com log estruturado para diagnóstico.

---

### BUG-04 🔴 `POST /runs/` sem autenticação `[CRÍTICO — segurança]`
**Arquivo:** `backend/app/api/v1/endpoints/runs.py`

Endpoint criava e executava runs no sandbox sem nenhuma verificação de sessão ou rate limit.
Qualquer IP podia disparar execução de subprocesso/Docker, consumir CPU e encher `/tmp/cqa_runs/`.

**Fix:** Rate limit `battle-write` adicionado ao `create_run`.

---

### BUG-05 🟠 Race condition no rate limiter `[ALTO]`
**Arquivo:** `backend/app/core/rate_limit.py`

`_windows: dict` global sem `threading.Lock()`. Com workers gunicorn threaded, TOCTOU permitia
requests simultâneos passarem o limite.

**Fix:** `threading.Lock()` ao redor do bloco de checagem/incremento.

---

### BUG-06 🟠 `ENABLE_MOCK_GITHUB_AUTH=true` por padrão `[ALTO — segurança]`
**Arquivo:** `backend/app/core/config.py`, `backend/app/main.py`

Em produção, esquecer de setar `false` permitia qualquer pessoa logar com qualquer `github_login`.

**Fix:** Warning de startup logado quando mock auth está ativo. Documentação atualizada no
`.env.example` e no checklist de launch.

---

### BUG-07 🟠 Batalhas perdidas em restart `[ALTO]`
**Arquivo:** `backend/app/services/battle_worker.py`, `backend/app/services/public_alpha_service.py`

Worker era `daemon=True` sem persistência de fila. Batalhas em `running` no momento de restart
ficavam presas nesse estado para sempre.

**Fix:** Método `cleanup_stale_battles()` adicionado ao worker; chamado no startup do
`PublicAlphaService` para marcar batalhas órfãs como `failed`.

---

### BUG-08 🟡 Lógica duplicada no `InProcessBattleWorker` `[BAIXO]`
**Arquivo:** `backend/app/services/battle_worker.py`

`_run_forever` e `run_next` duplicavam a lógica de execução/retry com riscos de divergência.

**Fix:** Método privado `_execute_job(job)` extraído; ambos os métodos delegam para ele.

---

### BUG-09 🟡 Null bytes não rejeitados em `workspace_policy` `[BAIXO]`
**Arquivo:** `backend/app/services/workspace_policy.py`

Caminhos com `\x00` não eram rejeitados, potencial path traversal em sistemas que truncam
no null byte.

**Fix:** Checagem de null byte adicionada em `_validate_workspace_path`.

---

## Gaps documentados (backlog)

Ver `docs/planning/06-tasks-backlog.md` para detalhamento e issues no GitHub.

| # | Gap | Impacto | Esforço |
|---|---|---|---|
| G1 | PostgreSQL persistente (SQLAlchemy + Alembic) | Bloqueador retenção | G |
| G2 | SDK Python (`arena_sdk`) | Desbloqueia agentes reais | M |
| G3 | SSE/WebSocket para battle status | UX live update | M |
| G4 | Integração nativa LLM (Claude/GPT/Ollama) | Demonstra pitch principal | G |
| G5 | CI/CD GitHub Actions | Qualidade de PRs | P |
| G6 | Mais quests (target: 20+) | Retenção de usuários | P/quest |
| G7 | Multi-linguagem (JS/TS, Go, Rust) | Audiência maior | G |
| G8 | DPO export (`GET /battles/export?format=dpo`) | Fine-tuning por camada | M |
| G9 | `cognitive_layers` nas quests | Metadado DPO | P |
| G10 | ELO rating real | Competição mais rica | M |

---

## Análise competitiva

| Projeto | Foco | Avalia | Sandbox | 1v1 | Open Source |
|---|---|---|---|---|---|
| SWE-bench | Bugs reais em repos | Modelos LLM | Não | ❌ | ✅ |
| EvalPlus (HumanEval+) | Geração de código | Modelos LLM | Não | ❌ | ✅ |
| Chatbot Arena (LMSYS) | Qualidade de resposta | Modelos LLM (Elo humano) | Não | ✅ vote | ✅ |
| AgentBench | Tarefas de agentes | Agentes LLM | Parcial | ❌ | ✅ |
| HackerRank/CodeSignal | Competição de código | Humanos | Sim | ❌ | ❌ |
| **Agent Battle Arena** | Estratégia de agentes | **Agentes** (não modelos) | Sim Docker | ✅ | ✅ |

**Nicho real:** único benchmark que avalia agentes (não modelos) em 1v1 com sandbox Docker real e
score determinístico. Genuinamente diferente — mas só funciona depois que os bugs críticos estão
corrigidos (o que este PR faz).

---

## Sequência recomendada pós-fix

```
Semana 1 (este PR)   — 9 bugs corrigidos ✅
Semana 2             — G5: CI/CD GitHub Actions + G9: cognitive_layers
Semana 3             — G6: 5 novas quests (good first issues)
Mês 2                — G1: PostgreSQL + G2: SDK Python
Mês 3                — G4: executor LLM nativo + G3: SSE
Mês 4+               — G7: multi-linguagem + G8: DPO export + G10: ELO
```
