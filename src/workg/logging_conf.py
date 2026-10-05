"""Configuração de logging estruturado (structlog)."""

from __future__ import annotations

import logging
import sys
from typing import TextIO

import structlog


def configure_logging(level: str = "INFO", stream: TextIO | None = None) -> None:
    """Configura structlog + logging padrão com saída legível no console.

    ``stream`` controla para onde os logs vão (default: stdout). No modo MCP
    (stdio) é obrigatório usar ``sys.stderr``, pois o stdout carrega o protocolo
    JSON-RPC e qualquer log nele corromperia a comunicação.
    """
    out = stream or sys.stdout
    log_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(format="%(message)s", stream=out, level=log_level, force=True)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        logger_factory=structlog.PrintLoggerFactory(file=out),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Retorna um logger estruturado."""
    return structlog.get_logger(name)
