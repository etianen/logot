from __future__ import annotations

import logging
from collections import deque
from contextlib import AbstractContextManager, ExitStack
from threading import Lock
from types import TracebackType
from typing import ClassVar

from logot._util import to_levelno, to_logger


class Logot:
    __slots__ = ("_timeout", "_stack", "_lock", "_queue")

    DEFAULT_LEVEL: ClassVar[int | str] = logging.NOTSET
    DEFAULT_LOGGER: ClassVar[logging.Logger | str | None] = None
    DEFAULT_TIMEOUT: ClassVar[float] = 3.0

    def __init__(
        self,
        *,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._timeout = timeout
        self._stack = ExitStack()
        self._lock = Lock()
        self._queue: deque[logging.LogRecord] = deque()

    def capturing(
        self,
        *,
        level: int | str = DEFAULT_LEVEL,
        logger: logging.Logger | str | None = DEFAULT_LOGGER,
    ) -> AbstractContextManager[Logot]:
        return _Capturing(self, levelno=to_levelno(level), logger=to_logger(logger))

    def capture(
        self,
        *,
        level: int | str = DEFAULT_LEVEL,
        logger: logging.Logger | str | None = DEFAULT_LOGGER,
    ) -> Logot:
        return self._stack.enter_context(self.capturing(level=level, logger=logger))

    def _emit(self, record: logging.LogRecord) -> None:
        with self._lock:
            self._queue.append(record)


class _Capturing:
    __slots__ = ("_logot", "_logger", "_handler", "_prev_levelno")

    def __init__(self, logot: Logot, *, levelno: int, logger: logging.Logger) -> None:
        self._logot = logot
        self._logger = logger
        self._handler = _Handler(logot, levelno=levelno)

    def __enter__(self) -> Logot:
        # If the logger is less verbose than the handler, force it to the necessary verboseness.
        self._prev_levelno = self._logger.level
        if self._handler.level < self._logger.level:
            self._logger.setLevel(self._handler.level)
        # Add the handler.
        self._logger.addHandler(self._handler)
        return self._logot

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        # Remove the handler.
        self._logger.removeHandler(self._handler)
        # If the logger was forced to a more verbose level, restore the previous level.
        if self._handler.level < self._prev_levelno:
            self._logger.setLevel(self._prev_levelno)


class _Handler(logging.Handler):
    __slots__ = ("_logot",)

    def __init__(self, logot: Logot, *, levelno: int) -> None:
        super().__init__(levelno)
        self._logot = logot

    def emit(self, record: logging.LogRecord) -> None:
        self._logot._emit(record)
