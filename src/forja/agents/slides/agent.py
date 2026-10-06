"""Agent de slides e infográficos.

Gera outlines de apresentação e specs de infográfico a partir de um relatório,
de uma consulta ao RAG ou de um texto livre; e prepara o pacote de fontes para
o NotebookLM.

Ações:
    outline (default) -> estrutura de slides (título + bullets por slide)
    infographic       -> spec de infográfico (seções, métricas, visuais)
    notebooklm        -> prepara o pacote de fontes p/ o NotebookLM
"""

from __future__ import annotations

from pathlib import Path

from forja.agents.slides import prompts
from forja.config import Settings, get_settings
from forja.integrations.notebooklm import NotebookLMAdapter
from forja.orchestrator.base import (
    AgentAction,
    AgentContext,
    AgentParam,
    AgentResult,
    AgentSpec,
    BaseAgent,
)
from forja.orchestrator.runtime import ClaudeRuntime, RuntimeUnavailableError
from forja.rag.pipeline import KnowledgeBase


class SlidesAgent(BaseAgent):
    spec = AgentSpec(
        slug="slides",
        name="Slides & Infographics",
        description="Gera outlines de slides/infográficos e prepara fontes para o NotebookLM.",
        tags=["slides", "infographic", "notebooklm"],
        icon="🎞️",
        actions=[
            AgentAction(
                name="outline",
                description="Estrutura de slides (título + bullets por slide).",
                params=[
                    AgentParam(name="source", help="Arquivo .md de origem (ex.: um relatório)."),
                    AgentParam(name="kb_query", help="Consulta ao RAG como fonte."),
                ],
            ),
            AgentAction(
                name="infographic",
                description="Spec de infográfico (mensagem, blocos, métricas).",
                params=[
                    AgentParam(name="source", help="Arquivo .md de origem."),
                    AgentParam(name="kb_query", help="Consulta ao RAG como fonte."),
                ],
            ),
            AgentAction(
                name="notebooklm",
                description="Prepara o pacote de fontes para o NotebookLM.",
                params=[
                    AgentParam(name="source", help="Arquivo .md de origem."),
                    AgentParam(name="title", help="Título do material."),
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
        self.notebooklm = NotebookLMAdapter(self.settings)

    @property
    def kb(self) -> KnowledgeBase:
        if self._kb is None:
            self._kb = KnowledgeBase(self.settings)
        return self._kb

    def _out_dir(self, context: AgentContext) -> Path:
        path = Path(str(context.params.get("output_dir") or "output/slides"))
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _source_content(self, context: AgentContext) -> str:
        """Resolve o conteúdo-fonte: arquivo, consulta RAG ou prompt."""
        src = context.params.get("source")
        if src and Path(str(src)).exists():
            return Path(str(src)).read_text(encoding="utf-8")
        kb_query = context.params.get("kb_query")
        if kb_query:
            hits = self.kb.query(str(kb_query), k=int(context.params.get("k", 6)))
            if hits:
                return "\n\n".join(f"[{h.source}]\n{h.text}" for h in hits)
        return context.prompt or ""

    async def run(self, context: AgentContext) -> AgentResult:
        action = context.action if context.action != "default" else "outline"
        if action == "outline":
            return await self._compose(context, prompts.OUTLINE, "outline", "slides.md")
        if action == "infographic":
            return await self._compose(
                context, prompts.INFOGRAPHIC, "infographic", "infographic.md"
            )
        if action == "notebooklm":
            return self._notebooklm(context)
        return self._result(
            context,
            ok=False,
            summary=f"Ação desconhecida: {action}",
            error="use 'outline', 'infographic' ou 'notebooklm'",
        ).done()

    async def _compose(
        self, context: AgentContext, template: str, kind: str, filename: str
    ) -> AgentResult:
        content = self._source_content(context)
        if not content.strip():
            return self._result(
                context,
                ok=False,
                summary="Sem conteúdo-fonte",
                error="informe --prompt, -p source=<arquivo.md> ou -p kb_query=...",
            ).done()
        if context.dry_run:
            return self._result(
                context,
                ok=True,
                summary=f"[dry-run] Geraria {kind}",
                data={"chars": len(content)},
            ).done()

        prompt = template.format(content=content[:12000])
        try:
            output = await self.runtime.run(prompt, system_prompt=prompts.SYSTEM)
        except RuntimeUnavailableError as exc:
            return self._result(
                context, ok=False, summary="Runtime de LLM indisponível", error=str(exc)
            ).done()

        out_path = self._out_dir(context) / filename
        out_path.write_text(output, encoding="utf-8")
        return self._result(
            context,
            ok=True,
            summary=f"{kind} gerado: {out_path}",
            data={"kind": kind, "path": str(out_path), "output": output},
            artifacts=[str(out_path)],
        ).done()

    def _notebooklm(self, context: AgentContext) -> AgentResult:
        content = self._source_content(context)
        if not content.strip():
            return self._result(
                context,
                ok=False,
                summary="Sem conteúdo-fonte para o NotebookLM",
                error="informe --prompt, -p source=<arquivo.md> ou -p kb_query=...",
            ).done()
        title = str(context.params.get("title") or "material")
        if context.dry_run:
            return self._result(
                context,
                ok=True,
                summary=f"[dry-run] Prepararia fontes '{title}'",
                data={"chars": len(content)},
            ).done()
        package = self.notebooklm.prepare_source(title, content, self._out_dir(context))
        result = self.notebooklm.generate(package)
        return self._result(
            context,
            ok=True,
            summary=f"Fontes para NotebookLM preparadas: {package.path}",
            data={"package": {"path": str(package.path), "chars": package.chars}, **result},
            artifacts=[str(package.path)],
        ).done()


def build() -> SlidesAgent:
    return SlidesAgent()
