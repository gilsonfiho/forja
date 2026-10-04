"""Agent de RAG: busca e responde sobre a base de conhecimento (.md).

Ações:
    query (default) -> retorna os trechos mais relevantes (sem LLM)
    ask             -> sintetiza uma resposta citando as fontes (LLM)
    reindex         -> reindexa a base de conhecimento
"""

from __future__ import annotations

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
Você é o agent de RAG da WorkG. Responda à pergunta do usuário usando SOMENTE
o contexto fornecido (trechos da base de conhecimento). Cite as fontes pelo
nome do arquivo entre colchetes, ex.: [chamados/x.md]. Se o contexto não
cobrir a pergunta, diga isso explicitamente. Responda em português.
"""


class RagAgent(BaseAgent):
    spec = AgentSpec(
        slug="rag",
        name="RAG / Base de Conhecimento",
        description="Busca semântica e Q&A sobre os documentos .md de chamados e projetos.",
        tags=["rag", "search", "knowledge"],
        icon="🔎",
        actions=[
            AgentAction(
                name="query",
                description="Retorna os trechos mais relevantes (sem LLM).",
                params=[
                    AgentParam(name="q", help="Pergunta (ou use o campo prompt)."),
                    AgentParam(name="k", help="Nº de trechos.", placeholder="5"),
                ],
            ),
            AgentAction(
                name="ask",
                description="Sintetiza uma resposta citando as fontes (LLM).",
                params=[
                    AgentParam(name="q", help="Pergunta (ou use o campo prompt)."),
                    AgentParam(name="k", help="Nº de trechos.", placeholder="5"),
                ],
            ),
            AgentAction(
                name="reindex",
                description="(Re)indexa a base de conhecimento.",
                accepts_prompt=False,
            ),
        ],
    )

    def __init__(
        self,
        settings: Settings | None = None,
        kb: KnowledgeBase | None = None,
        runtime: ClaudeRuntime | None = None,
    ):
        super().__init__()
        self.settings = settings or get_settings()
        self.kb = kb or KnowledgeBase(self.settings)
        self.runtime = runtime or ClaudeRuntime(self.settings)

    async def run(self, context: AgentContext) -> AgentResult:
        action = context.action if context.action != "default" else "query"
        if action == "reindex":
            return self._reindex(context)
        if action == "query":
            return self._query(context)
        if action == "ask":
            return await self._ask(context)
        return self._result(
            context,
            ok=False,
            summary=f"Ação desconhecida: {action}",
            error="use 'query', 'ask' ou 'reindex'",
        ).done()

    def _reindex(self, context: AgentContext) -> AgentResult:
        if context.dry_run:
            return self._result(context, ok=True, summary="[dry-run] Reindexaria a base").done()
        stats = self.kb.reindex()
        return self._result(
            context,
            ok=True,
            summary=f"Base reindexada: {stats['documents']} docs, {stats['chunks']} chunks",
            data=stats,
        ).done()

    def _question(self, context: AgentContext) -> str:
        return str(context.params.get("q") or context.prompt or "").strip()

    def _query(self, context: AgentContext) -> AgentResult:
        question = self._question(context)
        if not question:
            return self._result(
                context,
                ok=False,
                summary="Pergunta vazia",
                error="passe --prompt '...' ou -p q=...",
            ).done()
        k = int(context.params.get("k", 5))
        hits = self.kb.query(question, k=k)
        return self._result(
            context,
            ok=True,
            summary=f"{len(hits)} trechos relevantes",
            data={"question": question, "hits": [h.to_dict() for h in hits]},
        ).done()

    async def _ask(self, context: AgentContext) -> AgentResult:
        question = self._question(context)
        if not question:
            return self._result(context, ok=False, summary="Pergunta vazia").done()
        k = int(context.params.get("k", 5))
        hits = self.kb.query(question, k=k)
        if not hits:
            return self._result(
                context,
                ok=True,
                summary="Nenhum contexto encontrado na base",
                data={"question": question, "hits": []},
            ).done()
        if context.dry_run:
            return self._result(
                context,
                ok=True,
                summary="[dry-run] Sintetizaria resposta",
                data={"question": question, "hits": [h.to_dict() for h in hits]},
            ).done()

        context_block = "\n\n".join(f"[{h.source}]\n{h.text}" for h in hits)
        prompt = f"Pergunta: {question}\n\nContexto:\n{context_block}"
        try:
            answer = await self.runtime.run(prompt, system_prompt=SYSTEM)
        except RuntimeUnavailableError as exc:
            return self._result(
                context,
                ok=True,
                summary="Trechos recuperados (sem síntese LLM)",
                data={"question": question, "hits": [h.to_dict() for h in hits]},
                error=str(exc),
            ).done()
        return self._result(
            context,
            ok=True,
            summary="Resposta sintetizada",
            data={
                "question": question,
                "answer": answer,
                "sources": [h.source for h in hits],
                "hits": [h.to_dict() for h in hits],
            },
        ).done()


def build() -> RagAgent:
    return RagAgent()
