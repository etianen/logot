from __future__ import annotations

from functools import partial

import loguru

from logot._capture import Captured
from logot._logot import Capturer, Logot
from logot._typing import Level, Logger


class LoguruCapturer(Capturer):
    """
    A :class:`logot.Capturer` implementation for :mod:`loguru`.
    """

    __slots__ = ("_handler_id",)

    def start_capturing(self, logot: Logot, /, *, level: Level, logger: Logger) -> None:
        self._handler_id = loguru.logger.add(partial(_sink, logot=logot), level=level, filter=logger)

    def stop_capturing(self) -> None:
        loguru.logger.remove(self._handler_id)


def _sink(msg: loguru.Message, *, logot: Logot) -> None:
    record = msg.record
    level = record["level"]
    logot.capture(Captured(level.name, record["message"], levelno=level.no))
