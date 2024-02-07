from __future__ import annotations

import logging
from collections.abc import Generator
from contextlib import contextmanager

from logot._capture import Captured
from logot._logot import Logot


@contextmanager
def capture_logging(
    logot: Logot,
    *,
    level: str | int = Logot.DEFAULT_LEVEL,
    logger: str | None = Logot.DEFAULT_LOGGER,
) -> Generator[None, None, None]:
    logger = logging.getLogger(logger)
    handler = _Handler(level, logot)
    # If the logger is less verbose than the handler, force it to the necessary verboseness.
    prev_levelno = logger.level
    if handler.level < logger.level:
        logger.setLevel(handler.level)
    # Add the handler.
    logger.addHandler(handler)
    try:
        yield
    finally:
        # Remove the handler and restore the previous level.
        logger.removeHandler(handler)
        logger.setLevel(prev_levelno)


class _Handler(logging.Handler):
    __slots__ = ("_logot",)

    def __init__(self, level: str | int, logot: Logot) -> None:
        super().__init__(level)
        self._logot = logot

    def emit(self, record: logging.LogRecord) -> None:
        captured = Captured(record.levelname, record.getMessage(), levelno=record.levelno)
        self._logot.capture(captured)
