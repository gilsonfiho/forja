"""Pipeline de RAG: ingestão de .md, chunking e busca semântica."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from workg.config import Settings, get_settings
from workg.logging_conf import get_logger
from workg.rag.embeddings import Embedder, get_embedder
from workg.rag.store import Record, get_store

log = get_logger("rag.pipeline")


@dataclass(slots=True)
class Hit:
    doc_id: str
    source: str
    score: float
    text: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "source": self.source,
            "score": round(self.score, 4),
            "text": self.text,
        }


def chunk_text(text: str, size: int = 900, overlap: int = 150) -> list[str]:
    """Divide o texto em janelas de caracteres com sobreposição."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= size:
        return [text]
    chunks: list[str] = []
    start = 0
    step = max(1, size - overlap)
    while start < len(text):
        chunks.append(text[start : start + size])
        start += step
    return chunks


def iter_documents(root: Path) -> list[tuple[str, str]]:
    """Retorna (caminho_relativo, conteúdo) de todos os .md sob ``root``."""
    root = Path(root)
    docs: list[tuple[str, str]] = []
    if not root.exists():
        return docs
    for path in sorted(root.rglob("*.md")):
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        docs.append((str(path.relative_to(root)), content))
    return docs


class KnowledgeBase:
    """Orquestra embedder + store para ingestão e consulta."""

    def __init__(self, settings: Settings | None = None, embedder: Embedder | None = None):
        self.settings = settings or get_settings()
        self.embedder = embedder or get_embedder(self.settings)
        self.store = get_store(self.settings)

    def reindex(self, root: Path | None = None) -> dict[str, int]:
        root = Path(root) if root else self.settings.knowledge_base_path
        self.store.reset()
        docs = iter_documents(root)
        records: list[Record] = []
        for source, content in docs:
            chunks = chunk_text(content)
            if not chunks:
                continue
            vectors = self.embedder.embed(chunks)
            for i, (chunk, vec) in enumerate(zip(chunks, vectors, strict=False)):
                rid = hashlib.sha1(f"{source}:{i}".encode()).hexdigest()[:16]  # noqa: S324
                records.append(
                    Record(id=rid, text=chunk, vector=vec, metadata={"source": source, "chunk": i})
                )
        if records:
            self.store.upsert(records)
        log.info("rag.reindex", docs=len(docs), chunks=len(records))
        return {"documents": len(docs), "chunks": len(records)}

    def query(self, question: str, k: int = 5) -> list[Hit]:
        if not question.strip():
            return []
        vector = self.embedder.embed([question])[0]
        results = self.store.query(vector, k=k)
        hits: list[Hit] = []
        for record, score in results:
            hits.append(
                Hit(
                    doc_id=record.id,
                    source=str(record.metadata.get("source", "?")),
                    score=float(score),
                    text=record.text,
                )
            )
        return hits

    def count(self) -> int:
        return self.store.count()
