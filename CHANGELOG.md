# Changelog

Todos os lançamentos notáveis deste projeto são documentados aqui.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/)
e o projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Added
- Estrutura inicial do repositório (baseline em `main`).
- Fundação da plataforma: configuração (`pydantic-settings`), logging estruturado,
  orquestrador (`BaseAgent`/`AgentRegistry`), runtime do Claude Agent SDK,
  CLI (`workg`), app FastAPI mínimo, tooling (ruff, mypy, pre-commit, CI) e docs base.
- Agent **Jira**: análise/triagem de issues via MCP Atlassian (backend `mcp`) e
  listagem via API REST (backend `rest`).
- Agent **Repo Analysis**: inventário e análise de saúde dos repositórios de
  serviços/projetos (stack, CI, testes, estado, riscos).
- Agent **Commit / PR / DevOps**: geração de mensagens Conventional Commits,
  descrições de PR e padrões/artefatos de DevOps.
- Módulo **RAG** + agent: ingestão de `.md`, embeddings configuráveis
  (sentence-transformers com fallback offline), vector store (Chroma ou
  in-memory) e Q&A com citação de fontes.

[Unreleased]: https://example.com/workg/compare/main...develop
