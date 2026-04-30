# Plano de Entrega

## Objetivo

Transformar o vertical slice atual em um MVP público viável, operável e
demonstrável para um grupo controlado de usuários.

## Estratégia

### Etapa 1

Trocar camadas locais e mockadas por equivalentes reais:

- OAuth real
- PostgreSQL
- sessão estável

### Etapa 2

Separar execução da requisição HTTP:

- worker simples
- fila básica
- estados de battle confiáveis

### Etapa 3

Fechar UX de alpha:

- dashboard melhor
- lobby/battle room mais claros
- leaderboard e histórico
- mensagens de erro e loading

### Etapa 4

Fechar operação:

- conteúdo oficial
- logs
- limites de abuso
- smoke tests
- deploy controlado

## Critérios de aceite do plano

- dois usuários reais conseguem batalhar
- login real funciona
- dados persistem
- battle não depende de intervenção manual
- resultado é confiável
