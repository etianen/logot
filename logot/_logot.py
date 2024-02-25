from __future__ import annotations

from _thread import allocate_lock
from abc import ABC, abstractmethod
from collections import deque
from contextlib import AbstractContextManager
from types import TracebackType
from typing import Any, Callable, ClassVar, Generic

from logot._capture import Captured
from logot._import import LazyCallable
from logot._logged import Logged
from logot._typing import Level, Name
from logot._validate import validate_level, validate_name, validate_timeout
from logot._wait import AsyncWaiter, W, create_threading_waiter


class Logot:
    """
    The main :mod:`logot` API for capturing and waiting for logs.

    .. seealso::

        See :doc:`/index` usage guide.

    :param capturer: See :attr:`Logot.capturer`.
    :param timeout: See :attr:`Logot.timeout`.
    :param async_waiter: See :attr:`Logot.async_waiter`.
    """

    __slots__ = ("capturer", "timeout", "async_waiter", "_lock", "_queue", "_wait")

    DEFAULT_LEVEL: ClassVar[Level] = "DEBUG"
    """
    The default ``level`` used by :meth:`capturing`.
    """

    DEFAULT_NAME: ClassVar[Name] = None
    """
    The default ``name`` used by :meth:`capturing`.

    Defaults to :data:`None`, representing the root logger.
    """

    DEFAULT_CAPTURER: ClassVar[Callable[[], Capturer]] = LazyCallable("logot.logging", "LoggingCapturer")
    """
    The default :attr:`capturer` for new :class:`Logot` instances.
    """

    DEFAULT_TIMEOUT: ClassVar[float] = 3.0
    """
    The default :attr:`timeout` (in seconds) for new :class:`Logot` instances.
    """

    DEFAULT_ASYNC_WAITER: ClassVar[Callable[[], AsyncWaiter]] = LazyCallable("logot.asyncio", "AsyncioWaiter")
    """
    The default :attr:`async_waiter` for new :class:`Logot` instances.
    """

    capturer: Callable[[], Capturer]
    """
    The default ``capturer`` used by :meth:`capturing`.

    .. note::

        This is for integration with :ref:`3rd-party logging frameworks <integrations-logging>`.

    Defaults to :attr:`Logot.DEFAULT_CAPTURER`.
    """

    timeout: float
    """
    The default ``timeout`` (in seconds) for calls to :meth:`wait_for` and :meth:`await_for`.

    Defaults to :attr:`Logot.DEFAULT_TIMEOUT`.
    """

    async_waiter: Callable[[], AsyncWaiter]
    """
    The default ``async_waiter`` for calls to :meth:`await_for`.

    .. note::

        This is for integration with :ref:`3rd-party asynchronous frameworks <integrations-async>`.

    Defaults to :attr:`Logot.DEFAULT_ASYNC_WAITER`.
    """

    def __init__(
        self,
        *,
        capturer: Callable[[], Capturer] = DEFAULT_CAPTURER,
        timeout: float = DEFAULT_TIMEOUT,
        async_waiter: Callable[[], AsyncWaiter] = DEFAULT_ASYNC_WAITER,
    ) -> None:
        self.capturer = capturer
        self.timeout = validate_timeout(timeout)
        self.async_waiter = async_waiter
        self._lock = allocate_lock()
        self._queue: deque[Captured] = deque()
        self._wait: _Wait[Any] | None = None

    def capturing(
        self,
        *,
        level: Level = DEFAULT_LEVEL,
        name: Name = DEFAULT_NAME,
        capturer: Callable[[], Capturer] | None = None,
    ) -> AbstractContextManager[Logot]:
        """
        Captures logs emitted at the given ``level`` (or higher) by the given logger ``name`` for the duration of the
        context.

        If the named logger level is less verbose than the requested ``level``, it will be temporarily adjusted to the
        requested ``level`` for the duration of the context.

        .. seealso::

            See :doc:`/log-capturing` usage guide.

        :param level: A log level name (e.g. ``"DEBUG"``) or numeric level (e.g. :data:`logging.DEBUG`). Defaults to
            :attr:`Logot.DEFAULT_LEVEL`.
        :param name: A logger name to capture logs from. Defaults to :attr:`Logot.DEFAULT_NAME`.
        :param capturer: Protocol used to capture logs. This is for integration with
            :ref:`3rd-party logging frameworks <integrations-logging>`. Defaults to :attr:`Logot.capturer`.
        """
        if capturer is None:
            capturer = self.capturer
        capturer_obj = capturer()
        level = validate_level(level)
        name = validate_name(name)
        return _Capturing(self, capturer_obj, level=level, name=name)

    def capture(self, captured: Captured) -> None:
        """
        Adds the given captured log record to the internal capture queue.

        Any waiters blocked on :meth:`wait_for` to :meth:`await_for` will be notified and wake up if their
        :doc:`log pattern </log-pattern-matching>` is satisfied.

        .. note::

            This method is for integration with :ref:`3rd-party logging frameworks <integrations-logging>`. It is not
            generally used when writing tests.

        :param captured: The captured log.
        """
        with self._lock:
            # If there is a waiter that has not been fully reduced, attempt to reduce it.
            if self._wait is not None and self._wait.logged is not None:
                self._wait.logged = self._wait.logged.reduce(captured)
                # If the waiter has fully reduced, release the blocked caller.
                if self._wait.logged is None:
                    self._wait.waiter_obj.release()
                return
            # Otherwise, buffer the captured log.
            self._queue.append(captured)

    def assert_logged(self, logged: Logged) -> None:
        """
        Fails *immediately* if the expected log pattern has not arrived.

        :param logged: The expected :doc:`log pattern </log-pattern-matching>`.
        :raises AssertionError: If the expected log pattern has not arrived.
        """
        reduced = self.reduce(logged)
        if reduced is not None:
            raise AssertionError(f"Not logged:\n\n{reduced}")

    def assert_not_logged(self, logged: Logged) -> None:
        """
        Fails *immediately* if the expected log pattern **has** arrived.

        :param logged: The expected :doc:`log pattern </log-pattern-matching>`.
        :raises AssertionError: If the expected log pattern **has** arrived.
        """
        reduced = self.reduce(logged)
        if reduced is None:
            raise AssertionError(f"Logged:\n\n{logged}")

    def wait_for(
        self,
        logged: Logged,
        *,
        timeout: float | None = None,
    ) -> None:
        """
        Waits for the expected log pattern to arrive or the ``timeout`` to expire.

        :param logged: The expected :doc:`log pattern </log-pattern-matching>`.
        :param timeout: How long to wait (in seconds) before failing the test. Defaults to :attr:`Logot.timeout`.
        :raises AssertionError: If the expected log pattern does not arrive within ``timeout`` seconds.
        """
        wait = self._start_waiting(logged, create_threading_waiter, timeout=timeout)
        if wait is None:
            return
        try:
            wait.waiter_obj.acquire(timeout=wait.timeout)
        finally:
            self._stop_waiting(wait)

    async def await_for(
        self,
        logged: Logged,
        *,
        timeout: float | None = None,
        async_waiter: Callable[[], AsyncWaiter] | None = None,
    ) -> None:
        """
        Waits *asynchronously* for the expected log pattern to arrive or the ``timeout`` to expire.

        :param logged: The expected :doc:`log pattern </log-pattern-matching>`.
        :param timeout: How long to wait (in seconds) before failing the test. Defaults to :attr:`Logot.timeout`.
        :param async_waiter: Protocol used to pause tests until expected logs arrive. This is for integration with
            :ref:`3rd-party asynchronous frameworks <integrations-async>`. Defaults to :attr:`Logot.async_waiter`.
        :raises AssertionError: If the expected log pattern does not arrive within ``timeout`` seconds.
        """
        if async_waiter is None:
            async_waiter = self.async_waiter
        wait = self._start_waiting(logged, async_waiter, timeout=timeout)
        if wait is None:
            return
        try:
            await wait.waiter_obj.wait(timeout=wait.timeout)
        finally:
            self._stop_waiting(wait)

    def reduce(self, logged: Logged) -> Logged | None:
        """
        Reduces the expected log pattern using captured logs.

        - No match - The same :doc:`log pattern </log-pattern-matching>` is returned.
        - Partial match - A smaller :doc:`log pattern </log-pattern-matching>` is returned.
        - Full match - :data:`None` is returned.

        .. note::

            This method is for building high-level log assertions. It is not generally used when writing tests.

        :param logged: The expected :doc:`log pattern </log-pattern-matching>`.
        """
        reduced: Logged | None = logged
        # Drain the queue until the log is fully reduced.
        # This does not need a lock, since `deque.popleft()` is thread-safe.
        while reduced is not None:
            try:
                captured = self._queue.popleft()
            except IndexError:
                break
            reduced = reduced.reduce(captured)
        # All done!
        return reduced

    def clear(self) -> None:
        """
        Clears any captured logs.
        """
        self._queue.clear()

    def _start_waiting(self, logged: Logged, waiter: Callable[[], W], *, timeout: float | None) -> _Wait[W] | None:
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
            reduced = self.reduce(logged)
            if reduced is None:
                return None
            # All done!
            waiter_obj = waiter()
            wait = self._wait = _Wait(logged=reduced, timeout=timeout, waiter_obj=waiter_obj)
            return wait

    def _stop_waiting(self, wait: _Wait[Any]) -> None:
        with self._lock:
            # Clear the waiter.
            self._wait = None
            # Error if the waiter logs are not fully reduced.
            if wait.logged is not None:
                raise AssertionError(f"Not logged:\n\n{wait.logged}")

    def __repr__(self) -> str:
        return f"Logot(capturer={self.capturer!r}, timeout={self.timeout!r}, async_waiter={self.async_waiter!r})"


class Capturer(ABC):
    """
    Protocol used by :meth:`Logot.capturing` to capture logs.

    .. note::

        This class is for integration with :ref:`3rd-party logging frameworks <integrations-logging>`. It is not
        generally used when writing tests.
    """

    __slots__ = ()

    @abstractmethod
    def start_capturing(self, logot: Logot, /, *, level: Level, name: Name) -> None:
        """
        Starts capturing logs for the given :class:`Logot`.

        Captured logs should be converted to a :class:`Captured` instance and sent to :meth:`Logot.capture`.

        :param logot: The :class:`Logot` instance.
        :param level: A log level name (e.g. ``"DEBUG"``) or numeric level (e.g. :data:`logging.DEBUG`).
        :param name: A logger name to capture logs from.
        """
        raise NotImplementedError

    @abstractmethod
    def stop_capturing(self) -> None:
        """
        Stops capturing logs.
        """
        raise NotImplementedError


class _Capturing:
    __slots__ = ("_logot", "_capturer_obj", "_level", "_name")

    def __init__(self, logot: Logot, capturer_obj: Capturer, *, level: Level, name: Name) -> None:
        self._logot = logot
        self._capturer_obj = capturer_obj
        self._level = level
        self._name = name

    def __enter__(self) -> Logot:
        self._capturer_obj.start_capturing(self._logot, level=self._level, name=self._name)
        return self._logot

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._capturer_obj.stop_capturing()


class _Wait(Generic[W]):
    __slots__ = ("logged", "timeout", "waiter_obj")

    def __init__(self, *, logged: Logged | None, timeout: float, waiter_obj: W) -> None:
        self.logged = logged
        self.timeout = timeout
        self.waiter_obj = waiter_obj
