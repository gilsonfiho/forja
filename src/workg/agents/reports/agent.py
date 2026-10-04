"""Agent de relatórios.

Monta relatórios em Markdown a partir de múltiplas fontes: contexto livre,
inventário de repositórios (agent repo-analysis) e trechos da base de
conhecimento (RAG). Quando o LLM está disponível, sintetiza a narrativa;
caso contrário, gera um relatório estruturado determinístico.

Ações:
    generate (default) -> gera e salva um relatório Markdown
"""

from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path

from workg.config import Settings, get_settings
from workg.orchestrator.base import (
    AgentAction,
    AgentContext,
    AgentParam,
    AgentResult,
    AgentSpec,
    BaseAgent,
)
from workg.orchestrator.runtime import ClaudeRuntime, RuntimeUnavailableError
from workg.rag.pipeline import KnowledgeBase

SYSTEM = """\
Você é o agent de relatórios da WorkG. Produz relatórios de engenharia claros,
em Markdown, para um público técnico e de gestão. Use as seções fornecidas,
seja objetivo, destaque riscos e próximos passos. Responda em português.
"""

REPORT_TYPES = {"status", "sprint", "incident", "custom"}


def _slugify(text: str) -> str:
    slug = re.sub(r"[^\w\-]+", "-", text.strip().lower()).strip("-")
    return slug or "relatorio"


class ReportsAgent(BaseAgent):
    spec = AgentSpec(
        slug="reports",
        name="Reports",
        description="Gera relatórios (status, sprint, incidente) de repos, RAG e contexto.",
        tags=["reports", "markdown", "synthesis"],
        icon="📊",
        actions=[
            AgentAction(
                name="generate",
                description="Gera e salva um relatório Markdown.",
                params=[
                    AgentParam(
                        name="type",
                        help="status | sprint | incident | custom",
                        placeholder="status",
                    ),
                    AgentParam(name="title", help="Título do relatório."),
                    AgentParam(name="include", help="Fontes extras (ex.: repos)."),
                    AgentParam(name="kb_query", help="Consulta p/ puxar contexto do RAG."),
                ],
            ),
        ],
    )

    def __init__(
        self,
        settings: Settings | None = None,
        runtime: ClaudeRuntime | None = None,
        kb: KnowledgeBase | None = None,
    ):
        super().__init__()
        self.settings = settings or get_settings()
        self.runtime = runtime or ClaudeRuntime(self.settings)
        self._kb = kb

    @property
    def kb(self) -> KnowledgeBase:
        if self._kb is None:
            self._kb = KnowledgeBase(self.settings)
        return self._kb

    def _output_dir(self, context: AgentContext) -> Path:
        base = context.params.get("output_dir") or "output/reports"
        path = Path(str(base))
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _gather(self, context: AgentContext) -> dict[str, str]:
        """Coleta blocos de contexto das fontes solicitadas."""
        sections: dict[str, str] = {}
        if context.prompt:
            sections["Contexto"] = context.prompt

        kb_query = context.params.get("kb_query")
        if kb_query:
            hits = self.kb.query(str(kb_query), k=int(context.params.get("k", 5)))
            if hits:
                sections["Base de conhecimento"] = "\n".join(
                    f"- [{h.source}] {h.text[:300]}" for h in hits
                )

        include = str(context.params.get("include", "")).split(",")
        if "repos" in include:
            root = context.params.get("root") or self.settings.repos_root
            if root:
                from workg.integrations import git_repos

                repos = git_repos.scan(Path(str(root)))
                sections["Repositórios"] = "\n".join(
                    f"- {r.name}: branch={r.current_branch}, stacks={r.stacks}, "
                    f"ci={'sim' if r.has_ci else 'não'}, testes={'sim' if r.has_tests else 'não'}"
                    for r in repos
                )
        return sections

    def _fallback_markdown(self, title: str, rtype: str, sections: dict[str, str]) -> str:
        today = _dt.date.today().isoformat()
        lines = [f"# {title}", "", f"- **Tipo:** {rtype}", f"- **Data:** {today}", ""]
        for name, body in sections.items():
            lines += [f"## {name}", "", body, ""]
        if not sections:
            lines += ["## Resumo", "", "_Sem dados de contexto fornecidos._", ""]
        return "\n".join(lines)

    async def run(self, context: AgentContext) -> AgentResult:
        action = context.action if context.action != "default" else "generate"
        if action != "generate":
            return self._result(
                context, ok=False, summary=f"Ação desconhecida: {action}", error="use 'generate'"
            ).done()
        return await self._generate(context)

    async def _generate(self, context: AgentContext) -> AgentResult:
        rtype = str(context.params.get("type", "status")).lower()
        if rtype not in REPORT_TYPES:
            return self._result(
                context,
                ok=False,
                summary=f"Tipo inválido: {rtype}",
                error=f"use um de: {sorted(REPORT_TYPES)}",
            ).done()
        title = str(context.params.get("title") or f"Relatório de {rtype}")
        sections = self._gather(context)

        if context.dry_run:
            return self._result(
                context,
                ok=True,
                summary=f"[dry-run] Geraria relatório '{title}'",
                data={"type": rtype, "sections": list(sections)},
            ).done()

        markdown = self._fallback_markdown(title, rtype, sections)
        try:
            prompt = (
                f"Gere um relatório do tipo '{rtype}' intitulado '{title}'.\n\n"
                "Use as seções abaixo como fonte:\n\n"
                + "\n\n".join(f"### {k}\n{v}" for k, v in sections.items())
            )
            synthesized = await self.runtime.run(prompt, system_prompt=SYSTEM)
            if synthesized.strip():
                markdown = synthesized
        except RuntimeUnavailableError:
            pass  # usa o markdown determinístico

        out_dir = self._output_dir(context)
        filename = f"{_dt.date.today().isoformat()}-{_slugify(title)}.md"
        out_path = out_dir / filename
        out_path.write_text(markdown, encoding="utf-8")

        return self._result(
            context,
            ok=True,
            summary=f"Relatório gerado: {out_path}",
            data={"type": rtype, "title": title, "path": str(out_path), "sections": list(sections)},
            artifacts=[str(out_path)],
        ).done()


def build() -> ReportsAgent:
    return ReportsAgent()
