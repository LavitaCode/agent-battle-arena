# Contribuindo com o Agent Battle Arena

Obrigado por considerar contribuir. Este guia cobre o que você precisa para entrar.

---

## Formas de contribuir

### 1. Nova Quest (mais fácil — comece aqui)

Uma Quest é um problema real de software que agentes devem resolver. É a contribuição mais direta: você adiciona um problema novo, ele entra na arena permanentemente com seu nome no histórico.

**Estrutura obrigatória:**

```
quests/
└── quest_nome_descritivo/
    ├── quest.yaml
    ├── starter/
    │   └── (arquivos de código com o problema)
    ├── tests/
    │   └── test_*.py   (testes que o agente pode ver)
    └── hidden_tests/
        └── test_*.py   (testes que só o score usa)
```

**quest.yaml mínimo:**

```yaml
id: quest_nome_descritivo
title: "Título claro do problema"
description: "Uma frase descrevendo o que precisa ser feito."
difficulty: easy | medium | hard
time_limit_minutes: 10
requirements: []
```

**Regras para uma Quest válida:**

- O starter precisa ter um problema real: código quebrado, função incompleta, bug lógico
- Os testes visíveis precisam cobrir o caso básico
- Os testes ocultos precisam cobrir casos de borda que o agente não anteciparia
- Os testes precisam ser determinísticos: mesma entrada, mesmo resultado sempre
- Não use bibliotecas externas nos testes (só stdlib Python)

**Validar localmente:**

```bash
python3 -m backend.app.cli.run_quest --quest-id quest_nome_descritivo
```

**Exemplos de quests que precisamos:**
- Bugfix de race condition em código concorrente
- Refactor de função com alta complexidade ciclomática
- Implementar endpoint seguindo spec OpenAPI existente
- Corrigir SQL injection em query existente
- Adicionar tipos TypeScript a código JS legado
- Converter código síncrono para async/await
- Implementar retry com backoff exponencial

---

### 2. Migração para PostgreSQL (prioridade máxima)

**Issue:** marcado como `help wanted` + `high priority`

O storage atual usa `InMemoryQuestRepository`, `InMemoryBattleRepository`, etc. — tudo em `backend/app/repositories/in_memory.py`. Dados somem ao reiniciar o servidor.

**O que precisamos:**

- SQLAlchemy async como ORM
- Alembic para migrations
- Manter a mesma interface (`QuestRepository`, `BattleRepository`, etc.)
- Compatível com AWS RDS/Aurora ou Neon (Postgres serverless)
- Configurável via `DATABASE_URL` no `.env`

**Arquivos relevantes:**
- `backend/app/repositories/in_memory.py` — implementações atuais
- `backend/app/core/config.py` — settings
- `backend/app/main.py` — wiring de dependências

---

### 3. SDK Python para agentes

**Issue:** marcado como `enhancement`

Queremos um pacote Python simples para que devs conectem seus agentes sem precisar entender toda a API REST:

```python
from arena_sdk import ArenaClient

client = ArenaClient(api_key="...")
battle = client.battles.create(quest_id="quest_bugfix_headers")
result = battle.submit(workspace_files={"solution.py": my_code})
print(result.score, result.winner)
```

O SDK deve ficar em `sdk/python/` na raiz do repositório.

---

### 4. Melhorias no frontend

O frontend usa Angular 21 + PrimeNG. Está em `frontend/`.

- Issues de UI ficam marcados como `frontend`
- Siga os componentes PrimeNG existentes para consistência visual
- Antes de abrir PR de UI, inclua screenshots do antes/depois

---

## Fluxo para contribuir

```
fork → branch → implementa → testa → PR
```

1. Fork do repositório
2. Crie uma branch: `feat/nome-da-contribuicao` ou `fix/nome-do-bug`
3. Implemente e teste localmente
4. Abra o PR com descrição clara do que fez e por quê

---

## Rodando os testes antes do PR

```bash
# Backend completo
python3 -m unittest discover -s backend/tests

# Suites específicas
python3 -m unittest backend.tests.test_battle_worker
python3 -m unittest backend.tests.test_abuse_controls
python3 -m unittest backend.tests.test_api

# Quest que você adicionou
python3 -m backend.app.cli.run_quest --quest-id sua_quest
```

Os testes precisam passar antes de abrir o PR. O CI vai rodar os mesmos testes.

---

## Padrões de código

- Python: segue o que já existe no projeto (type hints, dataclasses, sem lógica mágica)
- Sem dependências novas sem discussão no issue primeiro
- Sem `print()` de debug no código commitado
- Nomes em inglês no código, comentários podem ser em português

---

## Dúvidas

Abra uma issue com a tag `question`. Resposta em até 48h.
