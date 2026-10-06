from forja.config import JiraBackend, Settings, VectorStore


def test_defaults():
    s = Settings(_env_file=None)
    assert s.llm_model == "claude-opus-4-8"
    assert s.vector_store is VectorStore.chroma
    assert s.jira_backend is JiraBackend.mcp
    assert s.is_production is False


def test_env_prefix(monkeypatch):
    monkeypatch.setenv("FORJA_PORT", "9999")
    monkeypatch.setenv("FORJA_LLM_MODEL", "claude-sonnet-5")
    s = Settings(_env_file=None)
    assert s.port == 9999
    assert s.llm_model == "claude-sonnet-5"


def test_require_raises_for_missing():
    s = Settings(_env_file=None)
    try:
        s.require("jira_base_url")
    except RuntimeError as exc:
        assert "FORJA_JIRA_BASE_URL" in str(exc)
    else:
        raise AssertionError("esperava RuntimeError")
