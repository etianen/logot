from __future__ import annotations

import logging


def createLogRecord(
    *,
    level: int = logging.INFO,
    message: str = "Hello world",
) -> logging.LogRecord:
    return logging.LogRecord(
        name="logot",
        level=level,
        pathname=__file__,
        lineno=1,
        msg=message,
        args=(),
        exc_info=None,
    )
