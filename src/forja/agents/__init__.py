"""Agents da plataforma.

``load_agents`` descobre e registra os agents disponíveis no registry global.
Cada módulo de agent expõe uma função ``build() -> BaseAgent``. Módulos ainda
não implementados (ou cujos extras não estão instalados) são ignorados com
log de aviso, permitindo que a plataforma suba em modo parcial.
"""

from __future__ import annotations

import importlib

from forja.logging_conf import get_logger
from forja.orchestrator.base import AgentRegistry, registry

log = get_logger("agents")

# Módulos de agent conhecidos (preenchidos conforme as features são integradas).
_AGENT_MODULES: tuple[str, ...] = (
    "forja.agents.jira.agent",
    "forja.agents.repo_analysis.agent",
    "forja.agents.commit_pr_devops.agent",
    "forja.agents.rag.agent",
    "forja.agents.reports.agent",
    "forja.agents.slides.agent",
)


def load_agents(target: AgentRegistry | None = None) -> AgentRegistry:
    """Importa e registra todos os agents disponíveis.

    É idempotente dentro de um registry novo; chamar duas vezes no registry
    global pode levantar erro de duplicidade — use ``reset=True`` via um
    registry limpo em testes.
    """
    reg = target or registry
    for module_path in _AGENT_MODULES:
        try:
            module = importlib.import_module(module_path)
        except ImportError as exc:
            log.warning("agents.skip", module=module_path, reason=str(exc))
            continue
        builder = getattr(module, "build", None)
        if builder is None:
            log.warning("agents.no_build", module=module_path)
            continue
        agent = builder()
        if agent.slug not in reg:
            reg.register(agent)
            log.info("agents.loaded", slug=agent.slug)
    return reg


__all__ = ["load_agents"]
