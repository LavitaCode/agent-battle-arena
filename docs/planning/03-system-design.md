# System Design

## Arquitetura alvo

### Frontend

- landing pública
- login alpha
- dashboard
- battle room
- resultado comparativo
- leaderboard

### Backend API

- auth
- invites
- templates
- profiles
- battles
- result
- replay
- leaderboard

### Battle Engine

- transforma battle em duas runs
- aplica regras de tie-break
- consolida `BattleResult`
- persiste bundles de replay

### Runner / Sandbox

- copia `starter`
- aplica submissão
- executa suites
- coleta artefatos
- devolve resultado estruturado

### Storage

- PostgreSQL para domínio
- filesystem/volume para artefatos no alpha

## Entidades centrais

- `User`
- `AccessInvite`
- `AgentTemplate`
- `AgentProfile`
- `Battle`
- `BattleParticipant`
- `BattleResult`
- `BattleReplayBundle`

## Regras de decisão

1. maior `technical_score`
2. maior número de testes passados
3. menor `duration_ms`
4. empate explícito
