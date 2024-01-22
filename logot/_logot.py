from __future__ import annotations

import logging
from collections import deque
from contextlib import AbstractContextManager
from threading import Lock
from types import TracebackType
from typing import ClassVar, Generic, TypeVar
from weakref import WeakValueDictionary

from logot._logged import Logged
from logot._util import to_levelno, to_logger, to_timeout
from logot._waiter import AsyncLoggedWaiter, LoggedWaiter, SyncLoggedWaiter, Waiter, WaitError

W = TypeVar("W", bound=LoggedWaiter)


class Logot:
    __slots__ = ("_timeout", "_lock", "_seen_records", "_waiter")

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
        self._waiter: Waiter = deque()

    def capturing(
        self,
        *,
        level: int | str = DEFAULT_LEVEL,
        logger: logging.Logger | str | None = DEFAULT_LOGGER,
    ) -> AbstractContextManager[Logot]:
        return _Capturing(self, levelno=to_levelno(level), logger=to_logger(logger))

    def _waiting(self, waiter_cls: type[W], log: Logged, *, timeout: float | None) -> AbstractContextManager[W | None]:
        return _Waiting(self, waiter_cls, log, timeout=timeout)

    def _emit(self, record: logging.LogRecord) -> None:
        with self._lock:
            # De-duplicate log records.
            # Duplicate log records are possible if we have multiple active captures.
            record_id = id(record)
            if record_id in self._seen_records:
                return
            self._seen_records[record_id] = record
            # Append the log to the waiter.
            self._waiter.append(record)

    def _reduce(self, log: Logged | None) -> Logged | None:
        assert self._lock.locked()
        # Ensure no other waiters.
        if not isinstance(self._waiter, deque):
            raise RuntimeError("Multiple waiters are not supported")
        # Drain the waiter until the log is fully reduced.
        while self._waiter and log is not None:
            log = log._reduce(self._waiter.popleft())
        # All done!
        return log

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
        with self._waiting(SyncLoggedWaiter, log, timeout=timeout) as waiter:
            if waiter is not None:
                waiter.wait()

    async def await_for(self, log: Logged, *, timeout: float | None = None) -> None:
        with self._waiting(AsyncLoggedWaiter, log, timeout=timeout) as waiter:
            if waiter is not None:
                await waiter.wait()


class _Capturing:
    __slots__ = ("_logot", "_logger", "_handler", "_prev_levelno")

    def __init__(self, logot: Logot, *, levelno: int, logger: logging.Logger) -> None:
        self._logot = logot
        self._logger = logger
        self._handler = _Handler(logot, levelno=levelno)

    def __enter__(self) -> Logot:
        self._prev_levelno = self._logger.level
        # If the logger is less verbose than the handler, force it to the necessary verboseness.
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
        # Restore the previous level.
        self._logger.setLevel(self._prev_levelno)


class _Waiting(Generic[W]):
    __slots__ = ("_logot", "_waiter_cls", "_log", "_timeout", "_prev_waiter", "_waiter")

    def __init__(self, logot: Logot, waiter_cls: type[W], log: Logged, *, timeout: float | None = None) -> None:
        self._logot = logot
        self._waiter_cls = waiter_cls
        self._log = log
        # If no timeout is provided, use the default timeout.
        # Otherwise, validate and use the provided timeout.
        if timeout is None:
            self._timeout = logot._timeout
        else:
            self._timeout = to_timeout(timeout)

    def __enter__(self) -> W | None:
        with self._logot._lock:
            self._prev_waiter = self._logot._waiter
            # Exit early if we're already reduced.
            reduced_log = self._logot._reduce(self._log)
            if reduced_log is None:
                return None
            # Set a waiter.
            self._waiter = self._logot._waiter = self._waiter_cls(
                self._logot._waiter,
                reduced_log,
                timeout=self._timeout,
            )
            return self._waiter

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        with self._logot._lock:
            # Restore the previous waiter.
            self._logot._waiter = self._prev_waiter
            # If the waiter failed, avoid a race condition by trying one last time with the lock.
            if exc_type is not None and issubclass(exc_type, WaitError):
                if self._waiter.log is not None:
                    raise AssertionError(f"Not logged:\n\n{self._waiter.log}")


class _Handler(logging.Handler):
    __slots__ = ("_logot",)

    def __init__(self, logot: Logot, *, levelno: int) -> None:
        super().__init__(levelno)
        self._logot = logot

    def emit(self, record: logging.LogRecord) -> None:
        self._logot._emit(record)
