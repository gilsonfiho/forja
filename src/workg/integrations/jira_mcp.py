"""Integração com o Jira.

Dois backends:

* ``mcp``  — usa o **Atlassian Remote MCP Server** através do Claude Agent SDK.
  O LLM ganha acesso às ferramentas do Atlassian (buscar issues via JQL,
  ler/transicionar issues, etc.) e o agent apenas orquestra o prompt.
* ``rest`` — fallback direto na API REST do Jira Cloud (``atlassian-python-api``),
  útil para automações sem LLM.

A seleção vem de ``settings.jira_backend``.
"""

from __future__ import annotations

from typing import Any

from workg.config import JiraBackend, Settings

# Endpoint oficial do Atlassian Remote MCP Server.
ATLASSIAN_MCP_URL = "https://mcp.atlassian.com/v1/sse"

# Prefixo das tools expostas pelo servidor MCP (nome lógico "atlassian").
ATLASSIAN_TOOL_PREFIX = "mcp__atlassian"


def build_atlassian_mcp_servers() -> dict[str, Any]:
    """Config de ``mcp_servers`` para o Claude Agent SDK (backend MCP)."""
    return {
        "atlassian": {
            "type": "sse",
            "url": ATLASSIAN_MCP_URL,
        }
    }


def atlassian_allowed_tools() -> list[str]:
    """Permite todas as tools do servidor Atlassian via wildcard de prefixo."""
    return [f"{ATLASSIAN_TOOL_PREFIX}__*"]


class JiraRestClient:
    """Cliente REST mínimo para o backend ``rest`` (sem LLM)."""

    def __init__(self, settings: Settings) -> None:
        self.base_url = str(settings.require("jira_base_url"))
        self.email = str(settings.require("jira_email"))
        token = settings.require("jira_api_token")
        self._token = token.get_secret_value() if hasattr(token, "get_secret_value") else str(token)

    def _client(self) -> Any:
        try:
            from atlassian import Jira  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                'Backend REST requer o extra de integrações: pip install -e ".[integrations]"'
            ) from exc
        return Jira(url=self.base_url, username=self.email, password=self._token, cloud=True)

    def search(self, jql: str, limit: int = 50) -> list[dict[str, Any]]:
        client = self._client()
        raw = client.jql(jql, limit=limit)
        return raw.get("issues", []) if isinstance(raw, dict) else []


def describe_backend(settings: Settings) -> str:
    if settings.jira_backend is JiraBackend.mcp:
        return f"MCP Atlassian ({ATLASSIAN_MCP_URL})"
    return f"REST ({settings.jira_base_url or 'base_url não configurada'})"
