from __future__ import annotations

import logging
from collections import deque
from contextlib import AbstractContextManager
from threading import Lock
from types import TracebackType
from typing import Any, Callable, ClassVar, Generic

from logot._asyncio import AsyncioWaiter
from logot._capture import Captured
from logot._logged import Logged
from logot._validate import validate_level, validate_logger, validate_timeout
from logot._wait import AsyncWaiter, W, create_threading_waiter


class Logot:
    """
    The main :mod:`logot` API for capturing and waiting for logs.

    .. seealso::

        See :doc:`/index` usage guide.

    :param timeout: See :attr:`Logot.timeout`.
    :param async_waiter: See :attr:`Logot.async_waiter`.
    """

    __slots__ = ("timeout", "async_waiter", "_lock", "_queue", "_wait")

    DEFAULT_LEVEL: ClassVar[str | int] = "DEBUG"
    """
    The default ``level`` used by :meth:`capturing`.
    """

    DEFAULT_LOGGER: ClassVar[str | None] = None
    """
    The default ``logger`` used by :meth:`capturing`.

    This is the root logger.
    """

    DEFAULT_TIMEOUT: ClassVar[float] = 3.0
    """
    The default ``timeout`` (in seconds) for new :class:`Logot` instances.
    """

    DEFAULT_ASYNC_WAITER: ClassVar[Callable[[], AsyncWaiter]] = AsyncioWaiter
    """
    The default ``async_waiter`` for new :class:`Logot` instances.
    """

    timeout: float
    """
    The default ``timeout`` (in seconds) for calls to :meth:`wait_for` and :meth:`await_for`.

    Defaults to :attr:`Logot.DEFAULT_TIMEOUT`.
    """

    async_waiter: Callable[[], AsyncWaiter]
    """
    The default ``async_waiter`` for calls to :meth:`await_for`.

    Defaults to :attr:`Logot.DEFAULT_ASYNC_WAITER`.
    """

    def __init__(
        self,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        async_waiter: Callable[[], AsyncWaiter] = DEFAULT_ASYNC_WAITER,
    ) -> None:
        self.timeout = validate_timeout(timeout)
        self.async_waiter = async_waiter
        self._lock = Lock()
        self._queue: deque[Captured] = deque()
        self._wait: _Wait[Any] | None = None

    def capturing(
        self,
        *,
        level: str | int = DEFAULT_LEVEL,
        logger: logging.Logger | str | None = DEFAULT_LOGGER,
    ) -> AbstractContextManager[Logot]:
        """
        Captures logs emitted at the given ``level`` by the given ``logger`` for the duration of the context.

        If the given ``logger`` level is less verbose than the requested ``level``, it will be temporarily adjusted to
        the requested ``level`` for the duration of the context.

        .. seealso::

            See :doc:`/log-capturing` usage guide.

        :param level: A log level name (e.g. ``"DEBUG"``) or numeric level (e.g. :data:`logging.DEBUG`). Defaults to
            :attr:`Logot.DEFAULT_LEVEL`.
        :param logger: A logger or logger name to capture logs from. Defaults to :attr:`Logot.DEFAULT_LOGGER`.
        """
        level = validate_level(level)
        logger = validate_logger(logger)
        return _Capturing(self, _Handler(level, self), logger=logger)

    def capture(self, captured: Captured) -> None:
        """
        Adds the given captured log record to the internal capture queue.

        Any waiters blocked on :meth:`wait_for` to :meth:`await_for` will be notified and wake up if their
        :doc:`log pattern </log-pattern-matching>` is satisfied.

        .. note::

            This method is for integration with :ref:`3rd-party logging frameworks <log-capturing-3rd-party>`. It is not
            generally used when writing tests.

        .. seealso::

            See :ref:`log-capturing-3rd-party` usage guide.

        :param captured: The captured log.
        """
        with self._lock:
            # If there is a waiter that has not been fully reduced, attempt to reduce it.
            if self._wait is not None and self._wait.logged is not None:
                self._wait.logged = self._wait.logged._reduce(captured)
                # If the waiter has fully reduced, notify the blocked caller.
                if self._wait.logged is None:
                    self._wait.waiter.release()
                return
            # Otherwise, buffer the captured log.
            self._queue.append(captured)

    def assert_logged(self, logged: Logged) -> None:
        """
        Fails *immediately* if the expected ``log`` pattern has not arrived.

        :param logged: The expected :doc:`log pattern </log-pattern-matching>`.
        :raises AssertionError: If the expected ``log`` pattern has not arrived.
        """
        reduced = self._reduce(logged)
        if reduced is not None:
            raise AssertionError(f"Not logged:\n\n{reduced}")

    def assert_not_logged(self, logged: Logged) -> None:
        """
        Fails *immediately* if the expected ``log`` pattern **has** arrived.

        :param logged: The expected :doc:`log pattern </log-pattern-matching>`.
        :raises AssertionError: If the expected ``log`` pattern **has** arrived.
        """
        reduced = self._reduce(logged)
        if reduced is None:
            raise AssertionError(f"Logged:\n\n{logged}")

    def wait_for(
        self,
        logged: Logged,
        *,
        timeout: float | None = None,
    ) -> None:
        """
        Waits for the expected ``log`` pattern to arrive or the ``timeout`` to expire.

        :param logged: The expected :doc:`log pattern </log-pattern-matching>`.
        :param timeout: How long to wait (in seconds) before failing the test. Defaults to :attr:`Logot.timeout`.
        :raises AssertionError: If the expected ``log`` pattern does not arrive within ``timeout`` seconds.
        """
        waiter = self._start_waiting(logged, create_threading_waiter, timeout=timeout)
        if waiter is None:
            return
        try:
            waiter.waiter.acquire(timeout=waiter.timeout)
        finally:
            self._stop_waiting(waiter)

    async def await_for(
        self,
        logged: Logged,
        *,
        timeout: float | None = None,
        async_waiter: Callable[[], AsyncWaiter] | None = None,
    ) -> None:
        """
        Waits *asynchronously* for the expected ``log`` pattern to arrive or the ``timeout`` to expire.

        :param logged: The expected :doc:`log pattern </log-pattern-matching>`.
        :param timeout: How long to wait (in seconds) before failing the test. Defaults to :attr:`Logot.timeout`.
        :param async_waiter: Protocol used to pause tests until expected logs arrive. Defaults to
            :attr:`Logot.DEFAULT_ASYNC_WAITER`.
        :raises AssertionError: If the expected ``log`` pattern does not arrive within ``timeout`` seconds.
        """
        if async_waiter is None:
            async_waiter = self.async_waiter
        waiter = self._start_waiting(logged, async_waiter, timeout=timeout)
        if waiter is None:
            return
        try:
            await waiter.waiter.wait(timeout=waiter.timeout)
        finally:
            self._stop_waiting(waiter)

    def clear(self) -> None:
        """
        Clears any captured logs.
        """
        self._queue.clear()

    def _start_waiting(
        self, logged: Logged | None, waiter: Callable[[], W], *, timeout: float | None
    ) -> _Wait[W] | None:
        with self._lock:
            # If no timeout is provided, use the default timeout.
            # Otherwise, validate and use the provided timeout.
            if timeout is None:
                timeout = self.timeout
            else:
                timeout = validate_timeout(timeout)
            # Ensure no other waiters.
            if self._wait is not None:  # pragma: no cover
                raise RuntimeError("Multiple concurrent waiters are not supported")
            # Apply an immediate reduction.
            logged = self._reduce(logged)
            if logged is None:
                return None
            # All done!
            wait = self._wait = _Wait(logged=logged, timeout=timeout, waiter=waiter())
            return wait

    def _stop_waiting(self, waiter: _Wait[Any]) -> None:
        with self._lock:
            # Clear the waiter.
            self._wait = None
            # Error if the waiter logs are not fully reduced.
            if waiter.logged is not None:
                raise AssertionError(f"Not logged:\n\n{waiter.logged}")

    def _reduce(self, logged: Logged | None) -> Logged | None:
        # Drain the queue until the log is fully reduced.
        # This does not need a lock, since `deque.popleft()` is thread-safe.
        while logged is not None:
            try:
                captured = self._queue.popleft()
            except IndexError:
                break
            logged = logged._reduce(captured)
        # All done!
        return logged

    def __repr__(self) -> str:
        return f"Logot(timeout={self.timeout!r})"


class _Capturing:
    __slots__ = ("_logot", "_handler", "_logger", "_prev_levelno")

    def __init__(self, logot: Logot, handler: logging.Handler, *, logger: logging.Logger) -> None:
        self._logot = logot
        self._handler = handler
        self._logger = logger

    def __enter__(self) -> Logot:
        # If the logger is less verbose than the handler, force it to the necessary verboseness.
        self._prev_levelno = self._logger.level
        if self._handler.level < self._logger.level:
            self._logger.setLevel(self._handler.level)
        # Add the handler.
        self._logger.addHandler(self._handler)
        return self._logot

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        # Remove the handler.
        self._logger.removeHandler(self._handler)
        # Restore the previous level.
        self._logger.setLevel(self._prev_levelno)


class _Handler(logging.Handler):
    __slots__ = ("_logot",)

    def __init__(self, level: str | int, logot: Logot) -> None:
        super().__init__(level)
        self._logot = logot

    def emit(self, record: logging.LogRecord) -> None:
        captured = Captured(record.levelname, record.getMessage(), levelno=record.levelno)
        self._logot.capture(captured)


class _Wait(Generic[W]):
    __slots__ = ("logged", "timeout", "waiter")

    def __init__(self, *, logged: Logged | None, timeout: float, waiter: W) -> None:
        self.logged = logged
        self.timeout = timeout
        self.waiter = waiter
