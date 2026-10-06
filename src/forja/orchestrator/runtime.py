"""Runtime de LLM baseado no Claude Agent SDK.

Encapsula a chamada ao Claude Agent SDK para que os agents não dependam
diretamente da API do SDK. Se o pacote ``claude-agent-sdk`` não estiver
instalado (extra ``agents``), a plataforma ainda sobe, mas qualquer execução
que precise do LLM lança :class:`RuntimeUnavailableError` com instruções.
"""

from __future__ import annotations

from typing import Any

from forja.config import Settings, get_settings
from forja.logging_conf import get_logger

log = get_logger("runtime")


class RuntimeUnavailableError(RuntimeError):
    """Levantada quando o runtime de LLM não pode ser usado."""


class ClaudeRuntime:
    """Fachada fina sobre o Claude Agent SDK."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def _ensure_sdk(self) -> Any:
        try:
            import claude_agent_sdk as sdk  # type: ignore
        except ImportError as exc:  # pragma: no cover - depende do ambiente
            raise RuntimeUnavailableError(
                "Claude Agent SDK não instalado. Instale o extra de agents:\n"
                '    pip install -e ".[agents]"'
            ) from exc
        return sdk

    async def run(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        allowed_tools: list[str] | None = None,
        mcp_servers: dict[str, Any] | None = None,
        model: str | None = None,
        max_turns: int = 6,
    ) -> str:
        """Executa uma consulta agentica e retorna o texto final consolidado.

        Parameters
        ----------
        prompt: instrução do usuário/agent.
        system_prompt: persona/sistema do agent.
        allowed_tools: lista de ferramentas permitidas (inclui tools de MCP).
        mcp_servers: configuração de servidores MCP (ex.: Atlassian).
        model: override do modelo; usa ``settings.llm_model`` por padrão.
        """
        sdk = self._ensure_sdk()
        options = sdk.ClaudeAgentOptions(
            system_prompt=system_prompt,
            allowed_tools=allowed_tools or [],
            mcp_servers=mcp_servers or {},
            model=model or self.settings.llm_model,
            max_turns=max_turns,
        )

        chunks: list[str] = []
        async for message in sdk.query(prompt=prompt, options=options):
            text = self._extract_text(message)
            if text:
                chunks.append(text)
        result = "\n".join(chunks).strip()
        log.debug("runtime.run.done", chars=len(result), model=options.model)
        return result

    @staticmethod
    def _extract_text(message: Any) -> str:
        """Extrai texto de uma AssistantMessage do SDK de forma defensiva."""
        content = getattr(message, "content", None)
        if content is None:
            return ""
        parts: list[str] = []
        for block in content:
            text = getattr(block, "text", None)
            if isinstance(text, str):
                parts.append(text)
        return "".join(parts)

    def available(self) -> bool:
        """True se o SDK está instalado e utilizável."""
        try:
            self._ensure_sdk()
            return True
        except RuntimeUnavailableError:
            return False
