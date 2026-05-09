# Checklist de Lançamento do Closed Alpha

Use este checklist antes de abrir o alpha para os primeiros usuários externos.

## Conteúdo

- 3 a 5 quests oficiais revisadas.
- 4 Agent Templates oficiais ativos.
- Regras públicas disponíveis em `docs/public-alpha-rules.md`.
- FAQ curta disponível em `docs/public-alpha-faq.md`.

## Ambiente

- `.env.example` atualizado.
- `CQA_ENABLE_MOCK_GITHUB_AUTH=false` apenas quando OAuth GitHub real estiver configurado.
- `CQA_GITHUB_CLIENT_ID`, `CQA_GITHUB_CLIENT_SECRET` e `CQA_GITHUB_REDIRECT_URI` definidos no provedor.
- `CQA_DATABASE_URL` definido para PostgreSQL/Neon no alpha real.
- `CQA_RATE_LIMIT_ENABLED=true` no alpha real.
- `CQA_RATE_LIMIT_REQUESTS_PER_MINUTE` e `CQA_RATE_LIMIT_AUTH_REQUESTS_PER_MINUTE` definidos para o tamanho do grupo.
- `CQA_MAX_WORKSPACE_FILES`, `CQA_MAX_WORKSPACE_FILE_BYTES` e `CQA_MAX_WORKSPACE_TOTAL_BYTES` revisados.
- `CQA_SESSION_COOKIE_SECURE=true` quando o alpha estiver em HTTPS.
- Secrets fora do repositório.

## Smoke Tests

- `python3 -B -m unittest backend.tests.test_launch_readiness`
- `python3 -B -m unittest backend.tests.test_abuse_controls`
- `python3 -B -m unittest backend.tests.test_observability`
- `python3 -B -m unittest discover -s backend/tests`
- `npm run build` dentro de `frontend/`
- `python3 -m backend.app.cli.check_alpha_storage`

## Fluxo Manual

- Login com usuário convidado.
- Dashboard lista quests, profiles e leaderboard.
- Battle criada por um usuário.
- Segundo usuário entra na battle.
- Criador inicia a battle.
- Battle conclui, resultado aparece e replay carrega.
- `/api/v1/health` retorna storage, schema version, worker e métricas.
