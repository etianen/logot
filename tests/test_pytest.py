from __future__ import annotations

import pytest

from logot import Logot
from logot._types import Level, LoggerLike


def test_level_default(logot_level: Level) -> None:
    assert logot_level == Logot.DEFAULT_LEVEL


def test_level_ini(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        """
        def test_level(logot_level):
            assert logot_level == "INFO"
        """
    )
    pytester.makeini(
        """
        [pytest]
        logot_level = INFO
        """
    )
    pytester.runpytest().assert_outcomes(passed=1)


def test_level_cli(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        """
        def test_level(logot_level):
            assert logot_level == "INFO"
        """
    )
    pytester.runpytest("--logot-level=INFO").assert_outcomes(passed=1)


def test_logger_default(logot_logger: LoggerLike) -> None:
    assert logot_logger == Logot.DEFAULT_LOGGER


def test_logger_ini(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        """
        def test_logger(logot_logger):
            assert logot_logger == "logot"
        """
    )
    pytester.makeini(
        """
        [pytest]
        logot_logger = logot
        """
    )
    pytester.runpytest().assert_outcomes(passed=1)


def test_logger_cli(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        """
        def test_logger(logot_logger):
            assert logot_logger == "logot"
        """
    )
    pytester.runpytest("--logot-logger=logot").assert_outcomes(passed=1)


def test_timeout_default(logot_timeout: float) -> None:
    assert logot_timeout == Logot.DEFAULT_TIMEOUT
