import pytest
from pydantic import ValidationError

from workg.orchestrator.base import (
    AgentContext,
    AgentRegistry,
    AgentSpec,
    BaseAgent,
)


class DummyAgent(BaseAgent):
    spec = AgentSpec(slug="dummy", name="Dummy", description="agente de teste")

    async def run(self, context: AgentContext):
        return self._result(context, ok=True, summary="ok", data={"echo": context.params}).done()


async def test_agent_run_returns_result():
    agent = DummyAgent()
    ctx = AgentContext(action="default", params={"a": 1})
    result = await agent.run(ctx)
    assert result.ok
    assert result.agent == "dummy"
    assert result.data == {"echo": {"a": 1}}
    assert result.finished_at is not None


def test_registry_register_and_get():
    reg = AgentRegistry()
    reg.register(DummyAgent())
    assert "dummy" in reg
    assert len(reg) == 1
    assert reg.get("dummy").slug == "dummy"


def test_registry_rejects_duplicates():
    reg = AgentRegistry()
    reg.register(DummyAgent())
    with pytest.raises(ValueError):
        reg.register(DummyAgent())


def test_registry_unknown_agent():
    reg = AgentRegistry()
    with pytest.raises(KeyError):
        reg.get("nope")


def test_spec_requires_fields():
    with pytest.raises(ValidationError):
        AgentSpec(slug="x")  # faltam name/description
