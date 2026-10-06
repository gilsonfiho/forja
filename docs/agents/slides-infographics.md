# Agent: Slides & Infographics

Gera outlines de apresentação e specs de infográfico, e prepara o pacote de
fontes para o **NotebookLM**.

## Ações

- `outline` (default): estrutura de slides (título + bullets, sugestões de visual).
- `infographic`: spec de infográfico (mensagem, blocos, métricas, visuais).
- `notebooklm`: consolida o conteúdo-fonte em um `.md` pronto para upload no
  NotebookLM e retorna instruções de geração.

## Fonte do conteúdo

Resolvida nesta ordem:
1. `-p source=<arquivo.md>` (ex.: um relatório gerado pelo agent `reports`);
2. `-p kb_query=...` (puxa trechos do RAG);
3. `--prompt "..."` (texto livre).

## NotebookLM

O NotebookLM não tem API pública estável, então o fluxo padrão é **assistido**:
o agent prepara o arquivo de fontes e você o carrega no NotebookLM para gerar
slides/infográficos/áudio. Configure `FORJA_NOTEBOOKLM_ENABLED` e
`FORJA_NOTEBOOKLM_NOTEBOOK_ID` para evoluir para automação futura.

## Exemplos

```bash
forja run slides --action outline -p source=output/reports/2026-10-04-status-x.md
forja run slides --action infographic -p kb_query="métricas do serviço X"
forja run slides --action notebooklm -p source=output/reports/2026-10-04-status-x.md -p title=status-x
```
