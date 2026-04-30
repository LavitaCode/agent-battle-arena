#!/bin/bash
set -e

# This script creates basic documentation files for the project.

echo "Setting up documentation skeleton..."

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Main documentation for the project
cat <<'DOCS_README' > "$ROOT_DIR/docs/README.md"
# Agent Battle Arena - MVP Esqueleto

Este diretório contém a documentação inicial para o MVP do projeto **Claude
Quest Arena**. O objetivo deste projeto open source é criar uma arena de
desafios de código supervisionada pela IA Claude, onde desenvolvedores podem
demonstrar habilidades técnicas em pequenos micro‑hackathons.

## Visão Geral

O MVP é dividido em quatro componentes principais:

1. **Backend**: Uma API construída com FastAPI que orquestra quests, recebe
   submissões de código, interage com a IA Claude para avaliar soluções e
   disponibiliza informações para a interface web.
2. **Frontend**: Uma aplicação Angular (a ser expandida) que apresenta a
   interface do usuário para acompanhar desafios, enviar soluções e ver
   rankings.
3. **Quests**: Desafios técnicos versionados em arquivos YAML, contendo
   descrições, requisitos e casos de teste automatizados.
4. **Documentação**: Arquivos explicativos sobre a arquitetura, como usar e
   contribuir para o projeto.

## Arquitetura

- **FastAPI Backend**: O backend foi estruturado seguindo princípios de
  arquitetura limpa, com separação entre modelos, repositórios, serviços e
  endpoints. A API está versionada (ex.: `/api/v1`). O padrão de
  repositório abstrai o mecanismo de armazenamento (`repositories/base.py`),
  permitindo trocar o backend facilmente (por exemplo, usar um banco de dados
  no lugar da implementação em memória de `repositories/in_memory.py`). O
  serviço (`services/quest_service.py`) encapsula as regras de negócio e
  expõe métodos para listar e criar quests. Dependências são injetadas
  usando as funções de `core/dependencies.py`, garantindo testabilidade e
  aderência ao princípio de inversão de dependência (SOLID).
    - **Angular Frontend**: O diretório `frontend/src` contém uma estrutura
      compatível com Angular 21 utilizando componentes standalone. O arquivo
      `main.ts` realiza o `bootstrapApplication` configurando o provedor
      `provideHttpClient()` em vez de usar módulos. O componente raiz e o
      componente `quest-list` são standalone e importam outros componentes ou
      módulos de forma declarativa através da propriedade `imports`. Um
      serviço Angular (`quest.service.ts`) gerencia a comunicação com o
      backend e um modelo (`quest.ts`) define a interface dos dados. Essa
      estrutura demonstra a separação de responsabilidades e a adoção das
      novidades do Angular 21.
- **Quests**: Os desafios ficam no diretório `quests/`. Cada subpasta
  representa uma nova quest com um arquivo `quest.yaml` contendo
  especificações, requisitos e casos de teste automatizados, além de um
  `README.md` com instruções.
- **Testes Automatizados**: Os testes descritos em cada `quest.yaml` servem
  como critérios de avaliação objetivos. A IA Claude e a comunidade podem
  complementar com uma avaliação subjetiva de criatividade e estilo.

## Próximos Passos

1. Implementar as rotas REST completas para submissões de quests e ranking.
2. Substituir o stub Angular por um projeto gerado via `ng new`.
3. Integrar um mecanismo de sandbox (como Judge0) para executar código de
   forma segura e automatizar os testes.
4. Estender o esquema de quests e criar um _pipeline_ de avaliação com
   feedback do Claude.
5. Documentar o processo de contribuição e abrir o repositório para a
   comunidade.

DOCS_README

cat <<'ROOT_README' > "$ROOT_DIR/README.md"
# Agent Battle Arena - MVP

Bem‑vindo ao esqueleto do projeto **Agent Battle Arena**. Este repositório
fornece uma base evoluída para começar a desenvolver uma plataforma onde a IA
Claude orquestra desafios de programação para desenvolvedores.

## Conteúdo

- **backend/** — Código fonte do backend em FastAPI com uma estrutura
  desacoplada em modelos, repositórios, serviços e endpoints, seguindo
  princípios SOLID e padrões de projeto como o *Repository Pattern*.
- **frontend/** — Estrutura base para a aplicação Angular 21 com modelos,
  serviços e componentes **standalone**. O frontend inclui um serviço e um
  componente que consomem a API de quests via HTTP.
- **quests/** — Exemplos de quests definidas em YAML e seus testes.
- **docs/** — Documentação do projeto.
- **project_setup/** — Scripts utilizados para gerar este esqueleto.

## Como iniciar

Para criar toda a estrutura a partir do zero, execute o script `run_all.sh`
presente no diretório `project_setup/`:

```bash
cd project_setup
chmod +x run_all.sh
./run_all.sh
```

Isso criará todas as pastas e arquivos necessários para começar a trabalhar
no MVP.

## Objetivo

O objetivo deste MVP é permitir que qualquer pessoa contribua para a criação
de quests, avaliação de soluções e expansão da arena. Mais detalhes sobre
arquitetura e próximos passos estão disponíveis em `docs/README.md`.

ROOT_README

echo "Documentation skeleton created."