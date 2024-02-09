from __future__ import annotations

from contextvars import ContextVar
from shlex import quote
from typing import Any, Callable

import pytest

from logot import Capturer, Logot
from logot._pytest import get_optname, get_qualname
from logot._typing import MISSING, Level, Name
from logot._wait import AsyncWaiter
from logot.asyncio import AsyncioWaiter
from logot.logging import LoggingCapturer

EXPECTED_VAR: ContextVar[Any] = ContextVar(f"{__name__}.EXPECTED_VAR")


def assert_fixture_config(
    pytester: pytest.Pytester,
    name: str,
    value: Any,
    *,
    expected: Any = MISSING,
    passed: bool = True,
) -> None:
    qualname = get_qualname(name)
    pytester.makepyfile(
        f"""
        from tests.test_pytest import EXPECTED_VAR

        def test_{name}({qualname}):
            assert {qualname} == EXPECTED_VAR.get()
        """
    )
    # Set the expected `ContextVar`.
    if expected is MISSING:
        expected = value
    expected_token = EXPECTED_VAR.set(expected)
    try:
        # Run the pytest with a CLI option.
        result = pytester.runpytest(f"{get_optname(name)}={quote(str(value))}")
        result.assert_outcomes(passed=int(passed), errors=int(not passed))
        # Run the pytest with an INI option.
        pytester.makeini(
            f"""
            [pytest]
            {qualname} = {value}
            """
        )
        # Run the pytest.
        result = pytester.runpytest()
        result.assert_outcomes(passed=int(passed), errors=int(not passed))
    finally:
        # Reset the expected `ContextVar`.
        EXPECTED_VAR.reset(expected_token)


def test_level_default(logot_level: Level) -> None:
    assert logot_level == Logot.DEFAULT_LEVEL


def test_level_config_pass(pytester: pytest.Pytester) -> None:
    assert_fixture_config(pytester, "level", "INFO")


def test_name_default(logot_name: Name) -> None:
    assert logot_name == Logot.DEFAULT_NAME


def test_name_config_pass(pytester: pytest.Pytester) -> None:
    assert_fixture_config(pytester, "name", "logot")


def test_capturer_default(logot_capturer: Callable[[], Capturer]) -> None:
    assert logot_capturer is Logot.DEFAULT_CAPTURER


def test_capturer_config_pass(pytester: pytest.Pytester) -> None:
    assert_fixture_config(pytester, "capturer", "logot.logging.LoggingCapturer", expected=LoggingCapturer)


def test_capturer_config_fail(pytester: pytest.Pytester) -> None:
    assert_fixture_config(pytester, "capturer", "boom!", passed=False)


def test_timeout_default(logot_timeout: float) -> None:
    assert logot_timeout == Logot.DEFAULT_TIMEOUT


def test_timeout_config_pass(pytester: pytest.Pytester) -> None:
    assert_fixture_config(pytester, "timeout", 9999.0)


def test_timeout_config_fail(pytester: pytest.Pytester) -> None:
    assert_fixture_config(pytester, "timeout", "boom!", passed=False)


def test_async_waiter_default(logot_async_waiter: Callable[[], AsyncWaiter]) -> None:
    assert logot_async_waiter is Logot.DEFAULT_ASYNC_WAITER


def test_async_waiter_config_pass(pytester: pytest.Pytester) -> None:
    assert_fixture_config(pytester, "async_waiter", "logot.asyncio.AsyncioWaiter", expected=AsyncioWaiter)


def test_async_waiter_config_fail(pytester: pytest.Pytester) -> None:
    assert_fixture_config(pytester, "async_waiter", "boom!", passed=False)
