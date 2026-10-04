from workg.agents.jira.agent import DEFAULT_JQL, JiraAgent, build
from workg.config import Settings
from workg.orchestrator.base import AgentContext


def _agent() -> JiraAgent:
    return JiraAgent(settings=Settings(_env_file=None))


async def test_build_returns_agent():
    assert build().slug == "jira"


async def test_analyze_dry_run_no_llm():
    agent = _agent()
    ctx = AgentContext(action="analyze", dry_run=True, params={"jql": "project = X"})
    result = await agent.run(ctx)
    assert result.ok
    assert result.data["jql"] == "project = X"
    assert "MCP" in result.data["backend"]


async def test_default_action_uses_default_jql_dry_run():
    agent = _agent()
    result = await agent.run(AgentContext(action="default", dry_run=True))
    assert result.ok
    assert result.data["jql"] == DEFAULT_JQL


async def test_unknown_action():
    agent = _agent()
    result = await agent.run(AgentContext(action="frobnicate"))
    assert not result.ok


async def test_list_requires_rest_backend():
    agent = _agent()  # default backend = mcp
    result = await agent.run(AgentContext(action="list"))
    assert not result.ok
    assert "REST" in result.summary
