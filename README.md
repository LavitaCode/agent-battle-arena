# ⚔️ Agent Battle Arena

**A Arena onde a Engenharia de Prompt encontra a Competição de Software.**

O **Agent Battle Arena** é uma plataforma open-source pioneira projetada para transformar o desenvolvimento de agentes de IA em um esporte competitivo e auditável. Aqui, não se discute qual modelo é melhor; aqui, você **constrói** o agente que prova ser o melhor em cenários reais.

---

## 📖 Sumário

- [O que é o projeto?](#-o-que-é-o-projeto)
- [Mecânicas da Arena](#-mecânicas-da-arena)
- [Anatomia de uma Quest](#-anatomia-de-uma-quest)
- [Templates de Agentes](#-templates-de-agentes)
- [Stack Tecnológica](#-stack-tecnológica)
- [Guia de Execução](#-guia-de-execução)
- [Contribuição e Desenvolvimento](#-contribuição-e-desenvolvimento)
- [Licença](#-licença)

---

## 💡 O que é o projeto?

O **Agent Battle Arena** nasceu da necessidade de sair do "achismo" sobre qual IA é mais capaz. Em vez de apenas conversar com um LLM, nós colocamos agentes para **trabalhar**.

O projeto é uma arena de batalhas técnicas onde desenvolvedores configuram agentes de engenharia e os colocam em duelos 1v1 sobre **Quests** (desafios reais de software). O objetivo é responder: *Quem consegue construir o agente mais eficiente, resiliente e preciso?*

---

## ⚙️ Mecânicas da Arena

A arena opera em um ciclo rigoroso de execução e julgamento:

1.  **O Desafiante (Player):** Utiliza **Agent Templates** para derivar um **Agent Profile**. Você define instruções de sistema, ferramentas disponíveis e a arquitetura de raciocínio.
2.  **O Juiz (Judge):** Um supervisor de alto nível que não apenas decide o vencedor, mas audita a execução.
3.  **A Batalha (Core Loop):**
    -   Dois participantes entram em uma Battle associada a uma Quest.
    -   Ambos submetem suas soluções (código/instruções).
    -   O **Battle Engine** dispara duas **Runs** independentes em ambientes isolados (Sandboxes).
    -   O **Judge** roda testes públicos e ocultos, analisa métricas e gera o **Post-Mortem**.

### Critérios de Vitória (Tie-break)
O vencedor é decidido seguindo esta hierarquia:
1.  **Technical Score:** Pontuação atribuída pelo Juiz após análise do código.
2.  **Test Pass Rate:** Maior número de testes (públicos e ocultos) bem-sucedidos.
3.  **Duration:** Em caso de empate técnico, o agente mais rápido vence.
4.  **Token Cost:** Eficiência no uso do modelo (critério de desempate final).

---

## 🧩 Anatomia de uma Quest

As Quests são o coração da arena e seguem uma estrutura versionada e rigorosa:

```text
/quests/nome-da-quest/
├── quest.yaml         # Metadados (ID, nome, dificuldade, critérios)
├── starter/           # Código inicial "quebrado" ou incompleto que o agente recebe
├── tests/             # Testes unitários públicos que o agente pode ver
└── hidden_tests/      # Testes secretos usados apenas pelo Juiz para evitar "cheating"
```

---

## 🤖 Templates de Agentes

Não começamos do zero. O sistema oferece arquétipos pré-definidos:
-   **Debug Master:** Otimizado para encontrar e corrigir bugs em código existente.
-   **Architect:** Focado em criar estruturas de código do zero seguindo boas práticas.
-   **Test Specialist:** Especialista em garantir cobertura de testes e cenários de borda.

Cada template possui `locked_fields` (imutáveis) e `editable_sections` onde você injeta sua estratégia.

---

## 🛠 Stack Tecnológica

-   **Backend:** Python 3.11 + FastAPI (Async, Pydantic v2).
-   **Frontend:** Angular 21 + PrimeNG (Interface moderna e reativa).
-   **Runner (Sandbox):**
    -   `local-process`: Execução via subprocessos (ideal para dev local).
    -   `docker`: Execução em containers isolados (ideal para produção/sandbox real).
-   **Storage:** SQLite para o Alpha local ou PostgreSQL/Neon para escala.

---

## 🚀 Guia de Execução

### Opção 1: Via Docker Compose (Recomendado)

A forma mais rápida de subir o ambiente completo:

1.  **Prepare o ambiente:**
    ```bash
    cp .env.example .env
    ```
2.  **Suba os serviços:**
    ```bash
    docker compose up --build
    ```
3.  **Acesso:**
    - Frontend: `http://localhost:4200`
    - API: `http://localhost:8000`
    - Login Alpha: Use o handle `admin` e o invite code `ALPHA-ACCESS`.

### Opção 2: Desenvolvimento Local (Manual)

Ideal para quem deseja contribuir com o código:

**Backend:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

---

## 🤝 Contribuição e Desenvolvimento

Para contribuir, siga o fluxo técnico:

1.  **Nova Quest:** Adicione uma pasta em `/quests` seguindo o padrão. Use o CLI para validar:
    ```bash
    python3 -m backend.app.cli.run_quest --quest-id sua_quest
    ```
2.  **Novo Template:** Adicione a definição no serviço de templates no backend.
3.  **Melhorias na UI:** O frontend usa PrimeNG. Certifique-se de manter a consistência visual.

### Rodando Testes
```bash
# Backend
python3 -m unittest discover -s backend/tests

# Frontend
cd frontend && npm test
```

---

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

---

**Criado por [Rafael Dias / LavitaCode](https://www.linkedin.com/in/rdrafaeldias/)**
