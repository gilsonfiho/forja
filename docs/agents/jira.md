# Agent: Jira

Analisa e ajuda a controlar tasks no Jira.

## Backends

| Backend (`FORJA_JIRA_BACKEND`) | Como funciona |
| --- | --- |
| `mcp` (padrão) | Claude Agent SDK + **Atlassian Remote MCP Server**. O LLM usa as tools do Atlassian para buscar/ler/transicionar issues. |
| `rest` | API REST do Jira Cloud (`atlassian-python-api`) para listagem crua; o LLM resume. |

## Ações

- `analyze` (default): resume e faz triagem de uma JQL (visão geral, itens em risco, próximas ações).
- `list`: lista issues cruas (apenas backend `rest`).

## Parâmetros

- `jql`: consulta JQL. Padrão: issues abertas do usuário atual.
- `prompt`: contexto livre adicional.
- `dry_run`: não executa, apenas descreve o plano.

## Exemplos

```bash
forja run jira --action analyze -p "jql=project = ABC AND sprint in openSprints()"
forja run jira --action analyze --prompt "foque em risco de prazo da sprint"
```

## Segurança

O agent nunca altera issues a menos que explicitamente solicitado; `dry_run`
bloqueia qualquer efeito colateral.
