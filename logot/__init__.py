from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from collections import deque
from contextlib import AbstractContextManager
from threading import Lock
from types import TracebackType
from typing import ClassVar
from weakref import WeakValueDictionary

from logot._logged import Logged as Logged
from logot._util import to_levelno, to_logger, to_timeout


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
        self._waiter: deque[logging.LogRecord] | _Waiter = deque()

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

    def _to_timeout(self, timeout: float | None) -> float:
        # Use the default timeout.
        if timeout is None:
            return self._timeout
        # Use the provided timeout.
        return to_timeout(timeout)

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
        timeout = self._to_timeout(timeout)
        with self._lock:
            reduced_log = self._reduce(log)
            # Exit early if we're already reduced.
            if reduced_log is None:
                return
            # Set a waiter.
            waiter = self._waiter = _SyncWaiter(reduced_log)
        # Wait for the log to be fully reduced.
        if not waiter.lock.acquire(timeout=timeout):
            raise AssertionError(f"Not logged:\n\n{reduced_log}")

    async def await_for(self, log: Logged, *, timeout: float | None = None) -> None:
        timeout = self._to_timeout(timeout)
        with self._lock:
            reduced_log = self._reduce(log)
            # Exit early if we're already reduced.
            if reduced_log is None:
                return
            # Set a waiter.
            waiter = self._waiter = _AsyncWaiter(reduced_log)
        # Wait for the log to be fully reduced.
        try:
            await asyncio.wait_for(waiter.future, timeout=timeout)
        except asyncio.TimeoutError:
            raise AssertionError(f"Not logged:\n\n{reduced_log}")


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


class _Waiter(ABC):
    __slots__ = ("_log",)

    def __init__(self, log: Logged) -> None:
        self._log = log

    def append(self, record: logging.LogRecord) -> None:
        reduced_log = self._log._reduce(record)
        # Handle full reduction.
        if reduced_log is None:
            self._notify()
            return
        # Handle partial or no reduction.
        self._log = reduced_log

    @abstractmethod
    def _notify(self) -> None:
        raise NotImplementedError


class _SyncWaiter(_Waiter):
    __slots__ = ("lock",)

    def __init__(self, log: Logged) -> None:
        super().__init__(log)
        self.lock = Lock()
        self.lock.acquire()

    def _notify(self) -> None:
        self.lock.release()


class _AsyncWaiter(_Waiter):
    __slots__ = ("_loop", "future")

    def __init__(self, log: Logged) -> None:
        super().__init__(log)
        self._loop = asyncio.get_running_loop()
        self.future: asyncio.Future[None] = self._loop.create_future()

    def _notify(self) -> None:
        self._loop.call_soon_threadsafe(self.future.set_result, None)
