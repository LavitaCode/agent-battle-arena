# Backlog de Contribuições

Issues marcadas no GitHub com os labels abaixo. Aqui está o detalhamento.

---

## `architecture` — dívida estrutural (P1)

### Refatorar para 7 camadas cognitivas explícitas

**Label:** `architecture` + `help wanted`

A Arena foi desenhada sobre 7 camadas cognitivas (C1 Percepção → C7 Avaliação), mas a
implementação atual tem 6 camadas — C7 (Avaliação/Reflexão) existe de forma rudimentar,
sem tag cognitiva nas batalhas e sem export DPO estruturado.

**O que precisa mudar:**

1. Adicionar campo `cognitive_layer` no modelo `Quest` (`quest.yaml`)
   ```yaml
   cognitive_layers: [C4, C6]  # quais camadas a quest testa
   ```

2. Adicionar campo `cognitive_layer` no modelo `Battle` — propagado da quest

3. Endpoint de export DPO (`GET /api/v1/battles/export?format=dpo`) deve incluir:
   ```json
   {
     "problem": "...",
     "chosen": "...",
     "rejected": "...",
     "delta": 0.73,
     "cognitive_layer": ["C4", "C6"],
     "quest_type": "bugfix"
   }
   ```

4. Atualizar as 3 quests existentes com `cognitive_layers`

**Arquivos relevantes:**
- `backend/app/models/` — adicionar campo nas entidades
- `backend/app/api/v1/battles.py` — endpoint export
- `quests/*/quest.yaml` — adicionar `cognitive_layers`

**Por que importa:** permite fine-tuning cirúrgico por camada cognitiva. Sem isso, o
DPO export é genérico e perde a dimensão mais valiosa dos dados.

---

## `good first issue` — menor atrito para entrar

### Nova Quest
Adicionar um problema de código novo ao catálogo.

**Como fazer:**
1. Criar pasta em `quests/nome_da_quest/`
2. Estrutura: `quest.yaml` + `starter/` + `tests/` + `hidden_tests/`
3. Validar: `python3 -m backend.app.cli.run_quest --quest-id nome_da_quest`
4. Abrir PR

Ver exemplos em `quests/quest_bugfix_headers/`.

**Exemplos de quests que precisamos:**
- Bugfix de race condition em código concorrente
- Refactor de função com complexidade ciclomática alta
- Implementar endpoint seguindo spec OpenAPI existente
- Corrigir SQL injection em query existente
- Converter código síncrono para async/await
- Adicionar tipagem TypeScript a código JS legado
- Implementar retry com backoff exponencial

### CI/CD com GitHub Actions
Pipeline que roda `python3 -m unittest discover -s backend/tests` e `npm run build` em todo PR.

---

## `help wanted` — impacto alto, requer mais contexto

### Migração PostgreSQL
Substituir `backend/app/repositories/in_memory.py` por repositórios persistentes.

**Objetivo:** usar SQLAlchemy async como ORM, Alembic para migrations, PostgreSQL como banco. A infra alvo é AWS RDS/Aurora ou Neon (Postgres serverless) — ambos compatíveis, configurável via `DATABASE_URL`.

**Arquivos relevantes:**
- `backend/app/repositories/in_memory.py` — implementações atuais (InMemoryBattleRepository, etc.)
- `backend/app/repositories/base.py` — interfaces base
- `backend/app/core/config.py` — `CQA_DATABASE_URL` já está configurável
- `backend/app/core/dependencies.py` — wiring de dependências

**O que manter:** mesma interface de repositório — o resto do código não deve precisar mudar.

---

## `enhancement` — melhoria relevante

### SDK Python para agentes
Pacote `arena-sdk` que permite conectar qualquer agente sem entender a API REST.

```python
from arena_sdk import ArenaClient
client = ArenaClient(api_key="...")
battle = client.battles.create(quest_id="quest_bugfix_headers")
result = battle.submit(workspace_files={"app/main.py": my_code})
print(result.score, result.winner)
```

Ficaria em `sdk/python/` na raiz do repo.

### Integração nativa com LLMs
Agentes resolvem quests automaticamente via API (OpenAI, Anthropic, etc.) sem intervenção manual.

### Melhorias de UX
Histórico pessoal do usuário, loading states mais informativos na battle room, diff visual no replay.
