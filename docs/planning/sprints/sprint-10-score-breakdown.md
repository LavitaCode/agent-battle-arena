# Sprint 10 — Score Breakdown Pós-Alpha

## Status

Concluída.

## Objetivo

Tornar o resultado de uma battle mais explicável para usuários e mantenedores,
começando por um breakdown técnico por participante.

## Entregas

- breakdown de score no contrato de `BattleResult`
- exposição por participante, seat e suites de teste
- base para UI futura de comparação lado a lado

## Critério de aceite

- endpoint `GET /api/v1/battles/{battle_id}/result` retorna um breakdown
  serializável para ambos os participantes de uma battle concluída
  sem quebrar os campos antigos `score_left`, `score_right` e `summary`

## Progresso

- Implementado: contrato `score_breakdown` em `BattleResult`.
- Implementado: breakdown por participante com seat, technical score, total score, duração, total de testes e suites.
- Implementado: tipagem frontend para consumir o novo payload.
- Implementado: cobertura no fluxo público de battle concluída.
