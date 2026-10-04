<div align="center">

# WorkG — Dev Workflow Copilot

**Plataforma de agents, skills e scripts orquestrados para acelerar o trabalho de engenharia.**

Jira · Análise de repositórios · Padrões de commit/PR/DevOps · Relatórios · Slides & infográficos · RAG sobre a base de conhecimento

</div>

---

## O que é

WorkG é uma plataforma modular que reúne vários **agents** especializados (baseados no **Claude Agent SDK**), **skills** reutilizáveis e **scripts**, orquestrados por uma **interface web (FastAPI + dashboard)**. O objetivo é centralizar e automatizar as tarefas recorrentes do dia a dia de engenharia.

### Agents / módulos

| Módulo | Papel |
| --- | --- |
| **Jira** | Analisar e controlar tasks no Jira (via MCP Atlassian): status, backlog, triagem, resumos. |
| **Repo Analysis** | Varrer e analisar os diversos repositórios de serviços/projetos: saúde, dependências, convenções, débitos. |
| **Commit / PR / DevOps** | Gerar bons padrões de commit (Conventional Commits), descrições de PR e práticas de DevOps/CI. |
| **Reports** | Montar relatórios (status, sprint, incidentes) a partir de dados do Jira, dos repos e do RAG. |
| **Slides & Infographics** | Conectar ao NotebookLM para gerar slides e infográficos a partir dos relatórios/base. |
| **RAG** | Busca semântica sobre a base de documentos e `.md` gerados de outros chamados e projetos. |

Tudo é exposto por um **dashboard web** e por uma **API** que orquestra os agents.

## Arquitetura (visão rápida)

```
┌──────────────────────────────────────────────────────────┐
│                  Web Dashboard + API (FastAPI)            │
└───────────────┬──────────────────────────────────────────┘
                │
        ┌───────▼────────┐      registry + runtime
        │  Orchestrator  │  ── Claude Agent SDK ──┐
        └───────┬────────┘                        │
   ┌────────────┼───────────────┬──────────┬──────┴──────┐
┌──▼──┐   ┌─────▼─────┐   ┌──────▼─────┐ ┌──▼────┐  ┌─────▼─────┐
│Jira │   │Repo Anal. │   │Commit/PR/  │ │Reports│  │Slides/    │
│agent│   │  agent    │   │DevOps agent│ │ agent │  │Infographic│
└──┬──┘   └─────┬─────┘   └──────┬─────┘ └──┬────┘  └─────┬─────┘
   │            │                │          │             │
┌──▼────────────▼────────────────▼──────────▼─────────────▼──┐
│  Integrations: Jira (MCP) · Git repos · NotebookLM          │
│  RAG: embeddings (configurável) + vector store (Chroma)     │
└─────────────────────────────────────────────────────────────┘
```

Detalhes em [`docs/architecture.md`](docs/architecture.md).

## Começando

```bash
# 1. Criar e ativar o ambiente
python -m venv .venv
# Windows (PowerShell):  .venv\Scripts\Activate.ps1
# Linux/macOS:           source .venv/bin/activate

# 2. Instalar em modo editável (dev)
pip install -e ".[dev]"

# 3. Configurar variáveis
cp .env.example .env   # e preencha as chaves

# 4. Subir o dashboard
workg serve
# ou:  uvicorn workg.web.app:app --reload
```

Scripts de bootstrap prontos em [`scripts/`](scripts/) (`bootstrap.ps1` / `bootstrap.sh`).

## Fluxo de desenvolvimento (Git Flow)

- `main` — produção, sempre estável, com tags de release.
- `develop` — integração contínua das features.
- `feature/*` — uma funcionalidade por branch, PR para `develop`.
- `release/*` — estabilização, bump de versão e CHANGELOG, PR para `main` + tag.
- `hotfix/*` — correção urgente a partir de `main`.

Versionamento **SemVer**, histórico em [`CHANGELOG.md`](CHANGELOG.md). Guia completo em [`docs/gitflow.md`](docs/gitflow.md) e helper em [`scripts/new_feature.sh`](scripts/new_feature.sh).

## Estrutura

```
src/workg/        código da plataforma (orchestrator, agents, rag, integrations, web)
knowledge_base/   documentos .md que alimentam o RAG
docs/             arquitetura, git flow e docs por agent
scripts/          bootstrap e helpers de git flow
tests/            testes (pytest)
```

## Licença

[MIT](LICENSE).
