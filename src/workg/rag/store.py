"""Vector stores.

Padrão: :class:`InMemoryVectorStore` (sem dependências; persiste em JSON).
Opcional: :class:`ChromaVectorStore` quando ``chromadb`` está instalado e
``WORKG_VECTOR_STORE=chroma``.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from workg.config import Settings, VectorStore
from workg.logging_conf import get_logger

log = get_logger("rag.store")


@dataclass(slots=True)
class Record:
    id: str
    text: str
    vector: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class InMemoryVectorStore:
    """Store simples em memória com persistência em JSON."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = Path(path) if path else None
        self._records: dict[str, Record] = {}
        if self.path and self.path.exists():
            self._load()

    def reset(self) -> None:
        self._records.clear()
        if self.path and self.path.exists():
            self.path.unlink()

    def upsert(self, records: list[Record]) -> None:
        for r in records:
            self._records[r.id] = r
        self._persist()

    def query(self, vector: list[float], k: int = 5) -> list[tuple[Record, float]]:
        scored = [(r, cosine(vector, r.vector)) for r in self._records.values()]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]

    def count(self) -> int:
        return len(self._records)

    def _persist(self) -> None:
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [
            {"id": r.id, "text": r.text, "vector": r.vector, "metadata": r.metadata}
            for r in self._records.values()
        ]
        self.path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def _load(self) -> None:
        assert self.path is not None
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        for item in data:
            self._records[item["id"]] = Record(
                id=item["id"],
                text=item["text"],
                vector=item["vector"],
                metadata=item.get("metadata", {}),
            )


class ChromaVectorStore:
    """Store sobre ChromaDB (persistente)."""

    def __init__(self, path: Path, collection: str = "workg") -> None:
        import chromadb  # type: ignore

        self._client = chromadb.PersistentClient(path=str(path))
        self._col = self._client.get_or_create_collection(collection)

    def reset(self) -> None:
        name = self._col.name
        self._client.delete_collection(name)
        self._col = self._client.get_or_create_collection(name)

    def upsert(self, records: list[Record]) -> None:
        self._col.upsert(
            ids=[r.id for r in records],
            embeddings=[r.vector for r in records],
            documents=[r.text for r in records],
            metadatas=[r.metadata or {"_": "1"} for r in records],
        )

    def query(self, vector: list[float], k: int = 5) -> list[tuple[Record, float]]:
        res = self._col.query(query_embeddings=[vector], n_results=k)
        hits: list[tuple[Record, float]] = []
        ids = (res.get("ids") or [[]])[0]
        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]
        for i, doc, meta, dist in zip(ids, docs, metas, dists, strict=False):
            hits.append((Record(id=i, text=doc, vector=[], metadata=meta or {}), 1.0 - float(dist)))
        return hits

    def count(self) -> int:
        return int(self._col.count())


def get_store(settings: Settings) -> InMemoryVectorStore | ChromaVectorStore:
    if settings.vector_store is VectorStore.chroma:
        try:
            return ChromaVectorStore(settings.chroma_path)
        except Exception as exc:  # noqa: BLE001 - fallback intencional
            log.warning("rag.store.fallback", reason=str(exc))
    index_path = settings.chroma_path / "inmemory_index.json"
    return InMemoryVectorStore(index_path)
