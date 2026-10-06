"""Permite `python -m forja.mcp_server` para subir o servidor MCP (stdio)."""

from __future__ import annotations

import sys

from forja.config import get_settings
from forja.logging_conf import configure_logging
from forja.mcp_server.server import run


def main() -> None:
    # stdout é o canal do protocolo MCP: logs vão para stderr.
    configure_logging(get_settings().log_level, stream=sys.stderr)
    run("stdio")


if __name__ == "__main__":
    main()
