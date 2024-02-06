from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Protocol, TypeVar

from logot._typing import TypeAlias


class AbstractWaiter(Protocol):
    @abstractmethod
    def release(self) -> None:
        raise NotImplementedError


W = TypeVar("W", bound=AbstractWaiter)


class AsyncWaiter(ABC):
    """
    Protocol used by :meth:`Logot.await_for` to pause tests until expected logs arrive.

    .. note::

        This class is for integration with :ref:`3rd-party asynchronous frameworks <index-testing-async>`. It is
        not generally used when writing tests.
    """

    __slots__ = ()

    @abstractmethod
    def release(self) -> None:
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


AsyncWaiterFactory: TypeAlias = Callable[[], AsyncWaiter]
