from __future__ import annotations

from shlex import quote
from typing import Any, Callable

import pytest

from logot import Logot
from logot._pytest import get_optname, get_qualname
from logot._wait import AsyncWaiter
from logot.asyncio import AsyncioWaiter


def assert_fixture_ini(pytester: pytest.Pytester, name: str, value: Any, *, passed: bool = True) -> None:
    qualname = get_qualname(name)
    pytester.makepyfile(
        f"""
        def test_{name}({qualname}):
            assert {qualname} == {value!r}
        """
    )
    pytester.makeini(
        f"""
        [pytest]
        {qualname} = {value}
        """
    )
    # Run the pytest.
    result = pytester.runpytest()
    result.assert_outcomes(passed=int(passed), errors=int(not passed))


def assert_fixture_cli(pytester: pytest.Pytester, name: str, value: Any, *, passed: bool = True) -> None:
    qualname = get_qualname(name)
    pytester.makepyfile(
        f"""
        def test_{name}({qualname}):
            assert {qualname} == {value!r}
        """
    )
    # Run the pytest.
    result = pytester.runpytest(f"{get_optname(name)}={quote(str(value))}")
    result.assert_outcomes(
        passed=int(passed),
        errors=int(not passed),
    )


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
    assert_fixture_ini(pytester, "timeout", "boom!", passed=False)


def test_timeout_cli(pytester: pytest.Pytester) -> None:
    assert_fixture_cli(pytester, "timeout", 9999.0)
    assert_fixture_cli(pytester, "timeout", "boom!", passed=False)


def test_async_waiter_default(logot_async_waiter: Callable[[], AsyncWaiter]) -> None:
    assert logot_async_waiter is AsyncioWaiter
