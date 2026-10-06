# Forja como servidor MCP

O Forja expõe cada agent como uma **tool MCP**, para ser usado de dentro do
**Claude Code**, **Cursor**, **Claude Desktop** e similares. Assim, durante uma
sessão de código você aciona os agents sem sair da ferramenta.

## Tools expostas

Uma tool por agent (nome `forja_<slug>`):

| Tool | Agent |
| --- | --- |
| `forja_jira` | análise/triagem de issues |
| `forja_repo_analysis` | inventário/saúde de repositórios |
| `forja_commit_pr_devops` | commits, PRs e DevOps |
| `forja_rag` | busca/Q&A na base de conhecimento |
| `forja_reports` | geração de relatórios |
| `forja_slides` | slides/infográficos + NotebookLM |

Cada tool aceita: `action` (string), `prompt` (instrução livre), `params`
(objeto chave→valor) e `dry_run` (bool). A descrição da tool lista as ações e
parâmetros de cada agent.

## Instalação

```bash
pip install -e ".[mcp]"      # ou ".[all]" para tudo
```

## Rodar o servidor

```bash
forja mcp                    # ou: python -m forja.mcp_server  (ou: forja-mcp)
```

Comunica por **stdio** (os logs vão para stderr para não interferir no protocolo).

## Adicionar ao Claude Code

Opção A — arquivo `.mcp.json` na raiz do projeto (veja `.mcp.json.example`):

```json
{
  "mcpServers": {
    "forja": {
      "command": "C:/caminho/para/forja/.venv/Scripts/python.exe",
      "args": ["-m", "forja.mcp_server"],
      "env": { "FORJA_ANTHROPIC_API_KEY": "sua-chave" }
    }
  }
}
```

Opção B — via CLI do Claude Code:

```bash
claude mcp add forja -- C:/caminho/para/forja/.venv/Scripts/python.exe -m forja.mcp_server
```

> Use o caminho do Python do **venv** do projeto (onde o Forja está instalado),
> não o Python do sistema.

## Cursor / Claude Desktop

Mesmo formato de `mcpServers` no arquivo de configuração MCP da ferramenta
(ex.: `claude_desktop_config.json`). Aponte `command` para o Python do venv e
`args` para `["-m", "forja.mcp_server"]`.

## Exemplos de uso (dentro do Claude Code)

- "Use a tool forja_reports para gerar um relatório de status com este contexto: …"
- "Chame forja_rag com action=ask e q='como foi o rollback do serviço X'."
- "Rode forja_repo_analysis action=scan para ver a saúde dos repositórios."
