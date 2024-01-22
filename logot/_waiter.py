from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from collections import deque
from threading import Lock
from typing import Union

from logot._logged import Logged

# A log record waiter.
# This is effectively a protocol type with a single `append(LogRecord)` method.
Waiter = Union[deque[logging.LogRecord], "LoggedWaiter"]


class LoggedWaiter(ABC):
    __slots__ = ("_parent", "_log", "_timeout")

    def __init__(self, parent: Waiter, log: Logged, *, timeout: float) -> None:
        self._parent = parent
        self._log: Logged | None = log
        self._timeout = timeout

    def append(self, record: logging.LogRecord) -> None:
        # If the log has already been fully-reduced, but the waiter is not yet cleaned up, add the record to the parent
        # waiter. The avoids any race condition that could lose log records.
        if self._log is None:
            self._parent.append(record)
            return
        # Reduce the log.
        self._log = self._log._reduce(record)
        # Handle full reduction.
        if self._log is None:
            self._notify()

    @abstractmethod
    def _notify(self) -> None:
        raise NotImplementedError


class SyncLoggedWaiter(LoggedWaiter):
    __slots__ = ("_lock",)

    def __init__(self, parent: Waiter, log: Logged, *, timeout: float) -> None:
        super().__init__(parent, log, timeout=timeout)
        self._lock = Lock()
        self._lock.acquire()

    def _notify(self) -> None:
        self._lock.release()

    def wait(self) -> bool:
        return self._lock.acquire(timeout=self._timeout)


class AsyncLoggedWaiter(LoggedWaiter):
    __slots__ = ("_loop", "_future")

    def __init__(self, parent: Waiter, log: Logged, *, timeout: float) -> None:
        super().__init__(parent, log, timeout=timeout)
        self._loop = asyncio.get_running_loop()
        self._future: asyncio.Future[None] = self._loop.create_future()

    def _notify(self) -> None:
        self._loop.call_soon_threadsafe(self._future.set_result, None)

    async def wait(self) -> bool:
        try:
            await asyncio.wait_for(self._future, timeout=self._timeout)
        except asyncio.TimeoutError:
            return False
        return True
