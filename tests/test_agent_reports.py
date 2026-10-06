from pathlib import Path

from forja.agents.reports.agent import ReportsAgent, _slugify, build
from forja.config import Settings
from forja.orchestrator.base import AgentContext


def test_slugify():
    assert _slugify("Status Semanal!") == "status-semanal"
    assert _slugify("   ") == "relatorio"


def test_build():
    assert build().slug == "reports"


def _agent(tmp_path: Path) -> ReportsAgent:
    return ReportsAgent(settings=Settings(_env_file=None, knowledge_base_path=tmp_path / "kb"))


async def test_generate_writes_markdown(tmp_path: Path):
    agent = _agent(tmp_path)
    out = tmp_path / "out"
    ctx = AgentContext(
        action="generate",
        prompt="Semana tranquila, sem incidentes.",
        params={"type": "status", "title": "Status X", "output_dir": str(out)},
    )
    result = await agent.run(ctx)
    assert result.ok
    path = Path(result.data["path"])
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "Status X" in content
    assert "Semana tranquila" in content
    assert result.artifacts == [str(path)]


async def test_invalid_type(tmp_path: Path):
    agent = _agent(tmp_path)
    result = await agent.run(AgentContext(action="generate", params={"type": "bogus"}))
    assert not result.ok


async def test_dry_run_does_not_write(tmp_path: Path):
    agent = _agent(tmp_path)
    out = tmp_path / "out"
    ctx = AgentContext(action="generate", dry_run=True, params={"output_dir": str(out)})
    result = await agent.run(ctx)
    assert result.ok
    assert not out.exists() or not any(out.iterdir())
