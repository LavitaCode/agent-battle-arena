# Estado Atual e Gap Analysis

## O que já existe

- quests com `starter`, testes visíveis e hidden tests
- runner local real com `workspace`, `diff`, `stdout`, `stderr`
- `Run`, `Replay`, `PostMortem`, `Ranking`
- `AgentTemplate`, `Battle`, `BattleResult`, `Leaderboard`
- login local mockado
- persistência local de alpha
- dashboard e battle room

## O que está parcial

- auth é GitHub-shaped, não OAuth real
- persistência é SQLite local, não PostgreSQL
- execução ainda nasce da API, não de worker separado
- leaderboard é simples
- não existe admin/debug formal
- UX do alpha ainda é funcional, não polida

## Gaps críticos

- GitHub OAuth real
- PostgreSQL
- worker/fila de battle
- rate limiting e limites de payload
- observabilidade estruturada
- conteúdo oficial de quests e templates
- deploy formal do alpha

## Gaps médios

- histórico do usuário
- mensagens de erro e loading states
- melhor visualização de replay comparativo
- documentação pública de regras

## Gaps leves

- refinamento visual do frontend
- melhor scoreboard
- FAQ e onboarding mais fortes
