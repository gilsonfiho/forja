"""RAG: ingestão da base de conhecimento, embeddings e busca semântica."""

from workg.rag.pipeline import Hit, KnowledgeBase, chunk_text

__all__ = ["Hit", "KnowledgeBase", "chunk_text"]
