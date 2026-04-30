# Sprint 6 — Worker e Operação

## Status

Concluída.

## Objetivo

Separar execução da API e endurecer o fluxo operacional.

## Entregas

- worker simples
- fila básica
- estados intermediários confiáveis
- retry controlado
- logs estruturados

## Critério de aceite

- API não executa battle diretamente e o estado continua consistente

## Progresso

- Implementado: `InProcessBattleWorker` com fila FIFO simples.
- Implementado: `start_battle` agora marca a battle como `queued` e enfileira job.
- Implementado: worker daemon processa jobs fora do endpoint HTTP.
- Implementado: retry controlado por `max_attempts`.
- Implementado: logs estruturados por evento de job.
- Implementado: proteção contra enfileirar a mesma battle fora do estado `ready`.
