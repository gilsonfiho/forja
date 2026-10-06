# Arquitetura

## Camadas

1. **Web (FastAPI + dashboard)** — `forja.web`
   API REST + dashboard (HTMX/Jinja2) que exibem e disparam os agents.

2. **Orquestrador** — `forja.orchestrator`
   - `base.py`: contratos (`BaseAgent`, `AgentContext`, `AgentResult`, `AgentSpec`) e o `AgentRegistry`.
   - `runtime.py`: `ClaudeRuntime`, fachada sobre o **Claude Agent SDK** (degrada com erro claro se o extra `agents` não estiver instalado).

3. **Agents** — `forja.agents.*`
   Cada agent é um módulo com `build() -> BaseAgent` e um `AgentSpec`. São
   descobertos por `forja.agents.load_agents()` e registrados no registry global.

4. **Integrações** — `forja.integrations`
   Adaptadores para sistemas externos: Jira (MCP Atlassian), repositórios Git,
   NotebookLM.

5. **RAG** — `forja.rag`
   Pipeline de ingestão da base de conhecimento (`knowledge_base/*.md`),
   embeddings configuráveis e vector store (Chroma por padrão; pgvector opcional).

## Princípios

- **Degradação graciosa:** a plataforma sobe mesmo sem os extras (`agents`,
  `rag`, `integrations`) instalados; cada agent valida suas dependências ao rodar.
- **Contrato único de resultado:** todo agent devolve `AgentResult`
  (ok/summary/data/artifacts), consumido igualmente pela API, pelo dashboard e pelo CLI.
- **Configuração por ambiente:** `forja.config.Settings` (prefixo `FORJA_`, `.env`).
- **Sem acoplamento de UI:** agents não conhecem FastAPI; a web apenas invoca o registry.

## Fluxo de uma execução

```
HTTP/CLI -> registry.get(slug) -> agent.run(AgentContext)
        -> (opcional) ClaudeRuntime.run(...) via Claude Agent SDK
        -> integrações / RAG -> AgentResult -> resposta JSON / dashboard
```

## Diagrama de componentes

Ver o diagrama no [README](../README.md#arquitetura-visão-rápida).
