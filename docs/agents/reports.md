# Agent: Reports

Monta relatórios em Markdown a partir de múltiplas fontes (contexto livre,
inventário de repositórios e base de conhecimento via RAG).

## Ação

- `generate` (default): gera e salva um relatório Markdown em `output/reports/`.

## Parâmetros

- `type`: `status` (default), `sprint`, `incident` ou `custom`.
- `title`: título do relatório.
- `include`: fontes extras separadas por vírgula (ex.: `repos`).
- `kb_query`: consulta para puxar contexto do RAG.
- `root`: raiz dos repositórios (para `include=repos`).
- `output_dir`: diretório de saída (default `output/reports`).

## Exemplos

```bash
workg run reports --action generate -p type=status -p title="Status Semanal" \
  -p include=repos -p kb_query="incidentes recentes do serviço X"
```

Sem LLM disponível, gera um relatório estruturado determinístico com as seções coletadas.
