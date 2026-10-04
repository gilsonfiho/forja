"""Agent de padrões de commit, PR e DevOps.

Ações:
    commit (default) -> mensagem Conventional Commits a partir do diff staged
    pr               -> descrição de PR a partir dos commits base..head
    devops           -> padrões/artefatos de DevOps para uma stack
"""

from __future__ import annotations

from pathlib import Path

from workg.agents.commit_pr_devops import prompts
from workg.config import Settings, get_settings
from workg.integrations import git_repos
from workg.orchestrator.base import (
    AgentAction,
    AgentContext,
    AgentParam,
    AgentResult,
    AgentSpec,
    BaseAgent,
)
from workg.orchestrator.runtime import ClaudeRuntime, RuntimeUnavailableError


class CommitPrDevOpsAgent(BaseAgent):
    spec = AgentSpec(
        slug="commit-pr-devops",
        name="Commit / PR / DevOps",
        description="Gera commits (Conventional Commits), descrições de PR e padrões de DevOps.",
        tags=["git", "commit", "pr", "devops", "ci"],
        icon="🔀",
        actions=[
            AgentAction(
                name="commit",
                description="Mensagem Conventional Commits a partir do diff staged.",
                params=[
                    AgentParam(name="repo", help="Caminho do repositório.", placeholder="."),
                    AgentParam(name="diff", help="Diff explícito (senão usa git diff --staged)."),
                ],
            ),
            AgentAction(
                name="pr",
                description="Descrição de PR a partir dos commits base..head.",
                params=[
                    AgentParam(name="base", help="Branch base.", placeholder="develop"),
                    AgentParam(name="head", help="Branch head.", placeholder="HEAD"),
                    AgentParam(name="repo", help="Caminho do repositório."),
                ],
            ),
            AgentAction(
                name="devops",
                description="Padrões/artefatos de DevOps para uma stack.",
                params=[AgentParam(name="stack", help="Stack alvo.", placeholder="python")],
            ),
        ],
    )

    def __init__(self, settings: Settings | None = None, runtime: ClaudeRuntime | None = None):
        super().__init__()
        self.settings = settings or get_settings()
        self.runtime = runtime or ClaudeRuntime(self.settings)

    async def run(self, context: AgentContext) -> AgentResult:
        action = context.action if context.action != "default" else "commit"
        if action == "commit":
            return await self._commit(context)
        if action == "pr":
            return await self._pr(context)
        if action == "devops":
            return await self._devops(context)
        return self._result(
            context,
            ok=False,
            summary=f"Ação desconhecida: {action}",
            error="use 'commit', 'pr' ou 'devops'",
        ).done()

    async def _llm(self, context: AgentContext, prompt: str, summary_ok: str) -> AgentResult:
        if context.dry_run:
            return self._result(
                context, ok=True, summary=f"[dry-run] {summary_ok}", data={"prompt": prompt}
            ).done()
        try:
            text = await self.runtime.run(prompt, system_prompt=prompts.SYSTEM)
        except RuntimeUnavailableError as exc:
            return self._result(
                context, ok=False, summary="Runtime de LLM indisponível", error=str(exc)
            ).done()
        return self._result(context, ok=True, summary=summary_ok, data={"output": text}).done()

    async def _commit(self, context: AgentContext) -> AgentResult:
        diff = context.params.get("diff")
        if not diff:
            repo = Path(str(context.params.get("repo") or "."))
            diff = git_repos.diff(repo, staged=True)
        if not diff.strip():
            return self._result(
                context,
                ok=False,
                summary="Nenhuma mudança staged encontrada",
                error="faça 'git add' ou passe -p diff=... / -p repo=<caminho>",
            ).done()
        prompt = prompts.COMMIT_TEMPLATE.format(context=context.prompt or "—", diff=diff)
        return await self._llm(context, prompt, "Mensagem de commit gerada")

    async def _pr(self, context: AgentContext) -> AgentResult:
        base = str(context.params.get("base") or "develop")
        head = str(context.params.get("head") or "HEAD")
        repo = Path(str(context.params.get("repo") or "."))
        commits = context.params.get("commits")
        if not commits:
            commits = "\n".join(f"- {c}" for c in git_repos.log_range(repo, base, head))
        if not str(commits).strip():
            return self._result(
                context,
                ok=False,
                summary=f"Nenhum commit em {base}..{head}",
                error="verifique base/head ou passe -p commits=...",
            ).done()
        prompt = prompts.PR_TEMPLATE.format(
            base=base, head=head, context=context.prompt or "—", commits=commits
        )
        return await self._llm(context, prompt, f"Descrição de PR ({base}..{head}) gerada")

    async def _devops(self, context: AgentContext) -> AgentResult:
        stack = str(context.params.get("stack") or "python")
        prompt = prompts.DEVOPS_TEMPLATE.format(stack=stack, context=context.prompt or "—")
        return await self._llm(context, prompt, f"Padrões de DevOps para '{stack}' gerados")


def build() -> CommitPrDevOpsAgent:
    return CommitPrDevOpsAgent()
