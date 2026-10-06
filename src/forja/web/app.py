"""Aplicação FastAPI: API + dashboard."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from forja import __version__
from forja.agents import load_agents
from forja.config import get_settings
from forja.logging_conf import configure_logging, get_logger
from forja.orchestrator.base import registry
from forja.web.routes import api, pages

log = get_logger("web")
_STATIC_DIR = Path(__file__).resolve().parent / "static"


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title="Forja — Dev Workflow Copilot",
        version=__version__,
        description="Agents, skills e scripts orquestrados.",
    )

    load_agents()
    log.info("web.startup", agents=len(registry), env=settings.env.value)

    if _STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    app.include_router(api.router)
    app.include_router(pages.router)

    @app.get("/health", tags=["meta"])
    async def health() -> dict[str, object]:
        return {"status": "ok", "version": __version__, "agents": len(registry)}

    return app


app = create_app()
