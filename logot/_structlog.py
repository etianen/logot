from __future__ import annotations

from functools import partial

import structlog
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

    __slots__ = ("_old_processors", "_old_wrapper_class")

    def start_capturing(self, logot: Logot, /, *, level: Level, name: Name) -> None:
        config = structlog.get_config()
        processors = config["processors"]
        wrapper_class = config["wrapper_class"]
        self._old_processors = processors.copy()
        self._old_wrapper_class = wrapper_class
        processors.clear()
        processors.append(partial(_processor, logot=logot, name=name))

        if level is not None:
            if isinstance(level, str):
                levelno = NAME_TO_LEVEL[level.lower()]
                wrapper_class = structlog.make_filtering_bound_logger(levelno)

        structlog.configure(processors=processors, wrapper_class=wrapper_class)

    def stop_capturing(self) -> None:
        processors = structlog.get_config()["processors"]
        processors.clear()
        processors.extend(self._old_processors)
        structlog.configure(processors=processors, wrapper_class=self._old_wrapper_class)


def _processor(logger: WrappedLogger, method_name: str, event_dict: EventDict, *, logot: Logot, name: Name) -> None:
    msg = event_dict["event"]
    level = method_name.upper()
    levelno = NAME_TO_LEVEL[method_name]

    if name is None or logger.name == name:
        logot.capture(Captured(level, msg, levelno=levelno))

    raise DropEvent
