"""Permite `python -m workg.mcp_server` para subir o servidor MCP (stdio)."""

from __future__ import annotations

import sys

from workg.config import get_settings
from workg.logging_conf import configure_logging
from workg.mcp_server.server import run


def main() -> None:
    # stdout é o canal do protocolo MCP: logs vão para stderr.
    configure_logging(get_settings().log_level, stream=sys.stderr)
    run("stdio")


if __name__ == "__main__":
    main()
