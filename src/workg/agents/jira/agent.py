"""Agent de Jira: analisa e ajuda a controlar issues.

Ações:
    analyze (default) -> resume/triage issues de uma JQL
    list              -> lista issues (crus) de uma JQL

Backend definido por ``settings.jira_backend`` (mcp | rest).
"""

from __future__ import annotations

from workg.agents.jira import prompts
from workg.config import JiraBackend, Settings, get_settings
from workg.integrations import jira_mcp
from workg.logging_conf import get_logger
from workg.orchestrator.base import (
    AgentAction,
    AgentContext,
    AgentParam,
    AgentResult,
    AgentSpec,
    BaseAgent,
)
from workg.orchestrator.runtime import ClaudeRuntime, RuntimeUnavailableError

log = get_logger("agent.jira")

DEFAULT_JQL = "assignee = currentUser() AND statusCategory != Done ORDER BY updated DESC"


class JiraAgent(BaseAgent):
    spec = AgentSpec(
        slug="jira",
        name="Jira",
        description="Analisa e ajuda a controlar tasks no Jira (via MCP Atlassian ou REST).",
        tags=["jira", "tasks", "planning"],
        icon="📋",
        actions=[
            AgentAction(
                name="analyze",
                description="Resume e faz triagem das issues de uma JQL.",
                params=[
                    AgentParam(
                        name="jql",
                        help="Consulta JQL.",
                        placeholder="project = ABC AND sprint in openSprints()",
                    ),
                ],
            ),
            AgentAction(
                name="list",
                description="Lista issues cruas (apenas backend REST).",
                accepts_prompt=False,
                params=[AgentParam(name="jql", help="Consulta JQL.")],
            ),
        ],
    )

    def __init__(self, settings: Settings | None = None, runtime: ClaudeRuntime | None = None):
        super().__init__()
        self.settings = settings or get_settings()
        self.runtime = runtime or ClaudeRuntime(self.settings)

    async def run(self, context: AgentContext) -> AgentResult:
        action = context.action if context.action != "default" else "analyze"
        jql = str(context.params.get("jql") or DEFAULT_JQL)

        if action == "list":
            return await self._list(context, jql)
        if action == "analyze":
            return await self._analyze(context, jql)
        return self._result(
            context,
            ok=False,
            summary=f"Ação desconhecida: {action}",
            error="use 'analyze' ou 'list'",
        ).done()

    async def _analyze(self, context: AgentContext, jql: str) -> AgentResult:
        backend = jira_mcp.describe_backend(self.settings)
        if context.dry_run:
            return self._result(
                context,
                ok=True,
                summary=f"[dry-run] Analisaria JQL via {backend}",
                data={"jql": jql, "backend": backend},
            ).done()

        prompt = prompts.ANALYZE_TEMPLATE.format(jql=jql, context=context.prompt or "—")
        try:
            if self.settings.jira_backend is JiraBackend.mcp:
                text = await self.runtime.run(
                    prompt,
                    system_prompt=prompts.SYSTEM,
                    mcp_servers=jira_mcp.build_atlassian_mcp_servers(),
                    allowed_tools=jira_mcp.atlassian_allowed_tools(),
                )
            else:
                issues = jira_mcp.JiraRestClient(self.settings).search(jql)
                text = await self.runtime.run(
                    f"{prompt}\n\nIssues (JSON):\n{issues}",
                    system_prompt=prompts.SYSTEM,
                )
        except RuntimeUnavailableError as exc:
            return self._result(
                context, ok=False, summary="Runtime de LLM indisponível", error=str(exc)
            ).done()
        except Exception as exc:  # noqa: BLE001 - superfície de erro p/ a UI
            log.error("jira.analyze.error", error=str(exc))
            return self._result(
                context, ok=False, summary="Falha ao analisar Jira", error=str(exc)
            ).done()

        return self._result(
            context,
            ok=True,
            summary="Análise de issues concluída",
            data={"jql": jql, "backend": backend, "analysis": text},
        ).done()

    async def _list(self, context: AgentContext, jql: str) -> AgentResult:
        if self.settings.jira_backend is not JiraBackend.rest:
            return self._result(
                context,
                ok=False,
                summary="'list' cru só está disponível no backend REST",
                error="defina WORKG_JIRA_BACKEND=rest ou use a ação 'analyze'",
            ).done()
        if context.dry_run:
            return self._result(
                context, ok=True, summary="[dry-run] Listaria issues", data={"jql": jql}
            ).done()
        try:
            issues = jira_mcp.JiraRestClient(self.settings).search(jql)
        except Exception as exc:  # noqa: BLE001
            return self._result(
                context, ok=False, summary="Falha ao listar issues", error=str(exc)
            ).done()
        keys = [i.get("key") for i in issues]
        return self._result(
            context,
            ok=True,
            summary=f"{len(issues)} issues",
            data={"jql": jql, "keys": keys, "issues": issues},
        ).done()


def build() -> JiraAgent:
    return JiraAgent()
