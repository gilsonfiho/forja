"""Embeddings configuráveis.

Provider padrão: ``local`` (sentence-transformers). Caso o pacote não esteja
instalado, cai para :class:`HashingEmbedder` — um embedder determinístico e
sem dependências (hashing bag-of-words), suficiente para a plataforma
funcionar offline e para os testes.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol, runtime_checkable

from forja.config import EmbeddingsProvider, Settings
from forja.logging_conf import get_logger

log = get_logger("rag.embeddings")
_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


@runtime_checkable
class Embedder(Protocol):
    dim: int

    def embed(self, texts: list[str]) -> list[list[float]]: ...


def _l2_normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0.0:
        return vec
    return [v / norm for v in vec]


class HashingEmbedder:
    """Embedder determinístico via hashing de tokens (sem dependências)."""

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def _embed_one(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for token in _TOKEN_RE.findall(text.lower()):
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)  # noqa: S324
            idx = h % self.dim
            sign = 1.0 if (h >> 1) % 2 == 0 else -1.0
            vec[idx] += sign
        return _l2_normalize(vec)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(t) for t in texts]


class SentenceTransformerEmbedder:
    """Wrapper sobre sentence-transformers (provider local)."""

    def __init__(self, model_name: str) -> None:
        from sentence_transformers import SentenceTransformer  # type: ignore

        self._model = SentenceTransformer(model_name)
        self.dim = int(self._model.get_sentence_embedding_dimension())

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts, normalize_embeddings=True)
        return [list(map(float, v)) for v in vectors]


def get_embedder(settings: Settings) -> Embedder:
    """Fábrica de embedder conforme a configuração, com fallback seguro."""
    if settings.embeddings_provider is EmbeddingsProvider.local:
        try:
            return SentenceTransformerEmbedder(settings.embeddings_model)
        except Exception as exc:  # noqa: BLE001 - fallback intencional
            log.warning("rag.embeddings.fallback", reason=str(exc))
            return HashingEmbedder()
    # Providers remotos (voyage/openai) ainda não implementados -> fallback.
    log.warning("rag.embeddings.provider_unsupported", provider=settings.embeddings_provider)
    return HashingEmbedder()
