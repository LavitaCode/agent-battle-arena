# Runbook de Incidente do Alpha Público

Este runbook define o processo mínimo para operar incidentes do closed alpha do
Agent Battle Arena. Ele cobre triagem, comunicação, contenção e encerramento.

## Severidade

- **SEV1**: indisponibilidade total da API, vazamento de sessão, execução fora do
  sandbox ou corrupção de dados competitivos.
- **SEV2**: battles travadas, fila do worker parada, login indisponível para parte
  dos usuários ou rate limit bloqueando uso legítimo.
- **SEV3**: degradação parcial, métricas inconsistentes, erro visual ou falha em
  uma quest específica sem impacto sistêmico.

## Primeiros 15 minutos

1. Abrir o painel operacional com `GET /api/v1/health`.
2. Se `CQA_ADMIN_DEBUG_TOKEN` estiver configurado, consultar `GET /api/v1/admin/debug`
   com o header `X-CQA-Admin-Token`.
3. Registrar horário, severidade, sintoma principal, commit/deploy atual e número
   aproximado de usuários afetados.
4. Para SEV1 ou suspeita de sandbox, pausar abertura de novas battles até entender
   o alcance.

## Contenção

- Para abuso ou volume anormal, reduzir `CQA_RATE_LIMIT_REQUESTS_PER_MINUTE` e
  `CQA_RATE_LIMIT_AUTH_REQUESTS_PER_MINUTE`.
- Para payloads problemáticos, reduzir `CQA_MAX_WORKSPACE_FILES`,
  `CQA_MAX_WORKSPACE_FILE_BYTES` ou `CQA_MAX_WORKSPACE_TOTAL_BYTES`.
- Para problema de worker, verificar `worker.pending_jobs` no health/debug e
  reiniciar o processo da API somente depois de registrar o snapshot.
- Para risco de sessão, rotacionar cookies/sessões e manter
  `CQA_SESSION_COOKIE_SECURE=true` em ambiente público com HTTPS.

## Encerramento

Um incidente só é encerrado quando:

- o sintoma principal não se reproduz;
- métricas e health check retornam ao esperado;
- usuários afetados têm uma resposta clara;
- existe um item de follow-up no backlog ou um patch aplicado;
- a planning da sprint relevante foi atualizada, quando o incidente muda escopo
  operacional ou requisitos de hardening.
