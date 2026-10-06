"""Forja como servidor MCP.

Expõe cada agent da plataforma como uma *tool* MCP, para ser consumido pelo
Claude Code, Cursor, Claude Desktop e similares. A lógica de montar as tools
(:func:`agent_tools`) e formatar o resultado (:func:`format_result`) é
independente do SDK MCP, para facilitar testes; :func:`build_server` e
:func:`run` fazem a ponte com o pacote ``mcp``.
"""

from forja.mcp_server.server import (
    ToolDef,
    agent_tools,
    build_server,
    format_result,
    run,
)

__all__ = ["ToolDef", "agent_tools", "build_server", "format_result", "run"]
