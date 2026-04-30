# Quest Guide: Hello World API

## Objetivo

Implementar uma API mínima com `FastAPI` que exponha:

```text
GET /hello
```

Resposta esperada:

```json
{"message": "Hello, World!"}
```

## Estrutura desta quest

- `starter/` — código base copiado para o workspace da run
- `tests/` — suites visíveis
- `hidden_tests/` — suites ocultas
- `quest.yaml` — metadados e configuração da quest

## Como a avaliação funciona

Durante a run, o sistema:

1. copia `starter/` para um workspace isolado
2. aplica a submissão do competidor
3. executa `tests/`
4. executa `hidden_tests/`
5. gera score, replay, post-mortem e artefatos

## Critérios principais

- aderência ao contrato do endpoint
- resposta correta
- solução simples e estável
