from workg.agents.commit_pr_devops.agent import CommitPrDevOpsAgent, build
from workg.config import Settings
from workg.orchestrator.base import AgentContext


def _agent() -> CommitPrDevOpsAgent:
    return CommitPrDevOpsAgent(settings=Settings(_env_file=None))


def test_build():
    assert build().slug == "commit-pr-devops"


async def test_commit_with_explicit_diff_dry_run():
    agent = _agent()
    ctx = AgentContext(action="commit", dry_run=True, params={"diff": "diff --git a b"})
    result = await agent.run(ctx)
    assert result.ok
    assert "Conventional Commits" in result.data["prompt"]


async def test_commit_without_changes_fails():
    agent = _agent()
    ctx = AgentContext(action="commit", params={"diff": "   "})
    result = await agent.run(ctx)
    assert not result.ok


async def test_pr_with_explicit_commits_dry_run():
    agent = _agent()
    ctx = AgentContext(
        action="pr", dry_run=True, params={"commits": "- feat: x", "base": "develop"}
    )
    result = await agent.run(ctx)
    assert result.ok
    assert "develop..HEAD" in result.summary


async def test_devops_dry_run():
    agent = _agent()
    ctx = AgentContext(action="devops", dry_run=True, params={"stack": "go"})
    result = await agent.run(ctx)
    assert result.ok
    assert "go" in result.summary


async def test_unknown_action():
    agent = _agent()
    result = await agent.run(AgentContext(action="nope"))
    assert not result.ok
