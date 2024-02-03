from __future__ import annotations

from abc import ABC, abstractmethod
from threading import Lock


class AbstractWaiter(ABC):
    __slots__ = ()

    @abstractmethod
    def notify(self) -> None:
        raise NotImplementedError


class Waiter(AbstractWaiter):
    __slots__ = ()

    @abstractmethod
    def wait(self, *, timeout: float) -> None:
        raise NotImplementedError


class AsyncWaiter(AbstractWaiter):
    __slots__ = ()

    @abstractmethod
    async def wait(self, *, timeout: float) -> None:
        raise NotImplementedError


class ThreadedWaiter(Waiter):
    __slots__ = ("_lock",)

    def __init__(self) -> None:
        # Create an already-acquired lock. This will be released by `notify()`.
        self._lock = Lock()
        self._lock.acquire()

    def notify(self) -> None:
        self._lock.release()

    def wait(self, *, timeout: float) -> None:
        self._lock.acquire(timeout=timeout)
