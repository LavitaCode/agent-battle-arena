#!/bin/bash
set -e

# This script creates an example quest to illustrate how quests are defined
# in the Agent Battle Arena project. It then invokes the documentation setup.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Setting up quests skeleton..."

# Example quest specification in YAML
cat <<'QUEST_YAML' > "$ROOT_DIR/quests/quest_hello_world/quest.yaml"
name: Hello World API
description: |
  Construir uma API REST simples que retorna "Hello, World!" em JSON.
requirements:
  - Expor o endpoint GET `/hello` que responde com `{"message": "Hello, World!"}`.
  - Utilizar o framework FastAPI.
  - Escrever um arquivo README com instruções de execução e teste.
tests:
  - description: "GET /hello should return status 200"
    type: http
    request:
      method: GET
      path: /hello
    expected_response:
      status_code: 200
      json:
        message: "Hello, World!"
  - description: "Resposta deve ter o cabeçalho Content-Type correto"
    type: header
    request:
      method: GET
      path: /hello
    expected_headers:
      Content-Type: "application/json"
QUEST_YAML

# Example README for the quest
cat <<'QUEST_README' > "$ROOT_DIR/quests/quest_hello_world/quest-guide.md"
# Quest: Hello World API

Esta é uma quest de exemplo para o projeto Agent Battle Arena. O objetivo é
implementar um serviço mínimo com FastAPI.

## Objetivo

Crie uma API REST que exponha o endpoint `GET /hello` e retorne:

```json
{"message": "Hello, World!"}
```

## Como começar

1. Navegue até o diretório `backend`.
2. Instale as dependências (por exemplo, com `pip install fastapi uvicorn`).
3. Execute a aplicação com o comando:

   ```bash
   uvicorn app.main:app --reload
   ```

4. Visite `http://localhost:8000/api/v1/hello` para ver a resposta.

## Avaliação

Além dos testes descritos em `quest.yaml`, os avaliadores (IA e humanos) irão
considerar a clareza da sua solução, a utilização adequada do framework e a
organização do código.
QUEST_README

echo "Quests skeleton created."

# Proceed to documentation setup
bash "$SCRIPT_DIR/05_setup_docs.sh"
