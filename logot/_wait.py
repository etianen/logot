from __future__ import annotations

from _thread import LockType, allocate_lock
from abc import ABC, abstractmethod
from typing import Protocol, TypeVar


class Waiter(Protocol):
    @abstractmethod
    def release(self) -> None:
        raise NotImplementedError


W = TypeVar("W", bound=Waiter)


def create_threading_waiter() -> LockType:
    # Create an already-acquired lock. This will be released by `release()`.
    lock = allocate_lock()
    lock.acquire()
    return lock


class AsyncWaiter(ABC):
    """
    Protocol used by :meth:`Logot.await_for` to pause tests until expected logs arrive.

    .. note::

        This class is for integration with :ref:`3rd-party asynchronous frameworks <integrations-async>`. It is not
        generally used when writing tests.
    """

    __slots__ = ()

    @abstractmethod
    def release(self) -> None:
        """
        Releases the test waiting on :meth:`wait`, allowing it to resume immediately.
        """
        raise NotImplementedError

    @abstractmethod
    async def wait(self, *, timeout: float) -> None:
        """
        Waits *asynchronously* for :meth:`release` to be called or the ``timeout`` to expire.

        :param timeout: How long to wait (in seconds) before resuming.
        """
        raise NotImplementedError
