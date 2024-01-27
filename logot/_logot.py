from __future__ import annotations

import logging
from collections import deque
from contextlib import AbstractContextManager
from threading import Lock
from types import TracebackType
from typing import ClassVar, TypeVar
from weakref import WeakValueDictionary

from logot._logged import Logged
from logot._validate import validate_levelno, validate_logger, validate_timeout
from logot._waiter import AsyncWaiter, SyncWaiter, Waiter

W = TypeVar("W", bound=Waiter)


class Logot:
    """
    The main :mod:`logot` API for capturing and waiting for logs.

    .. seealso::

        See :doc:`index` usage guide.

    :param timeout: The default timeout (in seconds) for calls to :meth:`wait_for` and :meth:`await_for`. Defaults to
        :attr:`DEFAULT_TIMEOUT`.
    """

    __slots__ = ("_timeout", "_lock", "_seen_records", "_queue", "_waiter")

    DEFAULT_LEVEL: ClassVar[int | str] = logging.NOTSET
    """
    The default ``level`` used by :meth:`capturing`.

    This is ``logging.NOTSET``, specifying that all logs are captured.
    """

    DEFAULT_LOGGER: ClassVar[logging.Logger | str | None] = None
    """
    The default ``logger`` used by :meth:`capturing`.

    This is the root logger.
    """

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
        self._seen_records: WeakValueDictionary[int, logging.LogRecord] = WeakValueDictionary()
        self._queue: deque[logging.LogRecord] = deque()
        self._waiter: Waiter | None = None

    def capturing(
        self,
        *,
        level: int | str = DEFAULT_LEVEL,
        logger: logging.Logger | str | None = DEFAULT_LOGGER,
    ) -> AbstractContextManager[Logot]:
        """
        Captures logs emitted at the given ``level`` by the given ``logger`` for the duration of the context.

        If the given ``logger`` level is less verbose than the requested ``level``, it will be temporarily adjusted to
        the requested ``level`` for the duration of the context.

        :param level: A log level (e.g. ``logging.DEBUG``) or string name (e.g. ``"DEBUG"``). Defaults to
            ``logging.NOTSET``, specifying that all logs are captured.
        :param logger: A logger or logger name to capture logs from. Defaults to the root logger.
        """
        levelno = validate_levelno(level)
        logger = validate_logger(logger)
        return _Capturing(self, _Handler(self, levelno=levelno), logger=logger)

    def clear(self) -> None:
        """
        Clears any captured logs.
        """
        with self._lock:
            self._queue.clear()

    def assert_logged(self, log: Logged) -> None:
        """
        Fails *immediately* if the expected ``log`` pattern has not arrived.

        :param log: The expected :doc:`log pattern <logged>`.
        :raises AssertionError: If the expected ``log`` pattern has not arrived.
        """
        reduced_log = self._reduce(log)
        if reduced_log is not None:
            raise AssertionError(f"Not logged:\n\n{reduced_log}")

    def assert_not_logged(self, log: Logged) -> None:
        """
        Fails *immediately* if the expected ``log`` pattern **has** arrived.

        :param log: The expected :doc:`log pattern <logged>`.
        :raises AssertionError: If the expected ``log`` pattern **has** arrived.
        """
        reduced_log = self._reduce(log)
        if reduced_log is None:
            raise AssertionError(f"Logged:\n\n{log}")

    def wait_for(self, log: Logged, *, timeout: float | None = None) -> None:
        """
        Waits for the expected ``log`` pattern to arrive or the ``timeout`` to expire.

        :param log: The expected :doc:`log pattern <logged>`.
        :param timeout: How long to wait (in seconds) before failing the test. Defaults to the ``timeout`` passed to
            :class:`Logot`.
        :raises AssertionError: If the expected ``log`` pattern does not arrive within ``timeout`` seconds.
        """
        waiter = self._open_waiter(log, SyncWaiter, timeout=timeout)
        try:
            waiter.wait()
        finally:
            self._close_waiter(waiter)

    async def await_for(self, log: Logged, *, timeout: float | None = None) -> None:
        """
        Waits *asynchronously* for the expected ``log`` pattern to arrive or the ``timeout`` to expire.

        :param log: The expected :doc:`log pattern <logged>`.
        :param timeout: How long to wait (in seconds) before failing the test. Defaults to the ``timeout`` passed to
            :class:`Logot`.
        :raises AssertionError: If the expected ``log`` pattern does not arrive within ``timeout`` seconds.
        """
        waiter = self._open_waiter(log, AsyncWaiter, timeout=timeout)
        try:
            await waiter.wait()
        finally:
            self._close_waiter(waiter)

    def _emit(self, record: logging.LogRecord) -> None:
        with self._lock:
            # De-duplicate log records.
            # Duplicate log records are possible if we have multiple active captures.
            record_id = id(record)
            if record_id in self._seen_records:  # pragma: no cover
                return
            self._seen_records[record_id] = record
            # If there is a waiter that has not been fully reduced, attempt to reduce it.
            if self._waiter is not None and self._waiter.log is not None:
                self._waiter.log = self._waiter.log._reduce(record)
                # If the waiter has fully reduced, notify the blocked caller.
                if self._waiter.log is None:
                    self._waiter.notify()
                return
            # Otherwise, buffer the log record.
            self._queue.append(record)

    def _reduce(self, log: Logged | None) -> Logged | None:
        # Drain the queue until the log is fully reduced.
        # This does not need a lock, since `deque.popleft()` is thread-safe.
        while self._queue and log is not None:
            log = log._reduce(self._queue.popleft())
        # All done!
        return log

    def _open_waiter(self, log: Logged, waiter_cls: type[W], *, timeout: float | None) -> W:
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
            waiter = self._waiter = waiter_cls(log, timeout=timeout)
            # Apply an immediate reduction.
            waiter.log = self._reduce(waiter.log)
            if waiter.log is None:
                waiter.notify()
            # All done!
            return waiter

    def _close_waiter(self, waiter: Waiter) -> None:
        with self._lock:
            # Clear the waiter.
            self._waiter = None
            # Error if the waiter logs are not fully reduced.
            if waiter.log is not None:
                raise AssertionError(f"Not logged:\n\n{waiter.log}")


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

    def __init__(self, logot: Logot, *, levelno: int) -> None:
        super().__init__(levelno)
        self._logot = logot

    def emit(self, record: logging.LogRecord) -> None:
        self._logot._emit(record)
