from __future__ import annotations

from abc import ABC, abstractmethod
from threading import Event

from logot._logged import Logged


class AbstractWaiter(ABC):
    __slots__ = ("_logged", "_timeout")

    # This protected attr is populated by `Logot._start_waiting`.
    _logged: Logged | None

    @abstractmethod
    def notify(self) -> None:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class Waiter(AbstractWaiter):
    """
    The protocol used by :meth:`Logot.wait_for` to pause tests until expected logs arrive.
    """

    __slots__ = ()

    @abstractmethod
    def notify(self) -> None:
        """
        Notifies the test waiting on :meth:`Waiter.wait` to resume immediately.
        """
        raise NotImplementedError

    @abstractmethod
    def wait(self, *, timeout: float) -> None:
        """
        Waits for :meth:`Waiter.notify` to be called or the ``timeout`` to expire.

        :param timeout: How long to wait (in seconds) before resuming.
        """
        raise NotImplementedError


class AsyncWaiter(AbstractWaiter):
    """
    The protocol used by :meth:`Logot.await_for` to pause tests until expected logs arrive.
    """

    __slots__ = ()

    @abstractmethod
    def notify(self) -> None:
        """
        Notifies the test waiting on :meth:`AsyncWaiter.wait` to resume immediately.
        """
        raise NotImplementedError

    @abstractmethod
    async def wait(self, *, timeout: float) -> None:
        """
        Waits *asynchronously* for :meth:`AsyncWaiter.notify` to be called or the ``timeout`` to expire.

        :param timeout: How long to wait (in seconds) before resuming.
        """
        raise NotImplementedError


class ThreadedWaiter(Waiter):
    __slots__ = ("_event",)

    def __init__(self) -> None:
        self._event = Event()

    def notify(self) -> None:
        self._event.set()

    def wait(self, *, timeout: float) -> None:
        self._event.wait(timeout=timeout)
