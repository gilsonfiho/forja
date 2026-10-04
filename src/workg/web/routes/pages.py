"""Rotas de páginas (dashboard HTML)."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from workg import __version__
from workg.orchestrator.base import registry

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    specs = [s.model_dump() for s in registry.specs()]
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "specs": specs,
            "specs_json": json.dumps(specs, ensure_ascii=False),
            "version": __version__,
        },
    )
