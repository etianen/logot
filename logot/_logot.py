from __future__ import annotations

import logging
from collections import deque
from contextlib import AbstractContextManager
from threading import Lock
from types import TracebackType
from typing import ClassVar, TypeVar
from weakref import WeakValueDictionary

from logot._logged import Logged
from logot._util import to_levelno, to_logger, to_timeout
from logot._waiter import AsyncioWaiter, SyncWaiter, Waiter

W = TypeVar("W", bound=Waiter)


class Logot:
    __slots__ = ("_timeout", "_lock", "_seen_records", "_queue", "_waiter")

    DEFAULT_LEVEL: ClassVar[int | str] = logging.NOTSET
    DEFAULT_LOGGER: ClassVar[logging.Logger | str | None] = None
    DEFAULT_TIMEOUT: ClassVar[float] = 3.0

    def __init__(
        self,
        *,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._timeout = to_timeout(timeout)
        self._lock = Lock()
        self._seen_records: WeakValueDictionary[int, logging.LogRecord] = WeakValueDictionary()
        self._queue: deque[logging.LogRecord] = deque()
        self._waiter: Waiter | None = None

    def capturing(
        self,
        *,
        level: int | str = DEFAULT_LEVEL,
        logger: logging.Logger | str | None = DEFAULT_LOGGER,
    ) -> AbstractContextManager[Logot]:
        return _Capturing(self, levelno=to_levelno(level), logger=to_logger(logger))

    def _emit(self, record: logging.LogRecord) -> None:
        with self._lock:
            # De-duplicate log records.
            # Duplicate log records are possible if we have multiple active captures.
            record_id = id(record)
            if record_id in self._seen_records:
                return
            self._seen_records[record_id] = record
            # If there is a waiter that has not been fully reduced, attempt to reduce it.
            if self._waiter is not None and self._waiter.log is not None:
                self._waiter.log = self._waiter.log._reduce(record)
                # If the waiter has fully reduced, notify the blocked caller.
                if self._waiter.log is None:
                    self._waiter.notify()
                return
            # Otherwise, buffer the log record.
            self._queue.append(record)

    def _reduce(self, log: Logged | None) -> Logged | None:
        assert self._lock.locked()
        # Ensure no other waiters.
        if self._waiter is not None:
            raise RuntimeError("Multiple waiters are not supported")
        # Drain the waiter until the log is fully reduced.
        while self._waiter and log is not None:
            log = log._reduce(self._waiter.popleft())
        # All done!
        return log

    def _open_waiter(self, log: Logged, waiter_cls: type[W], *, timeout: float | None) -> W | None:
        with self._lock:
            # If no timeout is provided, use the default timeout.
            # Otherwise, validate and use the provided timeout.
            if timeout is None:
                timeout = self._timeout
            else:
                timeout = to_timeout(timeout)
            # Exit early if we're already reduced.
            reduced_log = self._reduce(log)
            if reduced_log is None:
                return None
            # Set a waiter.
            waiter = self._waiter = waiter_cls(reduced_log, timeout=timeout)
            return waiter

    def _close_waiter(self) -> None:
        with self._lock:
            # Clear the waiter.
            waiter = self._waiter
            self._waiter = None
            # Another thread might have fully-reduced the log between the wait failing and the context exiting.
            if waiter is not None and waiter.log is not None:
                raise AssertionError(f"Not logged:\n\n{waiter.log}")

    def assert_logged(self, log: Logged) -> None:
        with self._lock:
            reduced_log = self._reduce(log)
            if reduced_log is not None:
                raise AssertionError(f"Not logged:\n\n{reduced_log}")

    def assert_not_logged(self, log: Logged) -> None:
        with self._lock:
            reduced_log = self._reduce(log)
            if reduced_log is None:
                raise AssertionError(f"Logged:\n\n{log}")

    def wait_for(self, log: Logged, *, timeout: float | None = None) -> None:
        waiter = self._open_waiter(log, SyncWaiter, timeout=timeout)
        try:
            if waiter is not None:
                waiter.wait()
        finally:
            self._close_waiter()

    async def await_for(self, log: Logged, *, timeout: float | None = None) -> None:
        waiter = self._open_waiter(log, AsyncioWaiter, timeout=timeout)
        try:
            if waiter is not None:
                await waiter.wait()
        finally:
            self._close_waiter()


class _Capturing:
    __slots__ = ("_logot", "_levelno", "_logger", "_prev_levelno", "_handler")

    def __init__(self, logot: Logot, *, levelno: int, logger: logging.Logger) -> None:
        self._logot = logot
        self._levelno = levelno
        self._logger = logger

    def __enter__(self) -> Logot:
        # If the logger is less verbose than the handler, force it to the necessary verboseness.
        self._prev_levelno = self._logger.level
        if self._levelno < self._logger.level:
            self._logger.setLevel(self._levelno)
        # Add the handler.
        self._handler = _Handler(self._logot, levelno=self._levelno)
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
        # Restore the previous level.
        self._logger.setLevel(self._prev_levelno)


class _Handler(logging.Handler):
    __slots__ = ("_logot",)

    def __init__(self, logot: Logot, *, levelno: int) -> None:
        super().__init__(levelno)
        self._logot = logot

    def emit(self, record: logging.LogRecord) -> None:
        self._logot._emit(record)
