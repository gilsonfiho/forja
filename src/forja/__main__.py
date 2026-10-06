"""CLI da plataforma Forja (Typer).

Comandos principais:
    forja serve     -> sobe o dashboard web (FastAPI/uvicorn)
    forja agents    -> lista os agents registrados
    forja run       -> executa um agent pela linha de comando
    forja version   -> mostra a versão
"""

from __future__ import annotations

import asyncio
import json

import typer
from rich.console import Console
from rich.table import Table

from forja import __version__
from forja.config import get_settings
from forja.logging_conf import configure_logging

app = typer.Typer(
    name="forja",
    help="Forja — Dev Workflow Copilot: agents, skills e scripts orquestrados.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


@app.command()
def version() -> None:
    """Mostra a versão instalada."""
    console.print(f"Forja [bold cyan]v{__version__}[/]")


@app.command()
def serve(
    host: str | None = typer.Option(None, help="Host (padrão: FORJA_HOST)."),
    port: int | None = typer.Option(None, help="Porta (padrão: FORJA_PORT)."),
    reload: bool = typer.Option(False, "--reload", help="Auto-reload (dev)."),
) -> None:
    """Sobe o dashboard web + API."""
    import uvicorn

    settings = get_settings()
    configure_logging(settings.log_level)
    uvicorn.run(
        "forja.web.app:app",
        host=host or settings.host,
        port=port or settings.port,
        reload=reload,
    )


@app.command()
def mcp() -> None:
    """Sobe o servidor MCP (stdio) que expõe os agents ao Claude Code/similares."""
    import sys

    from forja.mcp_server.server import run

    # stdout é o canal do protocolo MCP: logs vão para stderr.
    configure_logging(get_settings().log_level, stream=sys.stderr)
    run("stdio")


@app.command()
def agents() -> None:
    """Lista os agents registrados."""
    from forja.agents import load_agents

    load_agents()
    from forja.orchestrator.base import registry

    table = Table(title="Agents registrados")
    table.add_column("slug", style="cyan", no_wrap=True)
    table.add_column("nome")
    table.add_column("descrição", overflow="fold")
    for spec in registry.specs():
        table.add_row(spec.slug, spec.name, spec.description)
    if len(registry) == 0:
        console.print("[yellow]Nenhum agent disponível neste ambiente.[/]")
    else:
        console.print(table)


@app.command()
def run(
    slug: str = typer.Argument(..., help="slug do agent (ex.: jira)."),
    action: str = typer.Option("default", help="Ação do agent."),
    prompt: str | None = typer.Option(None, help="Instrução livre."),
    param: list[str] = typer.Option(None, "--param", "-p", help="Par chave=valor."),
    dry_run: bool = typer.Option(False, help="Não executar efeitos colaterais."),
) -> None:
    """Executa um agent pela CLI e imprime o resultado em JSON."""
    from forja.agents import load_agents
    from forja.orchestrator.base import AgentContext, registry

    configure_logging(get_settings().log_level)
    load_agents()

    params: dict[str, str] = {}
    for item in param or []:
        key, _, value = item.partition("=")
        params[key.strip()] = value.strip()

    try:
        agent = registry.get(slug)
    except KeyError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(code=1) from exc

    ctx = AgentContext(action=action, prompt=prompt, params=params, dry_run=dry_run)
    result = asyncio.run(agent.run(ctx))
    console.print_json(json.dumps(result.to_dict(), ensure_ascii=False))
    raise typer.Exit(code=0 if result.ok else 2)


if __name__ == "__main__":
    app()
