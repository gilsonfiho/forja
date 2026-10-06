"""Agent de análise de repositórios de serviços/projetos.

Ações:
    scan (default) -> inventário dos repositórios sob FORJA_REPOS_ROOT
    analyze        -> análise de saúde (LLM) de um repositório específico
"""

from __future__ import annotations

from pathlib import Path

from forja.config import Settings, get_settings
from forja.integrations import git_repos
from forja.logging_conf import get_logger
from forja.orchestrator.base import (
    AgentAction,
    AgentContext,
    AgentParam,
    AgentResult,
    AgentSpec,
    BaseAgent,
)
from forja.orchestrator.runtime import ClaudeRuntime, RuntimeUnavailableError

log = get_logger("agent.repo")

SYSTEM = """\
Você é o agent de análise de repositórios da Forja. Avalie a saúde de
repositórios de engenharia a partir dos metadados fornecidos: stack, CI,
testes, README, atividade (último commit) e estado (mudanças não commitadas).
Aponte riscos (sem CI, sem testes, parado há muito tempo, dirty) e dê
recomendações priorizadas. Responda em português, de forma objetiva.
"""


class RepoAnalysisAgent(BaseAgent):
    spec = AgentSpec(
        slug="repo-analysis",
        name="Repo Analysis",
        description="Varre e analisa repositórios de serviços/projetos (saúde, stack, CI).",
        tags=["git", "repos", "health"],
        icon="🗂️",
        actions=[
            AgentAction(
                name="scan",
                description="Inventário de todos os repositórios sob a raiz.",
                accepts_prompt=False,
                params=[
                    AgentParam(name="root", help="Raiz dos repos (default FORJA_REPOS_ROOT)."),
                    AgentParam(name="max_depth", help="Profundidade da busca.", placeholder="3"),
                ],
            ),
            AgentAction(
                name="analyze",
                description="Análise de saúde (LLM) de um repositório específico.",
                params=[
                    AgentParam(name="name", required=True, help="Nome do repositório."),
                    AgentParam(name="root", help="Raiz dos repos."),
                ],
            ),
        ],
    )

    def __init__(self, settings: Settings | None = None, runtime: ClaudeRuntime | None = None):
        super().__init__()
        self.settings = settings or get_settings()
        self.runtime = runtime or ClaudeRuntime(self.settings)

    def _root(self, context: AgentContext) -> Path | None:
        raw = context.params.get("root") or self.settings.repos_root
        return Path(str(raw)) if raw else None

    async def run(self, context: AgentContext) -> AgentResult:
        action = context.action if context.action != "default" else "scan"
        if action == "scan":
            return self._scan(context)
        if action == "analyze":
            return await self._analyze(context)
        return self._result(
            context,
            ok=False,
            summary=f"Ação desconhecida: {action}",
            error="use 'scan' ou 'analyze'",
        ).done()

    def _scan(self, context: AgentContext) -> AgentResult:
        root = self._root(context)
        if not root:
            return self._result(
                context,
                ok=False,
                summary="Raiz de repositórios não definida",
                error="defina FORJA_REPOS_ROOT ou passe -p root=<caminho>",
            ).done()
        max_depth = int(context.params.get("max_depth", 3))
        repos = git_repos.scan(root, max_depth=max_depth)
        data = {
            "root": str(root),
            "count": len(repos),
            "repos": [r.to_dict() for r in repos],
            "risks": {
                "sem_ci": [r.name for r in repos if not r.has_ci],
                "sem_testes": [r.name for r in repos if not r.has_tests],
                "dirty": [r.name for r in repos if r.dirty],
            },
        }
        return self._result(
            context,
            ok=True,
            summary=f"{len(repos)} repositórios encontrados em {root}",
            data=data,
        ).done()

    async def _analyze(self, context: AgentContext) -> AgentResult:
        root = self._root(context)
        name = context.params.get("name")
        if not root or not name:
            return self._result(
                context,
                ok=False,
                summary="Parâmetros insuficientes",
                error="informe 'name' (e FORJA_REPOS_ROOT ou -p root=...)",
            ).done()
        repo_path = Path(root) / str(name)
        if not (repo_path / ".git").exists():
            return self._result(
                context,
                ok=False,
                summary=f"Repositório não encontrado: {name}",
                error=str(repo_path),
            ).done()

        info = git_repos.inspect_repo(repo_path)
        if context.dry_run:
            return self._result(
                context, ok=True, summary=f"[dry-run] Analisaria {name}", data=info.to_dict()
            ).done()
        try:
            text = await self.runtime.run(
                f"Metadados do repositório:\n{info.to_dict()}\n\nContexto: {context.prompt or '—'}",
                system_prompt=SYSTEM,
            )
        except RuntimeUnavailableError as exc:
            # Sem LLM ainda entregamos o inventário cru + aviso.
            return self._result(
                context,
                ok=True,
                summary=f"Inventário de {name} (sem análise LLM)",
                data=info.to_dict(),
                error=str(exc),
            ).done()
        return self._result(
            context,
            ok=True,
            summary=f"Análise de {name} concluída",
            data={**info.to_dict(), "analysis": text},
        ).done()


def build() -> RepoAnalysisAgent:
    return RepoAnalysisAgent()
