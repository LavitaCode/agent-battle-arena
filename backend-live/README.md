# Backend Live — Modo B (Arena Live 3D)

API **Go** exclusiva do **Modo B**. Não substitui nem depende do `backend/` Python (Modo A — Quests).

| Modo | Pasta | Stack |
|------|-------|-------|
| A — Arena Quests | `backend/` | Python 3.11 + FastAPI |
| B — Arena Live 3D | `backend-live/` | Go 1.22+ (stdlib `net/http`) |

Prefixo de rotas: `/api/v1/live/…`

## Requisitos

- [Go 1.22+](https://go.dev/dl/)

## Rodar local

```bash
cd backend-live
go run ./cmd/api
```

Health: `GET http://localhost:8080/api/v1/live/health`  
Porta: `LIVE_API_ADDR` (default `:8080`).

## Testes

```bash
cd backend-live
go test ./...
```

## Escopo atual (scaffold)

- Health check sob `/api/v1/live/health`
- Auth, matchmaking, protocolo e game server → specs UNI-02+
