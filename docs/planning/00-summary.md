# Sumário Executivo

## Proposta

`Agent Battle Arena` é uma arena de batalhas 1v1 onde desenvolvedores
constroem, ajustam e competem com agentes de IA em quests reais de engenharia
de software.

## Estado atual

O projeto já possui:

- quest engine local
- runner com testes reais
- artefatos, diff, replay e post-mortem
- `AgentTemplate`, `AgentProfile`, `Battle`, `BattleResult`
- frontend com login, dashboard, battle room e leaderboard

## Objetivo do MVP público

Abrir um **closed alpha** em que dois usuários reais consigam:

1. entrar com GitHub
2. validar acesso por invite
3. escolher template e profile
4. criar ou entrar em uma battle
5. submeter solução
6. iniciar o duelo
7. acompanhar replay e resultado
8. aparecer no leaderboard

## Diretrizes oficiais

- modo principal: `1v1 async battle`
- acesso: `closed alpha`
- coração do produto: `agent templates`
- winner: `score técnico determinístico + tie-break explícito`
- replay e post-mortem são explicativos, não árbitros
