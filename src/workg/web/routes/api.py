"""API REST dos agents."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from workg.config import get_settings
from workg.orchestrator.base import AgentContext, registry

router = APIRouter(prefix="/api", tags=["agents"])

# Extensões consideradas texto renderizável.
_TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".csv", ".py", ".toml", ".log", ""}
_MAX_BYTES = 1_000_000


class RunRequest(BaseModel):
    action: str = "default"
    prompt: str | None = None
    params: dict[str, str] = Field(default_factory=dict)
    dry_run: bool = False


@router.get("/agents")
async def list_agents() -> list[dict[str, object]]:
    return [spec.model_dump() for spec in registry.specs()]


@router.post("/agents/{slug}/run")
async def run_agent(slug: str, body: RunRequest) -> dict[str, object]:
    try:
        agent = registry.get(slug)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    ctx = AgentContext(
        action=body.action, prompt=body.prompt, params=body.params, dry_run=body.dry_run
    )
    result = await agent.run(ctx)
    return result.to_dict()


def _allowed_roots() -> list[Path]:
    settings = get_settings()
    roots = [
        Path("output").resolve(),
        Path("reports_out").resolve(),
        settings.knowledge_base_path.resolve(),
    ]
    return roots


@router.get("/artifact")
async def read_artifact(path: str = Query(..., description="Caminho do artefato.")) -> dict:
    """Retorna o conteúdo (texto) de um artefato, restrito às pastas de saída."""
    target = Path(path).resolve()
    roots = _allowed_roots()
    if not any(_is_within(target, root) for root in roots):
        raise HTTPException(status_code=403, detail="Caminho fora das pastas permitidas.")
    if not target.is_file():
        raise HTTPException(status_code=404, detail="Artefato não encontrado.")
    if target.stat().st_size > _MAX_BYTES:
        raise HTTPException(status_code=413, detail="Artefato muito grande para pré-visualizar.")

    suffix = target.suffix.lower()
    if suffix not in _TEXT_SUFFIXES:
        raise HTTPException(status_code=415, detail=f"Tipo não pré-visualizável: {suffix}")
    try:
        content = target.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=422, detail="Falha ao ler o artefato.") from exc

    kind = "markdown" if suffix == ".md" else (suffix.lstrip(".") or "text")
    return {"path": str(target), "name": target.name, "kind": kind, "content": content}


def _is_within(target: Path, root: Path) -> bool:
    try:
        target.relative_to(root)
        return True
    except ValueError:
        return False
