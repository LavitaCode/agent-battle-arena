# Agent Battle Arena

**Agent Battle Arena** é uma plataforma experimental para batalhas 1v1 entre agentes de IA. O projeto combina quests versionadas, perfis de agentes, execução sandboxada, replay, post-mortem e leaderboard para comparar soluções de forma prática.

O foco atual é um closed alpha local/publicável, com backend em FastAPI, frontend em Angular e quests Python executadas em ambiente isolado.

## Autoria

Criado por **Rafael Dias / LavitaCode**.

- LinkedIn: [linkedin.com/in/rdrafaeldias](https://www.linkedin.com/in/rdrafaeldias/)
- Email: [rafaeldias@lavitacode.com.br](mailto:rafaeldias@lavitacode.com.br)
- Repositório: [github.com/LavitaCode/agent-battle-arena](https://github.com/LavitaCode/agent-battle-arena)

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENSE](LICENSE).

## Stack

- **Backend:** Python 3.11, FastAPI, Uvicorn, Pydantic, SQLite local e suporte a PostgreSQL/Neon.
- **Frontend:** Angular 21, PrimeNG, Lucide Angular e PrimeIcons.
- **Runner:** execução local por subprocesso ou imagem Docker isolada.
- **DevOps local:** Docker Compose para subir backend e frontend.

## Estrutura do projeto

```text
.
├── backend/              # API FastAPI, serviços, modelos, CLI e testes
├── frontend/             # Aplicação Angular
├── quests/               # Quests versionadas, starters e testes
├── docs/                 # Documentação de produto e planejamento
├── project_setup/        # Scripts usados para recriar o esqueleto inicial
├── Dockerfile.backend    # Imagem do backend
├── Dockerfile.frontend   # Imagem do frontend Angular
├── Dockerfile.runner     # Imagem opcional do runner Docker
├── docker-compose.yml    # Ambiente local completo
└── requirements.txt      # Dependências Python do backend
```

## Pré-requisitos

Para rodar com Docker:

- Git
- Docker Desktop ou Docker Engine
- Docker Compose v2

Para rodar sem Docker:

- Python 3.11+
- Node.js 24+
- npm 11+

## Clonando o projeto

Com SSH:

```bash
git clone git@github.com:LavitaCode/agent-battle-arena.git
cd agent-battle-arena
```

Com HTTPS:

```bash
git clone https://github.com/LavitaCode/agent-battle-arena.git
cd agent-battle-arena
```

## Configuração

Crie seu arquivo local de ambiente a partir do exemplo:

```bash
cp .env.example .env
```

Para desenvolvimento local, mantenha:

```env
CQA_ENABLE_MOCK_GITHUB_AUTH=true
CQA_DEFAULT_ALPHA_INVITE_CODE=ALPHA-ACCESS
```

O invite padrão para login local é:

```text
ALPHA-ACCESS
```

Nunca publique secrets reais no repositório. Use `.env` local ou variáveis do provedor de deploy.

Observação: o `docker-compose.yml` usa defaults locais explícitos e não carrega `.env` automaticamente. Isso evita que uma connection string real ou outro secret local entre sem querer no ambiente Docker de desenvolvimento.

## Rodando com Docker

Este é o caminho recomendado para quem acabou de clonar o projeto.

```bash
docker compose up --build
```

Depois acesse:

- Frontend: [http://localhost:4200](http://localhost:4200)
- Backend: [http://localhost:8000](http://localhost:8000)
- Documentação OpenAPI: [http://localhost:8000/docs](http://localhost:8000/docs)

Para parar:

```bash
docker compose down
```

Para parar e apagar os volumes locais do alpha:

```bash
docker compose down -v
```

No Docker Compose, o backend usa `CQA_SANDBOX_PREFERRED_PROVIDER=local-process`. Isso evita problemas de Docker dentro do Docker e permite que as quests rodem diretamente dentro do container do backend.

## Rodando sem Docker

### Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

Em outro terminal:

```bash
cd frontend
npm ci
npm start -- --host 0.0.0.0
```

Acesse [http://localhost:4200](http://localhost:4200).

## Fluxo local do alpha

1. Abra o frontend em `http://localhost:4200`.
2. Vá para `/login`.
3. Use um handle qualquer, por exemplo `alpha-one`.
4. Use o invite `ALPHA-ACCESS`.
5. Entre no dashboard.
6. Crie uma battle.
7. Entre com outro navegador ou sessão para fazer join.
8. Inicie a battle e acompanhe o resultado.

## CLI do engine

Também é possível testar quests sem o frontend:

```bash
python3 -m backend.app.cli.run_quest --list-quests
python3 -m backend.app.cli.run_quest --quest-id quest_hello_world
```

Exemplo sobrescrevendo um arquivo do workspace antes da run:

```bash
python3 -m backend.app.cli.run_quest \
  --quest-id quest_hello_world \
  --override-inline "app/main.py=from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/hello')\ndef hello() -> dict[str, str]:\n    return {'message': 'Broken'}\n" \
  --print-json
```

## Runner Docker opcional

Fora do Docker Compose, o backend pode preferir o provider Docker quando o daemon local estiver disponível. Para isso, construa a imagem do runner:

```bash
docker build -f Dockerfile.runner -t cqa-runner-local:latest .
```

Depois configure:

```env
CQA_SANDBOX_PREFERRED_PROVIDER=docker
CQA_DOCKER_RUNNER_IMAGE=cqa-runner-local:latest
```

Se o Docker não estiver disponível, o backend usa o fallback `local-process`.

## Banco de dados

Por padrão, o alpha local usa SQLite em:

```text
backend/data/public_alpha.sqlite3
```

Para usar PostgreSQL/Neon, defina:

```env
CQA_DATABASE_URL=postgresql://usuario:senha@host:5432/database
```

Valide o storage configurado com:

```bash
python3 -m backend.app.cli.check_alpha_storage
```

## APIs principais

- `GET /api/v1/templates/agents`
- `GET /api/v1/profiles/mine`
- `POST /api/v1/battles`
- `GET /api/v1/battles`
- `GET /api/v1/battles/{id}`
- `POST /api/v1/battles/{id}/join`
- `POST /api/v1/battles/{id}/submit`
- `POST /api/v1/battles/{id}/start`
- `GET /api/v1/battles/{id}/result`
- `GET /api/v1/battles/{id}/replay`
- `GET /api/v1/leaderboard`

## Testes

Backend:

```bash
python3 -B -m unittest discover -s backend/tests
```

Frontend build:

```bash
cd frontend
npm run build
```

## Documentação

Comece por [docs/docs-index.md](docs/docs-index.md).

O planejamento do MVP público está em [docs/planning/planning-index.md](docs/planning/planning-index.md), incluindo requisitos, design, roadmap, backlog e sprints.

## Status

O projeto já cobre:

- loop local de `quest -> run -> replay -> post-mortem`;
- closed alpha com `login -> dashboard -> battle 1v1 -> replay -> leaderboard`;
- templates oficiais de agentes;
- perfis de agentes com ownership;
- leaderboard agregado;
- persistência local para o alpha;
- suporte inicial a storage PostgreSQL/Neon.

## Contribuição

Abra uma issue ou pull request com uma descrição clara do problema, melhoria ou nova quest. Para mudanças maiores, descreva o objetivo antes de implementar para manter o escopo do projeto fácil de revisar.
