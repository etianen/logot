from __future__ import annotations

import sys
from functools import partial

import structlog
from structlog.processors import NAME_TO_LEVEL
from structlog.types import EventDict, WrappedLogger

from logot._capture import Captured
from logot._logot import Capturer, Logot
from logot._typing import Level, Name


class StructlogCapturer(Capturer):
    """
    A :class:`logot.Capturer` implementation for :mod:`structlog`.
    """

    __slots__ = ("_old_processors",)

    def start_capturing(self, logot: Logot, /, *, level: Level, name: Name) -> None:
        config = structlog.get_config()
        processors = config["processors"]
        self._old_processors = processors

        if isinstance(level, str):
            levelno = NAME_TO_LEVEL[level.lower()]
        else:
            levelno = level

        structlog.configure(processors=[partial(_processor, logot=logot, name=name, levelno=levelno), *processors])

    def stop_capturing(self) -> None:
        structlog.configure(processors=self._old_processors)


def _processor(
    logger: WrappedLogger, method_name: str, event_dict: EventDict, *, logot: Logot, name: Name, levelno: int
) -> EventDict:
    msg = event_dict["event"]
    level = method_name.upper()
    event_levelno = NAME_TO_LEVEL[method_name]
    logger_name = getattr(logger, "name", None)

    if (name is None or f"{logger_name}.".startswith(f"{name}.")) and event_levelno >= levelno:
        exc_info_val = event_dict.get("exc_info")
        if exc_info_val is True:
            exc_info = sys.exc_info()[1]
        elif isinstance(exc_info_val, BaseException):
            exc_info = exc_info_val
        elif isinstance(exc_info_val, tuple) and exc_info_val[1] is not None:
            exc_info = exc_info_val[1]
        else:
            exc_info = None
        logot.capture(Captured(level, msg, exc_info=exc_info, levelno=event_levelno, name=logger_name))

    return event_dict
