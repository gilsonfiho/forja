# Changelog

Todos os lançamentos notáveis deste projeto são documentados aqui.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/)
e o projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

Cada **feature** entrega uma versão `MINOR` própria (com tag na sua merge em
`develop`); a estabilização para produção acontece em uma `release/*` com merge
e tag em `main`.

## [Unreleased]

## [2.0.0] - 2026-10-05
Primeira release pública como **Forja**. Consolida em `main` tudo desde a
`1.0.0`: saída rica no dashboard (`1.1.0`), servidor MCP (`1.2.0`) e o rename
do projeto para Forja (`1.3.0`).

### Changed
- **BREAKING:** identidade do projeto passou a ser **Forja** — pacote `forja`,
  CLI `forja`/`forja-mcp`, tools MCP `forja_*`, prefixo de ambiente `FORJA_`.

## [1.3.0] - 2026-10-05
### Changed
- **Projeto renomeado para Forja** (antes "WorkG"). Mudança de identidade que
  afeta: pacote Python (`forja`), CLI (`forja` / `forja-mcp`), tools MCP
  (`forja_jira`, …), prefixo de variáveis de ambiente (`FORJA_`), além de docs,
  README e exemplos. O histórico (`git mv`) foi preservado.

> Nota: o nome `forja` já existe no PyPI (projeto não relacionado). Para o
> GitHub não há conflito; caso publique no PyPI no futuro, use um nome de
> distribuição alternativo (ex.: `forja-dev`).

## [1.2.0] - 2026-10-04
### Added
- **Servidor MCP** (`forja mcp` / `python -m forja.mcp_server` / `forja-mcp`):
  expõe cada agent como uma tool MCP (`forja_jira`, `forja_rag`, `forja_reports`,
  …) para uso dentro do **Claude Code**, Cursor e Claude Desktop.
- Formatação de resultado específica para LLM e descrição de tool com as ações/
  parâmetros de cada agent; exemplo de config em `.mcp.json.example` e guia em
  `docs/mcp.md`.
- Extra `mcp` e console script `forja-mcp`.

### Changed
- `configure_logging` aceita `stream`; no modo MCP os logs vão para **stderr**
  (stdout é reservado ao protocolo).
- README reposiciona o Forja como ferramenta auxiliar ao Claude Code (MCP como
  superfície principal; dashboard como cockpit opcional).

## [1.1.0] - 2026-10-04
### Added
- **Saída rica no dashboard**: resultado renderizado em Markdown com syntax
  highlighting, tabelas para dados estruturados, abas (Resultado/Artefatos/
  Dados/JSON), chip de status e tempo de execução.
- **Preview de artefatos**: endpoint `GET /api/artifact` (sandbox nas pastas de
  saída) e pré-visualização inline dos arquivos gerados.
- **Formulário dinâmico por agent**: ações e parâmetros declarados em
  `AgentSpec.actions` dirigem os campos da UI; ícone por agent.

## [1.0.0] - 2026-10-04
Primeira release de produção. Consolida as features `0.1.0`–`0.8.0` em `main`:
plataforma de agents (Jira, Repo Analysis, Commit/PR/DevOps, RAG, Reports,
Slides & Infographics), orquestrador com Claude Agent SDK e dashboard web.

## [0.8.0] - 2026-10-04
### Added
- **Web dashboard**: interface FastAPI (API + UI) que lista e executa os agents,
  com console de resultados, páginas Jinja2 e estáticos (CSS/JS).

## [0.7.0] - 2026-10-04
### Added
- Agent **Slides & Infographics**: outlines de slides, specs de infográfico e
  preparação do pacote de fontes para o NotebookLM.

## [0.6.0] - 2026-10-04
### Added
- Agent **Reports**: gera relatórios Markdown (status/sprint/incidente)
  combinando contexto livre, inventário de repos e RAG.

## [0.5.0] - 2026-10-04
### Added
- Módulo **RAG** + agent: ingestão de `.md`, embeddings configuráveis
  (sentence-transformers com fallback offline), vector store (Chroma ou
  in-memory) e Q&A com citação de fontes.

## [0.4.0] - 2026-10-04
### Added
- Agent **Commit / PR / DevOps**: geração de mensagens Conventional Commits,
  descrições de PR e padrões/artefatos de DevOps.

## [0.3.0] - 2026-10-04
### Added
- Agent **Repo Analysis**: inventário e análise de saúde dos repositórios de
  serviços/projetos (stack, CI, testes, estado, riscos).

## [0.2.0] - 2026-10-04
### Added
- Agent **Jira**: análise/triagem de issues via MCP Atlassian (backend `mcp`) e
  listagem via API REST (backend `rest`).

## [0.1.0] - 2026-10-04
### Added
- Estrutura inicial do repositório (baseline em `main`).
- Fundação da plataforma: configuração (`pydantic-settings`), logging estruturado,
  orquestrador (`BaseAgent`/`AgentRegistry`), runtime do Claude Agent SDK,
  CLI (`forja`), app FastAPI mínimo, tooling (ruff, mypy, pre-commit, CI) e docs base.

[Unreleased]: https://github.com/gilsonfiho/forja/compare/v2.0.0...develop
[2.0.0]: https://github.com/gilsonfiho/forja/compare/v1.3.0...v2.0.0
[1.3.0]: https://github.com/gilsonfiho/forja/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/gilsonfiho/forja/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/gilsonfiho/forja/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/gilsonfiho/forja/compare/v0.8.0...v1.0.0
[0.8.0]: https://github.com/gilsonfiho/forja/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/gilsonfiho/forja/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/gilsonfiho/forja/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/gilsonfiho/forja/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/gilsonfiho/forja/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/gilsonfiho/forja/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/gilsonfiho/forja/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/gilsonfiho/forja/releases/tag/v0.1.0
