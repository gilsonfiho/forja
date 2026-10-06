import pytest

from forja.mcp_server.server import agent_tools, build_server, format_result


def test_agent_tools_one_per_agent():
    tools = agent_tools()
    names = {t.name for t in tools}
    assert "forja_jira" in names
    assert "forja_repo_analysis" in names  # hífen -> underscore
    assert all(t.name.startswith("forja_") for t in tools)
    assert len(tools) >= 6


def test_tool_description_lists_actions():
    jira = next(t for t in agent_tools() if t.name == "forja_jira")
    assert "analyze" in jira.description
    assert "params" in jira.description


def test_format_result_renders_primary_and_artifacts():
    result = {
        "agent": "reports",
        "action": "generate",
        "ok": True,
        "summary": "Relatório gerado",
        "data": {"analysis": "# Título\nconteúdo", "type": "status"},
        "artifacts": ["output/reports/x.md"],
        "error": None,
    }
    text = format_result(result)
    assert "[OK] reports · generate" in text
    assert "# Título" in text
    assert "output/reports/x.md" in text
    assert '"type": "status"' in text  # dado extra em JSON


def test_format_result_error():
    result = {
        "agent": "jira",
        "action": "analyze",
        "ok": False,
        "summary": "falhou",
        "data": {},
        "artifacts": [],
        "error": "boom",
    }
    text = format_result(result)
    assert "[ERRO]" in text
    assert "boom" in text


async def test_tool_handler_dry_run():
    jira = next(t for t in agent_tools() if t.name == "forja_jira")
    out = await jira.handler("analyze", None, {"jql": "project = X"}, True)
    assert "[OK] jira · analyze" in out
    assert "dry-run" in out.lower()


async def test_build_server_registers_tools():
    pytest.importorskip("mcp")
    server = build_server()
    tools = await server.list_tools()
    tool_names = {t.name for t in tools}
    assert "forja_jira" in tool_names
    assert "forja_rag" in tool_names
