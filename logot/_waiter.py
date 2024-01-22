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


class WaitError(Exception):
    pass


class LoggedWaiter(ABC):
    __slots__ = ("_parent", "log", "_timeout")

    def __init__(self, parent: Waiter, log: Logged, *, timeout: float) -> None:
        self._parent = parent
        self.log: Logged | None = log
        self._timeout = timeout

    def append(self, record: logging.LogRecord) -> None:
        # If the log has already been fully-reduced, but the waiter is not yet cleaned up, add the record to the parent
        # waiter. The avoids any race condition that could lose log records.
        if self.log is None:
            self._parent.append(record)
            return
        # Reduce the log.
        self.log = self.log._reduce(record)
        # Handle full reduction.
        if self.log is None:
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

    def wait(self) -> None:
        if not self._lock.acquire(timeout=self._timeout):
            raise WaitError


class AsyncLoggedWaiter(LoggedWaiter):
    __slots__ = ("_loop", "_future")

    def __init__(self, parent: Waiter, log: Logged, *, timeout: float) -> None:
        super().__init__(parent, log, timeout=timeout)
        self._loop = asyncio.get_running_loop()
        self._future: asyncio.Future[None] = self._loop.create_future()

    def _notify(self) -> None:
        self._loop.call_soon_threadsafe(self._anotify)

    def _anotify(self) -> None:
        try:
            self._future.set_result(None)
        except asyncio.InvalidStateError:
            # The future might have been cancelled by a failed timeout, so ignore this error.
            pass

    async def wait(self) -> None:
        try:
            await asyncio.wait_for(self._future, timeout=self._timeout)
        except asyncio.TimeoutError:
            raise WaitError from None
