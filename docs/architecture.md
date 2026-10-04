# Arquitetura

## Camadas

1. **Web (FastAPI + dashboard)** — `workg.web`
   API REST + dashboard (HTMX/Jinja2) que exibem e disparam os agents.

2. **Orquestrador** — `workg.orchestrator`
   - `base.py`: contratos (`BaseAgent`, `AgentContext`, `AgentResult`, `AgentSpec`) e o `AgentRegistry`.
   - `runtime.py`: `ClaudeRuntime`, fachada sobre o **Claude Agent SDK** (degrada com erro claro se o extra `agents` não estiver instalado).

3. **Agents** — `workg.agents.*`
   Cada agent é um módulo com `build() -> BaseAgent` e um `AgentSpec`. São
   descobertos por `workg.agents.load_agents()` e registrados no registry global.

4. **Integrações** — `workg.integrations`
   Adaptadores para sistemas externos: Jira (MCP Atlassian), repositórios Git,
   NotebookLM.

5. **RAG** — `workg.rag`
   Pipeline de ingestão da base de conhecimento (`knowledge_base/*.md`),
   embeddings configuráveis e vector store (Chroma por padrão; pgvector opcional).

## Princípios

- **Degradação graciosa:** a plataforma sobe mesmo sem os extras (`agents`,
  `rag`, `integrations`) instalados; cada agent valida suas dependências ao rodar.
- **Contrato único de resultado:** todo agent devolve `AgentResult`
  (ok/summary/data/artifacts), consumido igualmente pela API, pelo dashboard e pelo CLI.
- **Configuração por ambiente:** `workg.config.Settings` (prefixo `WORKG_`, `.env`).
- **Sem acoplamento de UI:** agents não conhecem FastAPI; a web apenas invoca o registry.

## Fluxo de uma execução

```
HTTP/CLI -> registry.get(slug) -> agent.run(AgentContext)
        -> (opcional) ClaudeRuntime.run(...) via Claude Agent SDK
        -> integrações / RAG -> AgentResult -> resposta JSON / dashboard
```

## Diagrama de componentes

Ver o diagrama no [README](../README.md#arquitetura-visão-rápida).
