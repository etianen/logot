from __future__ import annotations

from functools import partial

import loguru
from loguru import logger

from logot._capture import Captured
from logot._logot import Capturer, Logot
from logot._typing import Level, Name


class LoguruCapturer(Capturer):
    """
    A :class:`logot.Capturer` implementation for :mod:`loguru`.
    """

    __slots__ = ("_handler_id",)

    def start_capturing(self, logot: Logot, /, *, level: Level, name: Name) -> None:
        self._handler_id = logger.add(partial(_sink, logot=logot), level=level, filter=name)

    def stop_capturing(self) -> None:
        logger.remove(self._handler_id)


def _sink(msg: loguru.Message, *, logot: Logot) -> None:
    record = msg.record
    level = record["level"]
    logot.capture(Captured(level.name, record["message"], levelno=level.no, name=record["name"]))
