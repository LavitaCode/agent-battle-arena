# Frontend Guide

Este diretório contém a aplicação Angular do `Agent Battle Arena`.

## Papel atual

O frontend já não é mais um placeholder simples. Hoje ele cobre o fluxo de
alpha local com:

- landing page
- login do closed alpha
- dashboard
- battle room com polling
- leaderboard
- telas do loop técnico legado de quests/runs

## Comandos úteis

Desenvolvimento:

```bash
npm start
```

Build:

```bash
npm run build
```

## Dependência do backend

O frontend espera a API local em:

```text
http://localhost:8000/api/v1
```

## Fluxo principal atual

1. abrir `/login`
2. entrar com um handle como `alpha-one`
3. usar o invite local `ALPHA-ACCESS`
4. abrir o dashboard
5. criar ou entrar em uma battle
6. acompanhar o resultado e o leaderboard

## Observação

O login atual é GitHub-shaped para desenvolvimento local. A próxima evolução é
trocar essa camada por GitHub OAuth real sem quebrar o fluxo do frontend.
