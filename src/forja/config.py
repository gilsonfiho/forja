"""Configuração central da aplicação.

Carrega variáveis de ambiente (prefixo ``FORJA_``) e/ou um arquivo ``.env``.
Todas as chaves são opcionais em tempo de import para permitir que a
plataforma suba em modo degradado; cada agent valida o que precisa quando
é efetivamente executado.
"""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    development = "development"
    production = "production"


class EmbeddingsProvider(StrEnum):
    local = "local"
    voyage = "voyage"
    openai = "openai"


class VectorStore(StrEnum):
    chroma = "chroma"
    pgvector = "pgvector"


class JiraBackend(StrEnum):
    mcp = "mcp"
    rest = "rest"


class Settings(BaseSettings):
    """Configurações carregadas de env vars / .env."""

    model_config = SettingsConfigDict(
        env_prefix="FORJA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ---- Aplicação ----
    env: Environment = Environment.development
    log_level: str = "INFO"
    host: str = "127.0.0.1"
    port: int = 8000

    # ---- LLM ----
    anthropic_api_key: SecretStr | None = None
    llm_model: str = "claude-opus-4-8"
    llm_max_tokens: int = 4096

    # ---- RAG / Embeddings ----
    embeddings_provider: EmbeddingsProvider = EmbeddingsProvider.local
    embeddings_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings_api_key: SecretStr | None = None
    vector_store: VectorStore = VectorStore.chroma
    chroma_path: Path = Path(".chroma")
    knowledge_base_path: Path = Path("knowledge_base")
    pgvector_dsn: SecretStr | None = None

    # ---- Jira ----
    jira_backend: JiraBackend = JiraBackend.mcp
    jira_base_url: str | None = None
    jira_email: str | None = None
    jira_api_token: SecretStr | None = None
    jira_default_project: str | None = None

    # ---- Repositórios ----
    repos_root: Path | None = None

    # ---- NotebookLM ----
    notebooklm_enabled: bool = False
    notebooklm_notebook_id: str | None = None

    @property
    def is_production(self) -> bool:
        return self.env is Environment.production

    def require(self, field: str) -> object:
        """Retorna o valor de um campo obrigatório ou lança erro claro."""
        value = getattr(self, field, None)
        if value in (None, ""):
            raise RuntimeError(
                f"Configuração obrigatória ausente: FORJA_{field.upper()}. "
                "Defina-a no .env (veja .env.example)."
            )
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton de configurações (cacheado)."""
    return Settings()
