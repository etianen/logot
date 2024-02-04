from __future__ import annotations

from abc import ABC, abstractmethod
from threading import Lock

from logot._logged import Logged


class AbstractWaiter(ABC):
    __slots__ = ("_logged", "_timeout")

    # This protected attr is populated by `Logot._start_waiting`.
    _logged: Logged | None

    @abstractmethod
    def notify(self) -> None:
        raise NotImplementedError


class Waiter(AbstractWaiter):
    """
    Protocol used by :meth:`Logot.wait_for` to pause tests until expected logs arrive.

    .. note::

        This class is for integration with :ref:`3rd-party threading frameworks <index-testing-threaded>`. It is
        not generally used when writing tests.
    """

    __slots__ = ()

    @abstractmethod
    def notify(self) -> None:
        """
        Notifies the test waiting on :meth:`wait` to resume immediately.
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
    """
    Protocol used by :meth:`Logot.await_for` to pause tests until expected logs arrive.

    .. note::

        This class is for integration with :ref:`3rd-party asynchronous frameworks <index-testing-async>`. It is
        not generally used when writing tests.
    """

    __slots__ = ()

    @abstractmethod
    def notify(self) -> None:
        """
        Notifies the test waiting on :meth:`wait` to resume immediately.
        """
        raise NotImplementedError

    @abstractmethod
    async def wait(self, *, timeout: float) -> None:
        """
        Waits *asynchronously* for :meth:`notify` to be called or the ``timeout`` to expire.

        :param timeout: How long to wait (in seconds) before resuming.
        """
        raise NotImplementedError


class ThreadingWaiter(Waiter):
    """
    A :class:`logot.Waiter` implementation for :mod:`threading`.

    .. note::

        This is the default :class:`logot.Waiter` implementation for :mod:`logot`.
    """

    __slots__ = ("_lock",)

    def __init__(self) -> None:
        # Create an already-acquired lock. This will be released by `notify()`.
        self._lock = Lock()
        self._lock.acquire()

    def notify(self) -> None:
        self._lock.release()

    def wait(self, *, timeout: float) -> None:
        self._lock.acquire(timeout=timeout)
