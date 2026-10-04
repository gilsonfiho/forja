# Base de Conhecimento (RAG)

Coloque aqui os documentos `.md` gerados de outros chamados, projetos,
runbooks e post-mortems. O agent de **RAG** ingere esta pasta
(recursivamente) para responder perguntas e alimentar relatórios.

## Organização sugerida

```
knowledge_base/
├── chamados/        # resumos e resoluções de tickets
├── projetos/        # docs de serviços/projetos
├── runbooks/        # procedimentos operacionais
└── postmortems/     # análises de incidentes
```

## Formato

- Markdown (`.md`), de preferência com um título `#` e seções claras.
- Metadados opcionais em frontmatter YAML (`title`, `tags`, `project`, `date`).

Após adicionar/editar arquivos, reindexe:

```bash
workg run rag --action reindex
```
