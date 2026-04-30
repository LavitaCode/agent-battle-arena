# Sprint 5 — Auth Real e Persistência

## Status

Concluída.

## Objetivo

Trocar camadas locais e mockadas por equivalentes prontos para operação real.

## Entregas

- GitHub OAuth real configurável por ambiente
- modo local leve com mock auth preservado
- sessão estável persistida no store local
- seed formal de templates/invite
- preparação de variáveis para Neon/PostgreSQL
- migração do store atual para adapter Postgres

## Critério de aceite

- login local continua funcionando sem GitHub externo
- start OAuth gera URL real do GitHub quando mock auth está desligado
- callback OAuth exige `code` real antes de criar sessão
- dados de sessão/profile persistem após recriar services/cache
- deploy alpha tem `.env.example` com variáveis de OAuth/storage

## Progresso

- Implementado: configuração OAuth GitHub por ambiente.
- Implementado: resposta de start auth com URL externa real quando `CQA_ENABLE_MOCK_GITHUB_AUTH=false`.
- Implementado: callback com resolução de login via GitHub OAuth code.
- Implementado: uso de invite sem acesso direto a métodos privados do store.
- Implementado: teste de persistência de sessão/profile após reset de services.
- Implementado: adapter inicial PostgreSQL/Neon selecionado por `CQA_DATABASE_URL`.
- Implementado: comando `python3 -m backend.app.cli.check_alpha_storage`.
- Validado: Neon inicializa como `storage=postgres`, com 4 templates e invite ativo.
- Validado: testes de alpha passaram contra PostgreSQL/Neon.
- Implementado: migrations versionadas formais com `schema_migrations`.
- Implementado: comando de storage exibe `schema_version`.
