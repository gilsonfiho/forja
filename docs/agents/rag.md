# Agent: RAG / Base de Conhecimento

Busca semântica e Q&A sobre os documentos `.md` de chamados e projetos
(pasta `knowledge_base/`, configurável por `FORJA_KNOWLEDGE_BASE_PATH`).

## Ações

- `query` (default): retorna os trechos mais relevantes (sem LLM).
- `ask`: sintetiza uma resposta citando as fontes (usa o LLM).
- `reindex`: (re)indexa a base de conhecimento.

## Embeddings e store

- **Embeddings** (`FORJA_EMBEDDINGS_PROVIDER`): `local` (sentence-transformers).
  Sem o pacote instalado, usa um embedder de hashing determinístico (offline).
- **Vector store** (`FORJA_VECTOR_STORE`): `chroma` (persistente) ou fallback
  em memória com persistência JSON.

## Exemplos

```bash
forja run rag --action reindex
forja run rag --action query --prompt "como resolvemos o timeout do serviço X?"
forja run rag --action ask -p q="passos do runbook de rollback" -p k=6
```
