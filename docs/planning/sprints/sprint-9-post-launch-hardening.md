# Sprint 9 — Hardening Pós-Lançamento

## Status

Concluída.

## Objetivo

Transformar o alpha em uma operação estável e sustentável.

## Entregas

- rate limiting
- métricas
- admin/debug
- revisão de segurança do runner
- processo de incidente

## Critério de aceite

- operação do alpha é sustentável sem resets frequentes

## Progresso

- Implementado: rate limiting em memória para auth, invite validate e writes de battle.
- Implementado: validação centralizada de `workspace_files` para paths, quantidade de arquivos e tamanho do payload.
- Implementado: aplicação da validação em run solo e battle create/join/submit.
- Implementado: runner deixa de ignorar paths inválidos silenciosamente.
- Implementado: cookie de sessão respeita `CQA_SESSION_COOKIE_SECURE`.
- Implementado: `.env.example` documenta rate limit, limites de workspace e secure cookie.
- Implementado: testes de abuse controls em `backend/tests/test_abuse_controls.py`.
- Implementado: métricas em memória para requests, rate-limit hits e ciclo de battles.
- Implementado: `/api/v1/health` com storage backend, schema version, fila do worker e snapshot de métricas.
- Implementado: testes de observabilidade em `backend/tests/test_observability.py`.
- Implementado: endpoint protegido `GET /api/v1/admin/debug` com snapshot operacional para mantenedores.
- Implementado: hardening adicional do runner Docker com `--read-only`, `no-new-privileges`, `--cap-drop ALL` e `tmpfs` restrito.
- Implementado: runbook de incidente em `docs/incident-response.md`.
