import pytest
from fastapi.testclient import TestClient

from workg.web.app import create_app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app())


def test_health(client: TestClient):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["agents"] >= 1


def test_list_agents(client: TestClient):
    res = client.get("/api/agents")
    assert res.status_code == 200
    slugs = {a["slug"] for a in res.json()}
    assert {"jira", "rag", "reports", "slides"}.issubset(slugs)


def test_dashboard_page(client: TestClient):
    res = client.get("/")
    assert res.status_code == 200
    assert "WorkG" in res.text
    assert "Executar" in res.text


def test_run_agent_dry_run(client: TestClient):
    res = client.post(
        "/api/agents/jira/run",
        json={"action": "analyze", "dry_run": True, "params": {"jql": "project = X"}},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    assert body["agent"] == "jira"


def test_run_unknown_agent_404(client: TestClient):
    res = client.post("/api/agents/nope/run", json={})
    assert res.status_code == 404
