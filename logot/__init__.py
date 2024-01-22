from __future__ import annotations

import logging
from collections import deque
from contextlib import AbstractContextManager
from threading import Lock
from types import TracebackType
from typing import Callable, ClassVar
from weakref import WeakValueDictionary

from logot._util import to_levelno, to_logger
from logot.logged import Logged


class Logot:
    __slots__ = ("_timeout", "_lock", "_seen_records", "_queue", "_expected_logs", "_expected_logs_waiter")

    DEFAULT_LEVEL: ClassVar[int | str] = logging.NOTSET
    DEFAULT_LOGGER: ClassVar[logging.Logger | str | None] = None
    DEFAULT_TIMEOUT: ClassVar[float] = 3.0

    def __init__(
        self,
        *,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._timeout = timeout
        self._lock = Lock()
        self._seen_records: WeakValueDictionary[int, logging.LogRecord] = WeakValueDictionary()
        self._queue: deque[logging.LogRecord] = deque()
        self._expected_logs: Logged | None = None
        self._expected_logs_waiter: Callable[[], None] | None = None

    def capturing(
        self,
        *,
        level: int | str = DEFAULT_LEVEL,
        logger: logging.Logger | str | None = DEFAULT_LOGGER,
    ) -> AbstractContextManager[Logot]:
        return _Capturing(self, levelno=to_levelno(level), logger=to_logger(logger))

    def _emit(self, record: logging.LogRecord) -> None:
        with self._lock:
            # De-duplicate log records. Duplicate log records are possible if we have multiple active captures.
            record_id = id(record)
            if record_id in self._seen_records:
                return
            self._seen_records[record_id] = record
            # If there are expected logs, reduce them.
            if self._expected_logs is not None:
                self._expected_logs = self._expected_logs._reduce(record)
                # If the expected logs have been fully reduced, notify the waiter.
                if self._expected_logs is None:
                    assert self._expected_logs_waiter is not None, "Unreachable"
                    self._expected_logs_waiter()
            # Buffer the record in the queue.
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
