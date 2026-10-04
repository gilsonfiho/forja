from pathlib import Path

from workg.agents.slides.agent import SlidesAgent, build
from workg.config import Settings
from workg.orchestrator.base import AgentContext


def _agent(tmp_path: Path) -> SlidesAgent:
    return SlidesAgent(settings=Settings(_env_file=None, knowledge_base_path=tmp_path / "kb"))


def test_build():
    assert build().slug == "slides"


async def test_outline_without_source_fails(tmp_path: Path):
    agent = _agent(tmp_path)
    result = await agent.run(AgentContext(action="outline"))
    assert not result.ok


async def test_outline_dry_run_counts_chars(tmp_path: Path):
    agent = _agent(tmp_path)
    ctx = AgentContext(action="outline", dry_run=True, prompt="conteúdo de exemplo")
    result = await agent.run(ctx)
    assert result.ok
    assert result.data["chars"] == len("conteúdo de exemplo")


async def test_notebooklm_prepares_source(tmp_path: Path):
    agent = _agent(tmp_path)
    out = tmp_path / "out"
    ctx = AgentContext(
        action="notebooklm",
        prompt="resumo do status do projeto",
        params={"title": "status-x", "output_dir": str(out)},
    )
    result = await agent.run(ctx)
    assert result.ok
    pkg = Path(result.data["package"]["path"])
    assert pkg.exists()
    assert "status do projeto" in pkg.read_text(encoding="utf-8")
    assert result.data["mode"] == "manual"  # notebooklm desabilitado por padrão


async def test_source_from_file(tmp_path: Path):
    src = tmp_path / "rep.md"
    src.write_text("# Relatório\nconteúdo", encoding="utf-8")
    agent = _agent(tmp_path)
    ctx = AgentContext(action="notebooklm", dry_run=True, params={"source": str(src)})
    result = await agent.run(ctx)
    assert result.ok
    assert result.data["chars"] > 0
