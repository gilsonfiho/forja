"""Contratos base de agents e o registry central.

Todo agent da plataforma herda de :class:`BaseAgent`, declara um
:class:`AgentSpec` (metadados) e implementa ``run``. O :class:`AgentRegistry`
mantém as instâncias disponíveis para a API/dashboard e para o CLI.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class AgentParam(BaseModel):
    """Parâmetro aceito por uma ação (dirige o formulário dinâmico na UI)."""

    name: str
    required: bool = False
    help: str = ""
    placeholder: str = ""


class AgentAction(BaseModel):
    """Ação exposta por um agent."""

    name: str
    description: str = ""
    params: list[AgentParam] = Field(default_factory=list)
    accepts_prompt: bool = True


class AgentSpec(BaseModel):
    """Metadados declarativos de um agent."""

    slug: str = Field(..., description="Identificador único, kebab-case (ex: 'jira').")
    name: str = Field(..., description="Nome legível.")
    description: str = Field(..., description="O que o agent faz.")
    tags: list[str] = Field(default_factory=list)
    version: str = "0.1.0"
    actions: list[AgentAction] = Field(default_factory=list)
    icon: str = "⚙"


class AgentContext(BaseModel):
    """Entrada de uma execução de agent."""

    action: str = Field(default="default", description="Ação/rota interna do agent.")
    params: dict[str, Any] = Field(default_factory=dict)
    prompt: str | None = Field(default=None, description="Instrução livre opcional.")
    dry_run: bool = Field(default=False, description="Se True, não executa efeitos colaterais.")


@dataclass(slots=True)
class AgentResult:
    """Saída padronizada de uma execução de agent."""

    agent: str
    action: str
    ok: bool
    summary: str
    data: dict[str, Any] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    finished_at: str | None = None
    error: str | None = None

    def done(self) -> AgentResult:
        self.finished_at = datetime.now(UTC).isoformat()
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent": self.agent,
            "action": self.action,
            "ok": self.ok,
            "summary": self.summary,
            "data": self.data,
            "artifacts": self.artifacts,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "error": self.error,
        }


class BaseAgent(abc.ABC):
    """Classe base de todos os agents."""

    spec: AgentSpec

    def __init__(self) -> None:
        if not getattr(self, "spec", None):
            raise TypeError(f"{type(self).__name__} precisa declarar 'spec: AgentSpec'.")

    @property
    def slug(self) -> str:
        return self.spec.slug

    @abc.abstractmethod
    async def run(self, context: AgentContext) -> AgentResult:
        """Executa a ação pedida e retorna um resultado padronizado."""

    def _result(self, context: AgentContext, *, ok: bool, summary: str, **kw: Any) -> AgentResult:
        return AgentResult(agent=self.slug, action=context.action, ok=ok, summary=summary, **kw)


class AgentRegistry:
    """Registro central de agents disponíveis."""

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> BaseAgent:
        if agent.slug in self._agents:
            raise ValueError(f"Agent duplicado: '{agent.slug}'.")
        self._agents[agent.slug] = agent
        return agent

    def get(self, slug: str) -> BaseAgent:
        try:
            return self._agents[slug]
        except KeyError as exc:
            raise KeyError(f"Agent desconhecido: '{slug}'.") from exc

    def all(self) -> list[BaseAgent]:
        return list(self._agents.values())

    def specs(self) -> list[AgentSpec]:
        return [a.spec for a in self._agents.values()]

    def __contains__(self, slug: object) -> bool:
        return slug in self._agents

    def __len__(self) -> int:
        return len(self._agents)


# Registry global (preenchido por workg.agents.load_agents()).
registry = AgentRegistry()
