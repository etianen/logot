from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from collections import deque
from threading import Lock
from typing import Union

from logot._logged import Logged

# A log record waiter.
# This is effectively a protocol type with one `.append(LogRecord)` method.
Waiter = Union[deque[logging.LogRecord], "_Waiter"]


class _Waiter(ABC):
    __slots__ = ("parent", "_log")

    def __init__(self, parent: Waiter, log: Logged) -> None:
        self.parent = parent
        self._log: Logged | None = log

    def append(self, record: logging.LogRecord) -> None:
        # If the log has already been fully-reduced, but not yet cleaned up, add it to the parent waiter.
        if self._log is None:
            self.parent.append(record)
            return
        # Reduce the log.
        self._log = self._log._reduce(record)
        # Handle full reduction.
        if self._log is None:
            self._notify()

    @abstractmethod
    def _notify(self) -> None:
        raise NotImplementedError


class SyncWaiter(_Waiter):
    __slots__ = ("_lock",)

    def __init__(self, parent: Waiter, log: Logged) -> None:
        super().__init__(parent, log)
        self._lock = Lock()
        self._lock.acquire()

    def _notify(self) -> None:
        self._lock.release()

    def wait(self, *, timeout: float) -> bool:
        return self._lock.acquire(timeout=timeout)


class AsyncWaiter(_Waiter):
    __slots__ = ("_loop", "_future")

    def __init__(self, parent: Waiter, log: Logged) -> None:
        super().__init__(parent, log)
        self._loop = asyncio.get_running_loop()
        self._future: asyncio.Future[None] = self._loop.create_future()

    def _notify(self) -> None:
        self._loop.call_soon_threadsafe(self._future.set_result, None)

    async def wait(self, *, timeout: float) -> bool:
        try:
            await asyncio.wait_for(self._future, timeout=timeout)
        except asyncio.TimeoutError:
            return False
        return True
