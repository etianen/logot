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
    The
    """

    __slots__ = ()

    @abstractmethod
    def notify(self) -> None:
        """
        Notifies the :class:`Waiter` that the test should be resumed.

        The test waiting on :meth:`wait` will resume.
        """
        raise NotImplementedError

    @abstractmethod
    def wait(self, *, timeout: float) -> None:
        """
        Waits for :meth:`notify` to be called or the ``timeout`` to expire.

        :param timeout: How long to wait (in seconds) before resuming.
        """
        raise NotImplementedError


class AsyncWaiter(AbstractWaiter):
    __slots__ = ()

    @abstractmethod
    def notify(self) -> None:
        """
        Notifies the waiter that the :doc:`log pattern </log-pattern-matching>` has been fully matched.

        The waiting test case will be resumed.
        """
        raise NotImplementedError

    @abstractmethod
    async def wait(self, *, timeout: float) -> None:
        raise NotImplementedError


class ThreadedWaiter(Waiter):
    __slots__ = ("_event",)

    def __init__(self) -> None:
        self._event = Event()

    def notify(self) -> None:
        self._event.set()

    def wait(self, *, timeout: float) -> None:
        self._event.wait(timeout=timeout)
