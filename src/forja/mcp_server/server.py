"""Construção do servidor MCP do Forja."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from forja.agents import load_agents
from forja.logging_conf import get_logger
from forja.orchestrator.base import AgentContext, AgentSpec, registry

log = get_logger("mcp")

# Campos de texto a priorizar ao renderizar o resultado para o LLM.
_PRIMARY_KEYS = ("answer", "analysis", "output", "markdown", "report", "instructions")
_MAX_DATA_CHARS = 4000

ToolHandler = Callable[[str, str | None, dict[str, str] | None, bool], Awaitable[str]]


@dataclass(slots=True)
class ToolDef:
    name: str
    description: str
    handler: ToolHandler


def format_result(result: dict[str, Any]) -> str:
    """Formata um AgentResult (dict) em texto legível para o LLM."""
    status = "OK" if result.get("ok") else "ERRO"
    head = f"[{status}] {result.get('agent')} · {result.get('action')} — {result.get('summary')}"
    parts: list[str] = [head]

    data = result.get("data") or {}
    primary = next(
        (data[k] for k in _PRIMARY_KEYS if isinstance(data.get(k), str) and data[k].strip()),
        None,
    )
    if primary:
        parts.append("\n" + primary.strip())

    artifacts = result.get("artifacts") or []
    if artifacts:
        parts.append("\nArtefatos:\n" + "\n".join(f"- {a}" for a in artifacts))

    if result.get("error"):
        parts.append(f"\nErro: {result['error']}")

    # Demais dados estruturados (sem o campo primário já exibido), truncados.
    extra = {k: v for k, v in data.items() if not (primary and isinstance(v, str) and v == primary)}
    if extra:
        blob = json.dumps(extra, ensure_ascii=False, indent=2)
        if len(blob) > _MAX_DATA_CHARS:
            blob = blob[:_MAX_DATA_CHARS] + "\n... [truncado] ..."
        parts.append("\nDados:\n" + blob)

    return "\n".join(parts)


def _describe(spec: AgentSpec) -> str:
    """Monta a descrição da tool a partir do spec do agent."""
    lines = [spec.description]
    if spec.actions:
        lines.append("\nAções disponíveis:")
        for a in spec.actions:
            params = ", ".join(p.name + ("*" if p.required else "") for p in a.params)
            suffix = f" (params: {params})" if params else ""
            lines.append(f"- {a.name}: {a.description}{suffix}")
    lines.append(
        "\nChame com: action (string), prompt (instrução livre opcional), "
        "params (objeto chave→valor), dry_run (bool; True não executa efeitos)."
    )
    return "\n".join(lines)


def _make_handler(slug: str) -> ToolHandler:
    async def handler(
        action: str = "default",
        prompt: str | None = None,
        params: dict[str, str] | None = None,
        dry_run: bool = False,
    ) -> str:
        agent = registry.get(slug)
        ctx = AgentContext(
            action=action or "default",
            prompt=prompt,
            params=params or {},
            dry_run=dry_run,
        )
        result = await agent.run(ctx)
        return format_result(result.to_dict())

    handler.__name__ = f"forja_{slug.replace('-', '_')}"
    return handler


def agent_tools() -> list[ToolDef]:
    """Uma ToolDef por agent registrado."""
    load_agents()
    tools: list[ToolDef] = []
    for spec in registry.specs():
        tools.append(
            ToolDef(
                name=f"forja_{spec.slug.replace('-', '_')}",
                description=_describe(spec),
                handler=_make_handler(spec.slug),
            )
        )
    return tools


def _import_mcp() -> Any:
    try:
        from mcp.server.mcpserver import MCPServer  # type: ignore

        return MCPServer
    except ImportError:
        pass
    try:
        from mcp.server.fastmcp import FastMCP  # type: ignore  # mcp 1.x

        return FastMCP
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            'Pacote MCP não instalado. Instale o extra: pip install -e ".[mcp]"'
        ) from exc


def build_server() -> Any:
    """Cria o servidor MCP com todas as tools dos agents registradas."""
    from forja import __version__

    server_cls = _import_mcp()
    server = server_cls(name="forja", version=__version__)
    tools = agent_tools()
    for tool in tools:
        server.add_tool(tool.handler, name=tool.name, description=tool.description)
    log.info("mcp.build", tools=len(tools))
    return server


def run(transport: str = "stdio") -> None:
    """Sobe o servidor MCP (por padrão em stdio, como o Claude Code espera)."""
    build_server().run(transport)
