from __future__ import annotations

import logging
from typing import ClassVar
from unittest import TestCase, TestResult

from logot._logot import Logot
from logot._wait import AsyncWaiterFactory


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

    .. note::

        Override this in subclasses to configure automatic :doc:`log capturing </log-capturing>`.
    """

    logot_logger: ClassVar[logging.Logger | str | None] = Logot.DEFAULT_LOGGER
    """
    The ``logger`` used for automatic :doc:`log capturing </log-capturing>`.

    Defaults to :attr:`logot.Logot.DEFAULT_LOGGER`.

    .. note::

        Override this in subclasses to configure automatic :doc:`log capturing </log-capturing>`.
    """

    logot_timeout: ClassVar[float] = Logot.DEFAULT_TIMEOUT
    """
    The default ``timeout`` (in seconds) for :attr:`LogotTestCase.logot`.

    Defaults to :attr:`logot.Logot.DEFAULT_TIMEOUT`.

    .. note::

        Override this in subclasses to configure automatic :doc:`log capturing </log-capturing>`.
    """

    logot_awaiter_factory: ClassVar[AsyncWaiterFactory] = Logot.DEFAULT_AWAITER_FACTORY
    """
    The default ``awaiter_factory`` for :attr:`LogotTestCase.logot`.

    Defaults to :attr:`logot.Logot.DEFAULT_AWAITER_FACTORY`.
    """

    def _logot_setup(self) -> None:
        self.logot = Logot(
            timeout=self.__class__.logot_timeout,
            awaiter_factory=self.__class__.logot_awaiter_factory,
        )
        ctx = self.logot.capturing(level=self.logot_level, logger=self.logot_logger)
        ctx.__enter__()
        self.addCleanup(ctx.__exit__, None, None, None)

    def run(self, result: TestResult | None = None) -> TestResult | None:
        self._logot_setup()
        return super().run(result)

    def debug(self) -> None:
        self._logot_setup()
        return super().debug()
