from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from threading import Lock

from logot._logged import Logged


class Waiter(ABC):
    __slots__ = ("log", "_timeout")

    def __init__(self, log: Logged, *, timeout: float) -> None:
        self.log: Logged | None = log
        self._timeout = timeout

    @abstractmethod
    def notify(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def wait(self) -> object:
        raise NotImplementedError


class SyncWaiter(Waiter):
    __slots__ = ("_lock",)

    def __init__(self, log: Logged, *, timeout: float) -> None:
        super().__init__(log, timeout=timeout)
        # Create an already-acquired lock. This will be released by `notify()`.
        self._lock = Lock()
        self._lock.acquire()

    def notify(self) -> None:
        self._lock.release()

    def wait(self) -> None:
        self._lock.acquire(timeout=self._timeout)


class AsyncWaiter(Waiter):
    __slots__ = ("_loop", "_future")

    def __init__(self, log: Logged, *, timeout: float) -> None:
        super().__init__(log, timeout=timeout)
        # Create an unresolved `asyncio.Future`. This will be resolved by `notify()`.
        self._loop = asyncio.get_running_loop()
        self._future: asyncio.Future[None] = self._loop.create_future()

    def notify(self) -> None:
        self._loop.call_soon_threadsafe(self._resolve)

    async def wait(self) -> None:
        timer = self._loop.call_later(self._timeout, self._resolve)
        try:
            await self._future
        finally:
            timer.cancel()

    def _resolve(self) -> None:
        try:
            self._future.set_result(None)
        except asyncio.InvalidStateError:  # pragma: no cover
            # It's possible that the timeout and the `notify()` will both occur in the same tick of the event loop.
            pass
