# Backend Live — Modo B (Arena Live 3D)

API **ASP.NET Core 8** exclusiva do **Modo B**. Não substitui nem depende do `backend/` Python (Modo A — Quests).

| Modo | Pasta | Stack |
|------|-------|-------|
| A — Arena Quests | `backend/` | Python 3.11 + FastAPI |
| B — Arena Live 3D | `backend-live/` | .NET 8 + ASP.NET Core Minimal APIs |

Prefixo de rotas: `/api/v1/live/…`

## Requisitos

- [.NET SDK 8](https://dotnet.microsoft.com/download/dotnet/8.0)

## Rodar local

```bash
cd backend-live
dotnet run --project src/AgentBattleArena.Live.Api
```

Health: `GET http://localhost:5xxx/api/v1/live/health` (porta em `launchSettings.json`).

## Testes

```bash
cd backend-live
dotnet test
```

## Escopo atual (scaffold)

- Health check versionado sob `/api/v1/live`
- Solução + projeto de testes xUnit
- Auth, matchmaking, protocolo e game server → specs UNI-02+
