# WorkG como servidor MCP

O WorkG expõe cada agent como uma **tool MCP**, para ser usado de dentro do
**Claude Code**, **Cursor**, **Claude Desktop** e similares. Assim, durante uma
sessão de código você aciona os agents sem sair da ferramenta.

## Tools expostas

Uma tool por agent (nome `workg_<slug>`):

| Tool | Agent |
| --- | --- |
| `workg_jira` | análise/triagem de issues |
| `workg_repo_analysis` | inventário/saúde de repositórios |
| `workg_commit_pr_devops` | commits, PRs e DevOps |
| `workg_rag` | busca/Q&A na base de conhecimento |
| `workg_reports` | geração de relatórios |
| `workg_slides` | slides/infográficos + NotebookLM |

Cada tool aceita: `action` (string), `prompt` (instrução livre), `params`
(objeto chave→valor) e `dry_run` (bool). A descrição da tool lista as ações e
parâmetros de cada agent.

## Instalação

```bash
pip install -e ".[mcp]"      # ou ".[all]" para tudo
```

## Rodar o servidor

```bash
workg mcp                    # ou: python -m workg.mcp_server  (ou: workg-mcp)
```

Comunica por **stdio** (os logs vão para stderr para não interferir no protocolo).

## Adicionar ao Claude Code

Opção A — arquivo `.mcp.json` na raiz do projeto (veja `.mcp.json.example`):

```json
{
  "mcpServers": {
    "workg": {
      "command": "C:/caminho/para/workG/.venv/Scripts/python.exe",
      "args": ["-m", "workg.mcp_server"],
      "env": { "WORKG_ANTHROPIC_API_KEY": "sua-chave" }
    }
  }
}
```

Opção B — via CLI do Claude Code:

```bash
claude mcp add workg -- C:/caminho/para/workG/.venv/Scripts/python.exe -m workg.mcp_server
```

> Use o caminho do Python do **venv** do projeto (onde o WorkG está instalado),
> não o Python do sistema.

## Cursor / Claude Desktop

Mesmo formato de `mcpServers` no arquivo de configuração MCP da ferramenta
(ex.: `claude_desktop_config.json`). Aponte `command` para o Python do venv e
`args` para `["-m", "workg.mcp_server"]`.

## Exemplos de uso (dentro do Claude Code)

- "Use a tool workg_reports para gerar um relatório de status com este contexto: …"
- "Chame workg_rag com action=ask e q='como foi o rollback do serviço X'."
- "Rode workg_repo_analysis action=scan para ver a saúde dos repositórios."
