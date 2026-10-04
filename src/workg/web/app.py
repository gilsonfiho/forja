"""Aplicação FastAPI (API + dashboard).

Na fundação expõe apenas health/version e a listagem de agents. O
dashboard rico e as rotas por agent são adicionados na feature de UI.
"""

from __future__ import annotations

from fastapi import FastAPI

from workg import __version__
from workg.agents import load_agents
from workg.config import get_settings
from workg.logging_conf import configure_logging, get_logger
from workg.orchestrator.base import registry

log = get_logger("web")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title="WorkG — Dev Workflow Copilot",
        version=__version__,
        description="Agents, skills e scripts orquestrados.",
    )

    load_agents()
    log.info("web.startup", agents=len(registry), env=settings.env.value)

    @app.get("/health", tags=["meta"])
    async def health() -> dict[str, object]:
        return {"status": "ok", "version": __version__, "agents": len(registry)}

    @app.get("/api/agents", tags=["agents"])
    async def list_agents() -> list[dict[str, object]]:
        return [spec.model_dump() for spec in registry.specs()]

    return app


app = create_app()
