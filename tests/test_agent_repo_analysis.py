from pathlib import Path

from forja.agents.repo_analysis.agent import RepoAnalysisAgent, build
from forja.config import Settings
from forja.integrations import git_repos
from forja.orchestrator.base import AgentContext


def _make_repo(root: Path, name: str, *, with_ci: bool = False, with_tests: bool = False) -> Path:
    repo = root / name
    (repo / ".git").mkdir(parents=True)
    (repo / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    (repo / "README.md").write_text("# x\n", encoding="utf-8")
    if with_ci:
        (repo / ".github" / "workflows").mkdir(parents=True)
    if with_tests:
        (repo / "tests").mkdir()
    return repo


def test_discover_and_inspect(tmp_path: Path):
    _make_repo(tmp_path, "svc-a", with_ci=True, with_tests=True)
    _make_repo(tmp_path, "svc-b")
    repos = git_repos.scan(tmp_path)
    names = {r.name for r in repos}
    assert names == {"svc-a", "svc-b"}
    a = next(r for r in repos if r.name == "svc-a")
    assert "python" in a.stacks
    assert a.has_ci and a.has_tests and a.has_readme


def test_build():
    assert build().slug == "repo-analysis"


async def test_scan_action_reports_risks(tmp_path: Path):
    _make_repo(tmp_path, "svc-a", with_ci=True, with_tests=True)
    _make_repo(tmp_path, "svc-b")  # sem ci, sem testes
    agent = RepoAnalysisAgent(settings=Settings(_env_file=None))
    result = await agent.run(AgentContext(action="scan", params={"root": str(tmp_path)}))
    assert result.ok
    assert result.data["count"] == 2
    assert "svc-b" in result.data["risks"]["sem_ci"]
    assert "svc-b" in result.data["risks"]["sem_testes"]
    assert "svc-a" not in result.data["risks"]["sem_ci"]


async def test_scan_without_root_fails():
    agent = RepoAnalysisAgent(settings=Settings(_env_file=None))
    result = await agent.run(AgentContext(action="scan"))
    assert not result.ok
