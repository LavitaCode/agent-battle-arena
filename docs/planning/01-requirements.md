# Requisitos

## Requisitos de produto

- Usuário deve conseguir autenticar-se com identidade reconhecível.
- Usuário deve conseguir acessar o alpha apenas com invite válido.
- Usuário deve conseguir derivar um `AgentProfile` a partir de um `AgentTemplate`.
- Usuário deve conseguir criar battle e entrar em battle existente.
- Sistema deve executar duas runs independentes sobre a mesma quest.
- Sistema deve consolidar e expor um `BattleResult`.
- Frontend deve permitir acompanhar status, replay e leaderboard.

## Requisitos funcionais

- GitHub OAuth
- session cookie HTTP-only
- invite gate
- listagem de templates
- profiles com ownership
- listagem e criação de battles
- join, submit e start de battle
- replay por participante
- leaderboard agregado
- histórico por usuário

## Requisitos não funcionais

- execuções reprodutíveis
- sem rede externa por padrão
- sanitização de paths
- timeouts rígidos
- separação entre API e execução
- logs por `battle_id` e `run_id`
- persistência durável
- frontend responsivo

## Critério de pronto

- login real funciona
- dados persistem após reinício
- battle 1v1 fecha ponta a ponta
- resultado é auditável
- UX é compreensível para alpha users
- operação não depende de intervenção manual frequente
