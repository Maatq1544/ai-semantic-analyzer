"""Structured logging via structlog."""

from __future__ import annotations

import logging
import sys

import structlog

from semantic_analyzer.config import Config


def setup_logging(config: Config | None = None, level: str | None = None) -> None:
    """Configure structlog + stdlib logging.

    Args:
        config: Optional Config object (its ``log_level`` is used).
        level: Optional explicit level override.
    """
    log_level = (level or (config.log_level if config else None) or "INFO").upper()

    # Map stdlib levels
    numeric_level = getattr(logging, log_level, logging.INFO)

    # Configure stdlib root logger
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=numeric_level,
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.dev.set_exc_info,
            structlog.processors.StackInfoRenderer(),
            (
                structlog.dev.ConsoleRenderer(colors=True)
                if sys.stderr.isatty()
                else structlog.processors.JSONRenderer()
            ),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a configured structlog logger."""
    return structlog.get_logger(name)
