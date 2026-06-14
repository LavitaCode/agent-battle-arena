# RITOS OLIMPO — Gaps G1–G10 (Agent Battle Arena)

> Gerado: 2026-06-14 | Protocolo: OLIMPO_FLIGHT F0→F5  
> Referência: audit-olimpo-2026-06-14.md | PRs já merged: #2 (bugs), #3 (G5+G9)  
> Gaps restantes: G1, G2, G3, G4, G6, G7, G8, G10

---

## Ondas de execução

```
Onda A (agora)   — G6: novas quests
Onda B           — G1: PostgreSQL  →  desbloqueia G2, G8, G10
Onda C           — G2: SDK Python  +  G3: SSE/WebSocket  +  G10: ELO
Onda D           — G4: executor LLM nativo
Onda E           — G7: multi-linguagem  +  G8: DPO export
```

---

## ONDA A — G6: Novas Quests

### F0 — Captura de objetivo
**Objetivo:** Ir de 3 para 8 quests (≥5 novas), cobrindo padrões clássicos de
desafio de código: concorrência, segurança, resiliência, tipagem e I/O assíncrono.

### F1 — PRE_FLIGHT

| Check | Resultado |
|---|---|
| Despacho Hera | Não necessário — escopo < 3 módulos (só `quests/`) |
| Hermes auditou feature nova? | Não necessário — sem wiring novo |
| Atena aprovou? | Não necessário — < 3 módulos |
| Afrodite spec clínica? | Não aplicável |
| HTML/UI aprovado? | Não aplicável |
| Git limpo? | Confirmar antes de criar branch |
| MCPs disponíveis? | Não necessário — escopo local |

**Branch:** `feat/g6-new-quests`  
**PRE_FLIGHT: VERDE — sem War Room.**

### F2 — PLANNING

**Arquivos a criar** (1 por quest, mesma estrutura dos 3 existentes):

```
quests/
  quest_race_condition_fix/
    quest.yaml
    starter/app.py
    tests/test_race_condition.py
    hidden_tests/test_race_hidden.py

  quest_sql_injection_fix/
    quest.yaml
    starter/app.py
    tests/test_sql.py
    hidden_tests/test_sql_hidden.py

  quest_retry_backoff/
    quest.yaml
    starter/retry.py
    tests/test_retry.py
    hidden_tests/test_retry_hidden.py

  quest_async_conversion/
    quest.yaml
    starter/service.py
    tests/test_async.py
    hidden_tests/test_async_hidden.py

  quest_typescript_types/
    quest.yaml
    starter/src/service.ts
    tests/test_types.spec.ts
    hidden_tests/test_types_hidden.spec.ts
```

**Campos obrigatórios em cada `quest.yaml`:**
```yaml
id: "quest_<slug>"
title: "..."
description: |
  ...
difficulty: "silver"  # ou "gold" para G7
mode: "solo"
time_limit_minutes: 25
stack:
  backend: "fastapi"  # ou "typescript" para quest_typescript_types
cognitive_layers:
  - "C3"
  - "C4"
scoring_profile: "standard_app_build_v1"
visible_tests:
  - "tests/test_<slug>.py"
hidden_tests:
  - "hidden_tests/test_<slug>_hidden.py"
```

### F3 — WAR ROOM
Não necessário — escopo exclusivo em `quests/`, sem módulo compartilhado.

### F4 — EXECUÇÃO (TDD-first)

**Ordem por quest:**
1. Escrever `tests/` + `hidden_tests/` (RED — falha sem implementação)
2. Escrever `starter/` com código QUEBRADO propositalmente (o que o competidor recebe)
3. Verificar que os testes falham contra o starter (`unittest discover`)
4. Confirmar que a solução de referência (em `docs/solutions/`) passa tudo (GREEN)
5. Commit + PR

**Contrato de qualidade por quest:**
- Visible tests: 2–4 casos (o competidor vê)
- Hidden tests: 2–4 casos adicionais (somente avaliador vê)
- Starter tem bug óbvio mas bem delimitado
- `requirements` no YAML lista o que se espera em linguagem clara

### F5 — POST_FLIGHT

```
[ ] python -m unittest discover -s backend/tests → 35+ OK
[ ] Cada quest: unittest discover na pasta tests/ falha contra o starter
[ ] Cada quest: solução de referência passa visible + hidden
[ ] YAML válido (python3 -c "import yaml; yaml.safe_load(open('quest.yaml'))")
[ ] PR aberto, label "good first issue" nos 5 quests novos
```

---

## ONDA B — G1: PostgreSQL persistente (SQLAlchemy async + Alembic)

> **Bloqueador:** G2, G8 e G10 dependem de G1. Fazer G1 antes de qualquer um.

### F0 — Captura de objetivo
**Objetivo:** Substituir `AlphaStore` (in-memory) por PostgreSQL via SQLAlchemy 2
async + Alembic, mantendo 100% dos testes existentes passando contra banco real.

### F1 — PRE_FLIGHT

| Check | Resultado |
|---|---|
| Despacho Hera | Necesário — ≥ 4 módulos tocados |
| Hermes auditou? | SIM — varrer `alpha_store.py`, `repositories/in_memory.py`, `core/dependencies.py`, `main.py` |
| Atena aprovou arquitetura? | SIM — decisão: Neon serverless ou SQLite+WAL local |
| Afrodite spec | Não aplicável |
| Git limpo? | Confirmar |
| MCPs disponíveis? | Não necessário |

**Risco único (falar 1x):** migração in-memory→PostgreSQL torna o estado persistente
entre testes; exige `pytest-asyncio` + `@pytest.fixture` com rollback por teste ou
banco de testes dedicado. Sem isso, testes podem interferir entre si.

**Branch:** `feat/g1-postgresql`  
**PRE_FLIGHT: REQUER War Room.**

### F2 — PLANNING

**Módulos tocados:**
```
backend/app/
  core/
    database.py          # NOVO — engine async + sessionmaker
    dependencies.py      # MODIFICAR — injetar AsyncSession
  models/
    db_models.py         # NOVO — SQLAlchemy ORM models
  repositories/
    sqlalchemy/
      __init__.py        # NOVO
      user_repo.py       # NOVO
      battle_repo.py     # NOVO
      profile_repo.py    # NOVO
  services/
    alpha_store.py       # MODIFICAR — delegar para repos SQLAlchemy
alembic/
  env.py                 # NOVO
  versions/
    0001_initial.py      # NOVO — tabelas users/battles/profiles/etc
requirements.txt         # ADICIONAR: sqlalchemy[asyncio], alembic, asyncpg
```

**Sequência de entrega:**
1. `db_models.py` — ORM puro, sem lógica
2. `alembic/` — migration inicial (CREATE TABLE)
3. Repos SQLAlchemy implementam a mesma interface de `repositories/base.py`
4. `dependencies.py` — swap in-memory → SQLAlchemy condicionado a `DATABASE_URL`
5. Testes adaptados com fixture `db_session` + rollback
6. `alpha_store.py` vira fachada sobre os repos (backward compat)

### F3 — WAR ROOM (obrigatório — 4 módulos)

**Decisão arquitetural central:** qual banco no ambiente de desenvolvimento?

| Opção | Pro | Contra |
|---|---|---|
| **Neon serverless** (PostgreSQL cloud) | Gratuito, sem instalação local, mesma infra de prod | Latência rede, requer `DATABASE_URL` configurada |
| **SQLite + WAL** local | Zero dependência externa, rápido em dev | Dialeto diferente do Postgres em prod (ARRAY, UUID nativo) |
| **PostgreSQL local via Docker** | Idêntico à prod, sem custo de rede | Dev precisa ter Docker rodando |

**Recomendação Ayla:** Neon serverless para CI + Docker para dev local, com
`DATABASE_URL` no `.env`. SQLite vetado — dialeto divergente cria bugs silenciosos.

**Decisão final:** Rafael escolhe. Sem escolha = Neon + Docker.

### F4 — EXECUÇÃO (TDD-first)

**Ordem:**
1. Afrodite: contrato das interfaces `UserRepository`, `BattleRepository` (ABC formal)
2. Apolo RED: testes falham sem implementação SQLAlchemy
3. Artemis honesty audit: confirma que RED é RED de verdade
4. Apolo GREEN: implementar repos + migration
5. Afrodite runtime: rodar migrations contra banco de testes
6. Artemis Pre-APPROVE: revisão de segurança (SQL injection via ORM, pool size)
7. Hefesto Retro Gate: build compila, 35+ testes passando, migration `upgrade head` limpa
8. Commit (zero push até Rafael revisar)

### F5 — POST_FLIGHT

```
[ ] alembic upgrade head sem erro
[ ] alembic downgrade -1 + upgrade head idempotente
[ ] 35+ testes backend verdes contra banco de testes
[ ] DATABASE_URL ausente → servidor sobe com in-memory (fallback gracioso)
[ ] DATABASE_URL presente → servidor persiste dados entre restarts
[ ] Nenhum campo `any` introduzido
[ ] RATE_LIMIT, SESSION_COOKIE_SECURE mantidos
```

---

## ONDA C — G2: SDK Python (`arena_sdk`)

> **Depende de G1** — precisa de dados persistidos para testar round-trip.

### F0 — Captura de objetivo
**Objetivo:** Pacote PyPI `arena_sdk` com `ArenaClient` que encapsula auth, criação
de batalha, submissão e polling de resultado. Desbloqueia integração de agentes
externos sem conhecimento do HTTP interno.

### F1 — PRE_FLIGHT

| Check | Resultado |
|---|---|
| Despacho Hera | Não necessário — SDK é repo separado ou `sdk/` isolado |
| Hermes auditou? | Sim — verificar API v1 endpoints existentes para garantir contrato estável |
| Atena aprovou? | Sim — decisão de estrutura do pacote (src layout vs flat) |
| Git limpo? | Confirmar |

**Risco (1x):** SDK acoplado a contrato instável (in-memory) cria breaking changes
assim que G1 mudar respostas. Ideal: publicar SDK somente após G1 merged.

**Branch:** `feat/g2-arena-sdk`

### F2 — PLANNING

```
sdk/
  arena_sdk/
    __init__.py          # ArenaClient exportado aqui
    client.py            # ArenaClient — requests + httpx
    models.py            # dataclasses Battle, Run, Quest (sem Pydantic)
    exceptions.py        # ArenaError, RateLimitError, AuthError
  tests/
    test_client.py       # testes contra servidor local (httpx.Client mock)
  pyproject.toml         # nome=arena-sdk, versão=0.1.0
  README.md
```

**Interface mínima (contrato público v0.1):**
```python
client = ArenaClient(base_url="http://localhost:8000", token="...")
battle = client.battles.create(quest_id="quest_hello_world", profile_id="...")
client.battles.submit(battle.id, workspace_files={"app/main.py": code})
result = client.battles.wait_result(battle.id, timeout=120)
```

### F3 — WAR ROOM
Não necessário — SDK é módulo isolado sem dependência circular.

### F4 — EXECUÇÃO

1. Escrever `test_client.py` com `respx` mock — RED
2. Implementar `ArenaClient` — GREEN
3. Testes de integração contra servidor real (requer `DATABASE_URL`)
4. `pyproject.toml` + `pip install -e sdk/` funciona
5. Commit

### F5 — POST_FLIGHT
```
[ ] pip install -e sdk/ sem erro
[ ] python -m pytest sdk/tests/ — todos verdes
[ ] client.battles.create() retorna Battle com id válido (contra servidor local)
[ ] client.battles.wait_result() retorna BattleResult com winner
[ ] Nenhum import de módulo interno do backend
```

---

## ONDA C — G3: SSE / WebSocket para battle status

### F0 — Captura de objetivo
**Objetivo:** Endpoint `GET /battles/{id}/stream` que emite eventos SSE enquanto
a batalha está em andamento (`queued` → `running` → `completed`/`failed`), eliminando
polling no frontend.

### F1 — PRE_FLIGHT

| Check | Resultado |
|---|---|
| Hermes auditou? | Sim — verificar `battle_worker.py` e onde `update_battle_status` é chamado |
| Atena aprovou? | Sim — SSE (EventSourceResponse) vs WebSocket (mais complexo) |
| Git limpo? | Confirmar |

**Risco (1x):** SSE não funciona atrás de proxy reverso sem `X-Accel-Buffering: no`.
Documentar no deployment guide.

**Branch:** `feat/g3-sse-battle-stream`

### F2 — PLANNING

```
backend/app/
  api/v1/endpoints/
    battles.py           # ADICIONAR rota GET /{id}/stream
  services/
    battle_event_bus.py  # NOVO — asyncio.Queue por battle_id, pub/sub local
```

**Contrato do endpoint:**
```
GET /api/v1/battles/{battle_id}/stream
Accept: text/event-stream

data: {"battle_id": "...", "status": "queued",   "ts": "..."}
data: {"battle_id": "...", "status": "running",  "ts": "..."}
data: {"battle_id": "...", "status": "completed","ts": "...", "winner": "..."}
```

**Integração frontend (Angular):**
```typescript
const es = new EventSource(`/api/v1/battles/${id}/stream`);
es.onmessage = (e) => { const ev = JSON.parse(e.data); ... };
```

### F3 — WAR ROOM
Não necessário — toca 2 módulos (novo endpoint + novo bus).

### F4 — EXECUÇÃO

1. `battle_event_bus.py` — dicionário `battle_id → asyncio.Queue`
2. `battle_worker.py` publica eventos no bus ao mudar status
3. Rota SSE lê da fila com `async for`
4. Testes com `httpx.AsyncClient` + `TestClient` streaming
5. Frontend: troca `setInterval` por `EventSource` na tela de batalha

### F5 — POST_FLIGHT
```
[ ] curl -N .../stream recebe 3 eventos para batalha completa
[ ] Batalha encerrada (completed/failed) fecha o stream automaticamente
[ ] Frontend não faz mais polling após merge
[ ] tsc --noEmit limpo no frontend
```

---

## ONDA C — G10: ELO rating

> **Depende de G1** — ELO precisa de persistência para ser significativo.

### F0 — Captura de objetivo
**Objetivo:** Sistema ELO K=32 calculado a cada batalha completada. `GET /leaderboard`
retorna agentes ordenados por ELO com histórico de Δ por batalha.

### F1 — PRE_FLIGHT

| Check | Resultado |
|---|---|
| Hermes auditou? | Sim — `alpha_store.py` lista_leaderboard, `BattleResult` |
| Atena aprovou? | Sim — ELO puro vs TrueSkill (TrueSkill melhor para ties mas mais complexo) |
| Git limpo? | Confirmar |

**Risco (1x):** ELO in-memory zera a cada restart até G1 estar merged. Lançar
após G1.

**Branch:** `feat/g10-elo`

### F2 — PLANNING

```
backend/app/
  services/
    elo_service.py       # NOVO — delta(Ra, Rb, outcome) → (Ra', Rb')
  models/
    leaderboard.py       # MODIFICAR — adicionar elo_rating, elo_delta, battles_count
  services/
    public_alpha_service.py  # MODIFICAR — chamar elo_service._run_battle
```

**Fórmula (K=32, padrão FIDE):**
```python
def expected(ra: float, rb: float) -> float:
    return 1 / (1 + 10 ** ((rb - ra) / 400))

def update(ra: float, rb: float, score_a: float) -> tuple[float, float]:
    ea = expected(ra, rb)
    return ra + 32 * (score_a - ea), rb + 32 * ((1 - score_a) - (1 - ea))
# score_a = 1.0 (vitória), 0.5 (empate), 0.0 (derrota)
```

### F3 — WAR ROOM
Não necessário — módulo novo + 1 integração.

### F4 — EXECUÇÃO

1. `elo_service.py` com testes unitários puros (sem banco)
2. `public_alpha_service._run_battle` chama ELO update ao salvar resultado
3. `list_leaderboard()` retorna ordenado por `elo_rating` DESC
4. Migration Alembic adiciona coluna `elo_rating FLOAT DEFAULT 1200`

### F5 — POST_FLIGHT
```
[ ] ELO de dois agentes se ajusta após 3 batalhas (teste manual)
[ ] GET /leaderboard retorna ordenado por elo_rating
[ ] Empate → ambos ficam ~iguais ao inicial
[ ] Coluna elo_rating na migration idempotente
```

---

## ONDA D — G4: Executor LLM nativo (Claude/GPT/Ollama)

### F0 — Captura de objetivo
**Objetivo:** `AgentExecutor` que, dado `agent_profile.executor = "claude-sonnet"`,
chama a API do LLM com o prompt da quest e retorna `workspace_files` prontos para
submissão — competição autônoma sem humano digitando código.

### F1 — PRE_FLIGHT

| Check | Resultado |
|---|---|
| Despacho Hera | Necessário — ≥ 4 módulos + integração externa |
| Hermes auditou? | Sim — varrer `agent_profile.py`, `battle_worker.py`, `execution_service.py` |
| Atena aprovou? | Sim — onde o executor LLM é chamado (antes ou durante batalha) |
| Afrodite spec | Sim — validar output do LLM antes de entrar no sandbox |
| Git limpo? | Confirmar |

**Risco (1x):** LLM pode gerar código malicioso. O output DEVE passar pelo
`validate_workspace_files()` e pelo sandbox antes de qualquer exec. Não executar
output LLM fora do sandbox em nenhuma hipótese.

**Branch:** `feat/g4-llm-executor`

### F2 — PLANNING

```
backend/app/
  executors/
    __init__.py
    base.py              # AgentExecutor ABC — execute(quest) → dict[str,str]
    claude_executor.py   # ClaudeExecutor — anthropic SDK
    openai_executor.py   # OpenAIExecutor — openai SDK
    ollama_executor.py   # OllamaExecutor — httpx direto
  services/
    executor_registry.py # NOVO — mapeia profile.executor → ExecutorClass
  models/
    agent_profile.py     # MODIFICAR — campo executor: str | None
```

**Prompt template base:**
```
Você é um agente de código competindo na Agent Battle Arena.
Quest: {quest.title}
Descrição: {quest.description}
Requisitos: {quest.requirements}
Código starter:
{starter_files}

Responda APENAS com JSON: {"workspace_files": {"path": "conteudo"}}
```

**Validação obrigatória do output:**
```python
raw = executor.execute(quest)
validate_workspace_files(raw["workspace_files"])  # §422 fail-closed
```

### F3 — WAR ROOM (obrigatório — ≥ 4 módulos + risco de segurança)

**Questões a resolver:**
1. Rate limiting por executor (LLMs têm TPM/RPM)
2. Timeout máximo por execução (sugestão: 60s)
3. Fallback se LLM timeout: `workspace_files = {}` (submissão vazia, perde)
4. Quais executores são opt-in (requerem API key no profile)

### F4 — EXECUÇÃO

1. `base.py` ABC + contrato
2. `claude_executor.py` — TDD com mock da Anthropic API
3. `executor_registry.py`
4. `battle_worker.py` — se `profile.executor` presente, chama executor antes de criar `run`
5. Testes de integração (mock executor retorna código fixo)
6. Tela frontend: badge "🤖 Auto" em profiles com executor

### F5 — POST_FLIGHT
```
[ ] Mock executor gera workspace_files que passam em validate_workspace_files
[ ] Batalha entre 2 agentes LLM completa sem intervenção humana
[ ] Timeout 60s → workspace_files={} → derrota por 0 testes
[ ] API key ausente → executor retorna erro claro (HTTP 400, não 500)
[ ] tsc --noEmit limpo
[ ] 35+ testes backend verdes
```

---

## ONDA E — G7: Multi-linguagem (JS/TS, Go, Rust)

> **Depende de G1** (storage) + **G4** (executores geram código em outras linguagens).

### F0 — Captura de objetivo
**Objetivo:** Sandbox capaz de compilar e testar código Go e JavaScript/TypeScript,
além do Python existente, detectando a linguagem pelo campo `stack.backend` da quest.

### F1 — PRE_FLIGHT

| Check | Resultado |
|---|---|
| Despacho Hera | Necessário — sandbox + CI + quests novos |
| Hermes auditou? | Sim — varrer `runner.py`, `DockerSandboxProvider`, Dockerfile |
| Atena aprovou? | Sim — imagem Docker única multi-linguagem vs imagens por linguagem |
| Git limpo? | Confirmar |

**Risco (1x):** Imagem Docker multi-linguagem (Python+Go+Node) fica pesada (~2GB).
Alternativa: imagens separadas com tag `python3.12-runner`, `node22-runner`, `go1.22-runner`.
Recomendação: imagens separadas por linguagem, seleção por `quest.stack.backend`.

**Branch:** `feat/g7-multilang`

### F2 — PLANNING

```
docker/
  runners/
    python/Dockerfile    # existente
    nodejs/Dockerfile    # NOVO — node:22-slim + jest
    go/Dockerfile        # NOVO — golang:1.22-alpine
quests/
  quest_async_js/        # NOVO — JavaScript
  quest_typed_go/        # NOVO — Go
backend/app/
  sandbox/
    runner.py            # MODIFICAR — selecionar imagem por stack.backend
    images.py            # NOVO — mapa stack → docker image tag
```

**Mapeamento imagem:**
```python
STACK_IMAGE = {
    "fastapi":    settings.DOCKER_RUNNER_IMAGE,   # python
    "express":    "arena-runner-nodejs:latest",
    "go":         "arena-runner-go:latest",
    "default":    settings.DOCKER_RUNNER_IMAGE,
}
```

### F3 — WAR ROOM (obrigatório)

**Questão:** como rodar testes Go dentro do container de forma determinística?
- Go: `go test ./...` nativo
- Node: `jest --passWithNoTests` ou `node --test`
- Decisão: cada imagem tem um script `run_tests.sh` padronizado

### F4 — EXECUÇÃO

1. `images.py` — mapeamento + seleção de imagem
2. Dockerfile para Node e Go com `run_tests.sh`
3. `DockerSandboxProvider` usa `images.py` ao montar comando
4. 2 quests novas (uma Go, uma JavaScript)
5. CI: adicionar step `docker build` para cada nova imagem

### F5 — POST_FLIGHT
```
[ ] Quest Go: solução correta passa hidden tests no container Go
[ ] Quest JS: solução correta passa hidden tests no container Node
[ ] docker build de cada imagem sem erro no CI
[ ] Imagem Python existente não regride
[ ] 35+ testes backend verdes
```

---

## ONDA E — G8: DPO export

> **Depende de G1** (dados persistidos) + G9 (cognitive_layers) já merged.

### F0 — Captura de objetivo
**Objetivo:** `GET /battles/export?format=dpo` retorna JSONL com pares
`(prompt, chosen, rejected)` por cognitive_layer, pronto para fine-tuning DPO.

### F1 — PRE_FLIGHT

| Check | Resultado |
|---|---|
| Hermes auditou? | Sim — `BattleResult`, `BattleRunBundle`, `cognitive_layers` |
| Atena aprovou? | Sim — formato exato do JSONL (HuggingFace DPO padrão) |
| Git limpo? | Confirmar |

**Branch:** `feat/g8-dpo-export`

### F2 — PLANNING

```
backend/app/
  api/v1/endpoints/
    battles.py           # ADICIONAR rota GET /export
  services/
    dpo_export_service.py  # NOVO — constrói pares DPO
  models/
    dpo.py               # NOVO — DPOPair dataclass
```

**Formato de saída (por linha do JSONL):**
```json
{
  "prompt": "Quest: Hello World API\nImplementar...",
  "chosen": "# solução do vencedor\n...",
  "rejected": "# solução do perdedor\n...",
  "cognitive_layer": "C2",
  "battle_id": "battle-...",
  "quest_id": "quest_hello_world"
}
```

**Regras de construção:**
- `chosen` = workspace_files do participante com maior `technical_score`
- `rejected` = workspace_files do participante perdedor
- Empates (tie) são excluídos do export
- Filtragem por `?cognitive_layer=C3` suportada

### F3 — WAR ROOM
Não necessário — módulo novo + 1 rota.

### F4 — EXECUÇÃO

1. `dpo_export_service.py` com testes unitários
2. Rota `GET /battles/export` com streaming (`StreamingResponse`)
3. Teste de integração: 2 batalhas completadas → export retorna 2 linhas JSONL

### F5 — POST_FLIGHT
```
[ ] GET /battles/export?format=dpo retorna Content-Type: application/x-ndjson
[ ] Cada linha é JSON válido com campos prompt/chosen/rejected/cognitive_layer
[ ] Empates não aparecem no export
[ ] ?cognitive_layer=C3 filtra corretamente
[ ] Sem vazamento de dados de sessão no export (campos sensíveis omitidos)
```

---

## Matriz de dependências

```
G6 (quests) ──── independente ──── pode começar AGORA

G1 (PostgreSQL)
  └── G2 (SDK)
  └── G8 (DPO export)
  └── G10 (ELO)

G4 (LLM executor) ──── depende de: G1 (persistência) + G3 (SSE, UX)

G7 (multi-lang) ──── depende de: G1 + sandbox estável (G4 opcional mas útil)

G3 (SSE) ──── independente (mas mais útil com G4 ativo)
```

---

## Critério de prioridade Rafael-decide

| Gap | Impacto comunidade | Impacto produto | Esforço | Prioridade |
|---|---|---|---|---|
| G6 (quests) | Alto — conteúdo | Alto — retenção | Baixo | **P0** |
| G1 (PostgreSQL) | Baixo visível | Alto — desbloqueia tudo | Grande | **P1** |
| G3 (SSE) | Médio — UX | Médio | Médio | P2 |
| G2 (SDK) | Alto — devs | Alto — integrações | Médio | P2 |
| G10 (ELO) | Alto — gamificação | Alto — retenção | Médio | P3 |
| G4 (LLM) | Altíssimo — demo | Altíssimo — diferencial | Grande | P3 |
| G8 (DPO export) | Alto — pesquisa | Médio | Médio | P4 |
| G7 (multi-lang) | Alto — audiência | Alto | Grande | P4 |

---

*Documento gerado pelo Protocolo OLIMPO_FLIGHT — Ayla (Olimpo Platform)*  
*PRs de referência: #2 (bugs), #3 (G5+G9)*
