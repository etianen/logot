from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from threading import Lock

from logot._logged import Logged


# Error thrown when a waiter fails to be notified within the given timeout.
class WaitError(Exception):
    pass


# Abstract waiter.
# In addition to the `notify()` method, the waiter must provide a `wait()` method that throws `WaitError` if `notify()`
# is not called within `timeout` seconds.
class Waiter(ABC):
    __slots__ = ("log", "_timeout")

    def __init__(self, log: Logged, *, timeout: float) -> None:
        self.log: Logged | None = log
        self._timeout = timeout

    @abstractmethod
    def notify(self) -> None:
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
        # Wait for the lock to be released by `notify()`.
        if not self._lock.acquire(timeout=self._timeout):
            raise WaitError


class AsyncWaiter(Waiter):
    __slots__ = ()

    @abstractmethod
    async def wait(self) -> None:
        raise NotImplementedError


class AsyncioWaiter(AsyncWaiter):
    __slots__ = ("_loop", "_future")

    def __init__(self, log: Logged, *, timeout: float) -> None:
        super().__init__(log, timeout=timeout)
        # Create an unresolved `asyncio.Future`. This will be resolved by `notify()`.
        self._loop = asyncio.get_running_loop()
        self._future: asyncio.Future[None] = self._loop.create_future()

    def notify(self) -> None:
        self._loop.call_soon_threadsafe(self._anotify)

    def _anotify(self) -> None:
        try:
            self._future.set_result(None)
        except asyncio.InvalidStateError:
            # The future might have been cancelled by a failed timeout, so ignore this error.
            pass

    async def wait(self) -> None:
        # Wait for the future to be resolved by `notify()`.
        # TODO: Use `asyncio.timeout()` when we only need to support Python 3.11+.
        try:
            await asyncio.wait_for(self._future, timeout=self._timeout)
        except asyncio.TimeoutError:
            raise WaitError from None
