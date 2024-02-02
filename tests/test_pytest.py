from __future__ import annotations

from typing import Any

import pytest

from logot import Logot


def assert_fixture_ini(pytester: pytest.Pytester, name: str, value: Any) -> None:
    pytester.makepyfile(
        f"""
        def test_{name}(logot_{name}):
            assert logot_{name} == {value!r}
        """
    )
    pytester.makeini(
        f"""
        [pytest]
        logot_{name} = {value}
        """
    )
    pytester.runpytest().assert_outcomes(passed=1)


def assert_fixture_cli(pytester: pytest.Pytester, name: str, value: Any) -> None:
    pytester.makepyfile(
        f"""
        def test_{name}(logot_{name}):
            assert logot_{name} == {value!r}
        """
    )
    pytester.runpytest(f"--logot-{name.replace('_', '-')}={value}").assert_outcomes(passed=1)


def test_level_default(logot_level: str | int) -> None:
    assert logot_level == Logot.DEFAULT_LEVEL


def test_level_ini(pytester: pytest.Pytester) -> None:
    assert_fixture_ini(pytester, "level", "INFO")


def test_level_cli(pytester: pytest.Pytester) -> None:
    assert_fixture_cli(pytester, "level", "INFO")


def test_logger_default(logot_logger: str | int) -> None:
    assert logot_logger == Logot.DEFAULT_LOGGER


def test_logger_ini(pytester: pytest.Pytester) -> None:
    assert_fixture_ini(pytester, "logger", "logot")


def test_logger_cli(pytester: pytest.Pytester) -> None:
    assert_fixture_cli(pytester, "logger", "logot")


def test_timeout_default(logot_timeout: float) -> None:
    assert logot_timeout == Logot.DEFAULT_TIMEOUT


def test_timeout_ini(pytester: pytest.Pytester) -> None:
    assert_fixture_ini(pytester, "timeout", 9999.0)


def test_timeout_cli(pytester: pytest.Pytester) -> None:
    assert_fixture_cli(pytester, "timeout", 9999.0)
