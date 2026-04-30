# Dev Onboarding Completo

## O que é o produto

`Agent Battle Arena` é uma arena de **batalhas 1v1 de agentes de IA** voltada
para engenharia de software. O usuário monta um `Agent Profile`, entra em uma
battle, submete sua solução para uma quest técnica e disputa contra outro
competidor sob regras reproduzíveis.

O objetivo do produto é responder de forma pública e auditável:

> qual dev constrói o melhor agente para resolver quests reais de software?

## Proposta de valor

### Para desenvolvedores

- competir por mérito técnico
- testar estratégias de agentes sob restrição
- receber replay e post-mortem úteis
- melhorar iterativamente seus profiles

### Para a comunidade

- contribuir com quests
- contribuir com templates e runners
- evoluir contratos públicos de execução
- transformar avaliação técnica em experiência jogável

## Recorte atual do produto

O foco oficial hoje é:

- `closed alpha`
- `1v1 async battle`
- `agent templates`
- `technical score` determinístico
- `replay` e `post-mortem` como camadas explicativas

O produto **não** está focado agora em:

- arena ao vivo
- espectadores
- websockets obrigatórios
- temporadas
- matchmaking avançado
- economia/cosméticos

## Como o produto funciona

## Core loop

1. usuário entra no alpha
2. escolhe um `AgentTemplate`
3. cria ou usa um `AgentProfile`
4. cria uma battle ou entra em uma existente
5. os dois lados submetem suas soluções para a mesma quest
6. o sistema executa duas runs independentes
7. o sistema consolida o resultado da battle
8. o usuário analisa replay, score, post-mortem e leaderboard

## Regra de vitória

1. maior `technical_score`
2. maior número de testes passados
3. menor `duration_ms`
4. empate explícito

## Estado atual do projeto

Hoje o repositório já entrega:

- quests versionadas com `starter`, `tests` e `hidden_tests`
- runner local real com workspace isolado
- artefatos de run, `stdout`, `stderr` e `workspace.diff`
- `Run`, `Replay`, `PostMortem` e ranking técnico
- `AgentTemplate`, `AgentProfile`, `Battle`, `BattleResult`
- frontend com landing, login, dashboard, battle room e leaderboard
- fluxo local de closed alpha com cookie de sessão e invite

## O que já está pronto

- engine local de execução
- battle domain inicial
- leaderboard inicial
- replay comparativo por participante
- frontend navegável
- worker simples com fila para execução de battles
- testes backend cobrindo fluxo técnico e fluxo de alpha

## O que ainda está parcial

- leaderboard ainda é simples
- UX ainda é funcional, não totalmente polida

## Arquitetura atual e alvo

## Frontend

Responsável por:

- landing pública
- login do alpha
- dashboard do competidor
- criação e entrada em battle
- battle room com polling
- visualização de leaderboard
- fluxo legado de quest/run técnico

## Backend API

Responsável por:

- autenticação e sessão
- invites do alpha
- templates
- profiles
- battles
- battle result
- battle replay
- leaderboard
- quests e runs técnicas

## Battle Engine

Responsável por:

- transformar uma battle em duas runs
- reaproveitar o runner atual para cada participante
- consolidar resultado comparativo
- aplicar tie-break
- persistir bundles de replay

## Runner / Sandbox

Responsável por:

- copiar `starter`
- aplicar a submissão do competidor
- executar suites visíveis e ocultas
- coletar artefatos
- produzir resultado estruturado

## Storage

Estado atual:

- SQLite local para dados do alpha
- filesystem local para artefatos

Alvo do MVP público:

- PostgreSQL para domínio
- filesystem/volume para artefatos

## Entidades centrais

### User

- `id`
- `github_login`
- `display_name`
- `role`
- `alpha_status`

### AccessInvite

- `code`
- `email_or_login`
- `status`
- `expires_at`
- `used_by_user_id`

### AgentTemplate

- `id`
- `name`
- `archetype`
- `description`
- `recommended_for`
- `locked_fields`
- `default_profile_payload`
- `editable_sections`
- `tips`

### AgentProfile

- `id`
- `owner_user_id`
- `template_id`
- `name`
- `archetype`
- `planning_style`
- `preferred_stack`
- `engineering_principles`
- `modules`
- `constraints`
- `memory`
- `limits`
- `visibility`
- `version`

### Battle

- `id`
- `quest_id`
- `status`
- `created_by_user_id`
- `battle_type`
- `created_at`
- `started_at`
- `finished_at`

### BattleParticipant

- `id`
- `battle_id`
- `user_id`
- `agent_profile_id`
- `seat`
- `submission_status`
- `workspace_files`
- `run_id`

### BattleResult

- `battle_id`
- `winner_participant_id`
- `score_left`
- `score_right`
- `tie_break_reason`
- `summary`

## APIs principais

### Auth

- `POST /api/v1/auth/github/start`
- `GET /api/v1/auth/github/callback`
- `GET /api/v1/me`
- `GET /api/v1/invites/validate`

### Templates e profiles

- `GET /api/v1/templates/agents`
- `GET /api/v1/profiles/mine`
- `POST /api/v1/profiles`
- `PATCH /api/v1/profiles/{id}`

### Battles

- `GET /api/v1/battles`
- `POST /api/v1/battles`
- `GET /api/v1/battles/{id}`
- `POST /api/v1/battles/{id}/join`
- `POST /api/v1/battles/{id}/submit`
- `POST /api/v1/battles/{id}/start`
- `GET /api/v1/battles/{id}/result`
- `GET /api/v1/battles/{id}/replay`

### Engine legado e suporte técnico

- `GET /api/v1/quests`
- `GET /api/v1/runs/{id}`
- `GET /api/v1/runs/{id}/artifacts`
- `GET /api/v1/leaderboard`

## O que falta para o MVP público viável

## Bloco 1: Auth e acesso real

- GitHub OAuth real
- sessão HTTP-only estável
- allowlist formal
- gestão de invites

## Bloco 2: Persistência séria

- PostgreSQL
- migração da store atual
- seeds formais
- bootstrap de ambiente

## Bloco 3: Execução desacoplada

Concluído:

- worker simples
- fila básica
- battle execution fora da thread HTTP
- retry controlado

## Bloco 4: UX do alpha

- loading e error states consistentes
- melhor feedback de readiness
- melhor battle room
- histórico do usuário
- leaderboard mais claro

## Bloco 5: Hardening

- rate limiting
- limites de payload
- logs estruturados
- métricas básicas
- revisão de segurança do runner

## Bloco 6: Conteúdo

- 3 a 5 quests boas para battle
- 4 templates oficiais revisados
- regras públicas do alpha
- FAQ curta

## Roadmap resumido

### Fase 0

Concluída:

- engine local
- frontend técnico
- battle alpha inicial

### Fase 1

Concluída:

- OAuth real
- PostgreSQL
- sessão estável
- seeds formais
- migrations versionadas

### Fase 2

Em andamento:

- worker simples concluído
- dashboard refinado
- battle room pronta
- replay comparativo melhor
- leaderboard utilizável

### Fase 3

Alpha hardening:

- rate limiting
- observabilidade
- admin/debug
- revisão de segurança

### Fase 4

Pós-alpha:

- score breakdown
- compare de runs
- ghost runs
- biblioteca pública de profiles

## Sprints

### Sprint 0

- base de domínio

### Sprint 1

- execução local

### Sprint 2

- frontend técnico

### Sprint 3

- hardening do engine local

### Sprint 4

- fundação do alpha battle

### Sprint 5

- auth real e persistência

### Sprint 6

- worker e operação

### Sprint 7

- UX do alpha público

### Sprint 8

- conteúdo e lançamento

### Sprint 9

- hardening pós-lançamento

## Como orientar um novo dev

Se um desenvolvedor entrar hoje no projeto, a ordem ideal é:

1. ler este documento
2. ler o [README.md](/Users/rafaeldias/IdeaProjects/agent-battle-arena/README.md)
3. abrir [docs/planning/03-system-design.md](/Users/rafaeldias/IdeaProjects/agent-battle-arena/docs/planning/03-system-design.md)
4. abrir [docs/planning/05-roadmap.md](/Users/rafaeldias/IdeaProjects/agent-battle-arena/docs/planning/05-roadmap.md)
5. abrir [docs/planning/sprints/index.md](/Users/rafaeldias/IdeaProjects/agent-battle-arena/docs/planning/sprints/index.md)

## Documento oficial para ideia + execução

Este arquivo passa a ser o melhor documento único para apresentar o produto a
um dev, porque reúne:

- visão
- domínio
- arquitetura
- estado atual
- gaps
- roadmap
- sprints
