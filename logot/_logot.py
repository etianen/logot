from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections import deque
from contextlib import AbstractContextManager
from threading import Lock
from types import TracebackType
from typing import TYPE_CHECKING, Callable, ClassVar, TypeVar, overload

from logot._captured import Captured
from logot._logged import Logged
from logot._validate import validate_levelno, validate_logger, validate_timeout
from logot._waiter import AsyncWaiter, SyncWaiter, Waiter

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    P = ParamSpec("P")
    W = TypeVar("W", bound=Waiter)


class Logot:
    """
    The main :mod:`logot` API for capturing and waiting for logs.

    .. seealso::

        See :doc:`index` usage guide.

    :param timeout: The default timeout (in seconds) for calls to :meth:`wait_for` and :meth:`await_for`. Defaults to
        :attr:`DEFAULT_TIMEOUT`.
    """

    __slots__ = ("_timeout", "_lock", "_queue", "_waiter")

    DEFAULT_TIMEOUT: ClassVar[float] = 3.0
    """
    The default ``timeout`` used by :meth:`wait_for` and :meth:`await_for`.

    This is 3 seconds.
    """

    def __init__(
        self,
        *,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._timeout = validate_timeout(timeout)
        self._lock = Lock()
        self._queue: deque[Captured] = deque()
        self._waiter: Waiter | None = None

    @overload
    def capturing(
        self,
        capture_cls: Callable[P, Capture],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AbstractContextManager[Logot]:
        ...

    @overload
    def capturing(
        self,
        *,
        level: int | str = ...,
        logger: logging.Logger | str | None = ...,
    ) -> AbstractContextManager[Logot]:
        ...

    def capturing(
        self,
        capture_cls: Callable[P, Capture] | None = None,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> AbstractContextManager[Logot]:
        """
        Captures logs emitted at the given ``level`` by the given ``logger`` for the duration of the context.

        If the given ``logger`` level is less verbose than the requested ``level``, it will be temporarily adjusted to
        the requested ``level`` for the duration of the context.

        :param level: A log level (e.g. :data:`logging.DEBUG`) or string name (e.g. ``"DEBUG"``). Defaults to
            :data:`logging.NOTSET`, specifying that all logs are captured.
        :param logger: A logger or logger name to capture logs from. Defaults to the root logger.
        """
        if capture_cls is None:
            capture: Capture = LoggingCapture(*args, **kwargs)  # type: ignore[arg-type]
        else:
            capture = capture_cls(*args, **kwargs)
        return _Capturing(self, capture)

    def wait_for(self, logged: Logged, *, timeout: float | None = None) -> None:
        """
        Waits for the expected ``log`` pattern to arrive or the ``timeout`` to expire.

        :param logged: The expected :doc:`log pattern <logged>`.
        :param timeout: How long to wait (in seconds) before failing the test. Defaults to the ``timeout`` passed to
            :class:`Logot`.
        :raises AssertionError: If the expected ``log`` pattern does not arrive within ``timeout`` seconds.
        """
        waiter = self._start_waiter(logged, SyncWaiter, timeout=timeout)
        try:
            waiter.wait()
        finally:
            self._stop_waiter(waiter)

    async def await_for(self, logged: Logged, *, timeout: float | None = None) -> None:
        """
        Waits *asynchronously* for the expected ``log`` pattern to arrive or the ``timeout`` to expire.

        :param logged: The expected :doc:`log pattern <logged>`.
        :param timeout: How long to wait (in seconds) before failing the test. Defaults to the ``timeout`` passed to
            :class:`Logot`.
        :raises AssertionError: If the expected ``log`` pattern does not arrive within ``timeout`` seconds.
        """
        waiter = self._start_waiter(logged, AsyncWaiter, timeout=timeout)
        try:
            await waiter.wait()
        finally:
            self._stop_waiter(waiter)

    def assert_logged(self, logged: Logged) -> None:
        """
        Fails *immediately* if the expected ``log`` pattern has not arrived.

        :param logged: The expected :doc:`log pattern <logged>`.
        :raises AssertionError: If the expected ``log`` pattern has not arrived.
        """
        reduced = self._reduce(logged)
        if reduced is not None:
            raise AssertionError(f"Not logged:\n\n{reduced}")

    def assert_not_logged(self, logged: Logged) -> None:
        """
        Fails *immediately* if the expected ``log`` pattern **has** arrived.

        :param logged: The expected :doc:`log pattern <logged>`.
        :raises AssertionError: If the expected ``log`` pattern **has** arrived.
        """
        reduced = self._reduce(logged)
        if reduced is None:
            raise AssertionError(f"Logged:\n\n{logged}")

    def clear(self) -> None:
        """
        Clears any captured logs.
        """
        with self._lock:
            self._queue.clear()

    def _capture(self, captured: Captured) -> None:
        with self._lock:
            # If there is a waiter that has not been fully reduced, attempt to reduce it.
            if self._waiter is not None and self._waiter.logged is not None:
                self._waiter.logged = self._waiter.logged._reduce(captured)
                # If the waiter has fully reduced, notify the blocked caller.
                if self._waiter.logged is None:
                    self._waiter.notify()
                return
            # Otherwise, buffer the capture.
            self._queue.append(captured)

    def _start_waiter(self, logged: Logged, waiter_cls: type[W], *, timeout: float | None) -> W:
        with self._lock:
            # If no timeout is provided, use the default timeout.
            # Otherwise, validate and use the provided timeout.
            if timeout is None:
                timeout = self._timeout
            else:
                timeout = validate_timeout(timeout)
            # Ensure no other waiters.
            if self._waiter is not None:  # pragma: no cover
                raise RuntimeError("Multiple waiters are not supported")
            # Set a waiter.
            waiter = self._waiter = waiter_cls(logged, timeout=timeout)
            # Apply an immediate reduction.
            waiter.logged = self._reduce(waiter.logged)
            if waiter.logged is None:
                waiter.notify()
            # All done!
            return waiter

    def _stop_waiter(self, waiter: Waiter) -> None:
        with self._lock:
            # Clear the waiter.
            self._waiter = None
            # Error if the waiter logged is not fully reduced.
            if waiter.logged is not None:
                raise AssertionError(f"Not logged:\n\n{waiter.logged}")

    def _reduce(self, logged: Logged | None) -> Logged | None:
        # Drain the queue until the logged is fully reduced.
        # This does not need a lock, since `deque.popleft()` is thread-safe.
        while logged is not None:
            try:
                captured = self._queue.popleft()
            except IndexError:
                break
            logged = logged._reduce(captured)
        # All done!
        return logged


class Capture(ABC):
    __slots__ = ("_logot",)

    _logot: Logot

    @property
    def is_capturing(self) -> bool:
        return hasattr(self, "_logot")

    def capture(self, captured: Captured) -> None:
        if not self.is_capturing:
            raise RuntimeError(f"{self!r}: Not capturing")
        # Delegate to the capture impl.
        self._logot._capture(captured)

    @abstractmethod
    def start_capturing(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop_capturing(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError


class LoggingCapture(Capture):
    __slots__ = ("_handler", "_logger", "_prev_levelno")

    def __init__(
        self,
        *,
        level: int | str = logging.NOTSET,
        logger: logging.Logger | str | None = None,
    ) -> None:
        self._handler = _Handler(self, levelno=validate_levelno(level))
        self._logger = validate_logger(logger)

    def start_capturing(self) -> None:
        # If the logger is less verbose than the handler, force it to the necessary verboseness.
        self._prev_levelno = self._logger.level
        if self._handler.level < self._logger.level:
            self._logger.setLevel(self._handler.level)
        # Add the handler.
        self._logger.addHandler(self._handler)

    def stop_capturing(self) -> None:
        # Remove the handler.
        self._logger.removeHandler(self._handler)
        # Restore the previous level.
        self._logger.setLevel(self._prev_levelno)

    def __repr__(self) -> str:
        return f"LoggingCapture(level={logging.getLevelName(self._handler.level)!r}, logger={self._logger.name!r})"


class _Capturing:
    __slots__ = ("_logot", "_capture")

    def __init__(self, logot: Logot, capture: Capture) -> None:
        self._logot = logot
        self._capture = capture

    def __enter__(self) -> Logot:
        if self._capture.is_capturing:
            raise RuntimeError(f"{self!r}: Already capturing")
        self._capture._logot = self._logot
        self._capture.start_capturing()
        return self._logot

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if not self._capture.is_capturing:
            raise RuntimeError(f"{self!r}: Not capturing")
        self._capture.stop_capturing()
        del self._capture._logot


class _Handler(logging.Handler):
    __slots__ = ("_capture",)

    def __init__(self, capture: LoggingCapture, *, levelno: int) -> None:
        super().__init__(levelno)
        self._capture = capture

    def emit(self, record: logging.LogRecord) -> None:
        self._capture.capture(Captured(record.levelno, record.getMessage()))
