"""API REST dos agents."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from workg.orchestrator.base import AgentContext, registry

router = APIRouter(prefix="/api", tags=["agents"])


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
