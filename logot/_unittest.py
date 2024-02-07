from __future__ import annotations

from typing import Callable, ClassVar
from unittest import TestCase, TestResult

from logot._logot import Capturer, Logot
from logot._wait import AsyncWaiter


class LogotTestCase(TestCase):
    """
    A :class:`unittest.TestCase` subclass with automatic :doc:`log capturing </log-capturing>`.
    """

    logot: Logot
    """
    An initialized :class:`logot.Logot` instance with :doc:`log capturing </log-capturing>` enabled.

    Use this to make log assertions in your tests.
    """

    logot_level: ClassVar[str | int] = Logot.DEFAULT_LEVEL
    """
    The ``level`` used for automatic :doc:`log capturing </log-capturing>`.

    Defaults to :attr:`logot.Logot.DEFAULT_LEVEL`.
    """

    logot_logger: ClassVar[str | None] = Logot.DEFAULT_LOGGER
    """
    The ``logger`` used for automatic :doc:`log capturing </log-capturing>`.

    Defaults to :attr:`logot.Logot.DEFAULT_LOGGER`.
    """

    logot_capturer: ClassVar[Capturer[...]] = Logot.DEFAULT_CAPTURER

    logot_timeout: ClassVar[float] = Logot.DEFAULT_TIMEOUT
    """
    The default ``timeout`` (in seconds) for :attr:`LogotTestCase.logot`.

    Defaults to :attr:`logot.Logot.DEFAULT_TIMEOUT`.
    """

    logot_async_waiter: ClassVar[Callable[[], AsyncWaiter]] = Logot.DEFAULT_ASYNC_WAITER
    """
    The default ``async_waiter`` for :attr:`LogotTestCase.logot`.

    Defaults to :attr:`logot.Logot.DEFAULT_ASYNC_WAITER`.
    """

    def _logot_setup(self) -> None:
        self.logot = Logot(
            timeout=self.__class__.logot_timeout,
            async_waiter=self.__class__.logot_async_waiter,
        )
        ctx = self.__class__.logot_capturer(self.logot, level=self.logot_level, logger=self.logot_logger)
        ctx.__enter__()
        self.addCleanup(ctx.__exit__, None, None, None)

    def run(self, result: TestResult | None = None) -> TestResult | None:
        self._logot_setup()
        return super().run(result)

    def debug(self) -> None:
        self._logot_setup()
        return super().debug()
