from pathlib import Path

from workg.agents.rag.agent import RagAgent
from workg.config import Settings
from workg.orchestrator.base import AgentContext
from workg.rag.embeddings import HashingEmbedder
from workg.rag.pipeline import KnowledgeBase, chunk_text


def test_chunk_text():
    assert chunk_text("") == []
    assert chunk_text("curto") == ["curto"]
    chunks = chunk_text("x" * 2000, size=900, overlap=150)
    assert len(chunks) >= 2
    assert all(len(c) <= 900 for c in chunks)


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        _env_file=None,
        knowledge_base_path=tmp_path / "kb",
        chroma_path=tmp_path / ".chroma",
        vector_store="chroma",  # cairá para in-memory se chromadb ausente
    )


def _kb(tmp_path: Path) -> KnowledgeBase:
    return KnowledgeBase(settings=_settings(tmp_path), embedder=HashingEmbedder())


def _seed(tmp_path: Path):
    kb_dir = tmp_path / "kb" / "chamados"
    kb_dir.mkdir(parents=True)
    (kb_dir / "timeout.md").write_text(
        "# Timeout no serviço de pagamentos\n"
        "Resolvemos aumentando o pool de conexões e o timeout do cliente HTTP.\n",
        encoding="utf-8",
    )
    (kb_dir / "rollback.md").write_text(
        "# Runbook de rollback\nPassos: parar deploy, reverter tag, validar health.\n",
        encoding="utf-8",
    )


def test_reindex_and_query(tmp_path: Path):
    _seed(tmp_path)
    kb = _kb(tmp_path)
    stats = kb.reindex()
    assert stats["documents"] == 2
    assert stats["chunks"] >= 2
    assert kb.count() >= 2
    hits = kb.query("timeout pagamentos pool de conexões", k=3)
    assert hits
    assert hits[0].source.endswith("timeout.md")


async def test_agent_query_action(tmp_path: Path):
    _seed(tmp_path)
    kb = _kb(tmp_path)
    kb.reindex()
    agent = RagAgent(settings=_settings(tmp_path), kb=kb)
    result = await agent.run(AgentContext(action="query", prompt="rollback health validar"))
    assert result.ok
    assert result.data["hits"]
    assert any("rollback" in h["source"] for h in result.data["hits"])


async def test_agent_query_empty_question(tmp_path: Path):
    agent = RagAgent(settings=_settings(tmp_path), kb=_kb(tmp_path))
    result = await agent.run(AgentContext(action="query"))
    assert not result.ok
