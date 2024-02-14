from __future__ import annotations

from functools import partial

from structlog import configure, get_config
from structlog.exceptions import DropEvent
from structlog.processors import NAME_TO_LEVEL
from structlog.typing import EventDict, WrappedLogger

from logot._capture import Captured
from logot._logot import Capturer, Logot
from logot._typing import Level, Name


class StructlogCapturer(Capturer):
    """
    A :class:`logot.Capturer` implementation for :mod:`structlog`.
    """

    __slots__ = ("_old_processors",)

    def start_capturing(self, logot: Logot, /, *, level: Level, name: Name) -> None:
        processors = get_config()["processors"]
        self._old_processors = processors.copy()
        processors.clear()
        processors.append(partial(_processor, logot=logot))
        configure(processors=processors)

    def stop_capturing(self) -> None:
        processors = get_config()["processors"]
        processors.clear()
        processors.extend(self._old_processors)
        configure(processors=processors)


def _processor(_: WrappedLogger, method_name: str, event_dict: EventDict, *, logot: Logot) -> None:
    record = event_dict["event"]
    level = method_name
    logot.capture(Captured(level, record["message"], levelno=NAME_TO_LEVEL[level]))

    raise DropEvent
