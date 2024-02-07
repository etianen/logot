from __future__ import annotations

import pytest

from logot import Captured, Logot, logged
from tests import lines


def test_assert_logged_pass(logot: Logot) -> None:
    logot.capture(Captured("INFO", "foo bar"))
    logot.assert_logged(logged.info("foo bar"))


def test_assert_logged_fail(logot: Logot) -> None:
    logot.capture(Captured("INFO", "boom!"))
    with pytest.raises(AssertionError) as ex:
        logot.assert_logged(logged.info("foo bar"))
    assert str(ex.value) == lines(
        "Not logged:",
        "",
        "[INFO] foo bar",
    )


def test_assert_not_logged_pass(logot: Logot) -> None:
    logot.capture(Captured("INFO", "boom!"))
    logot.assert_not_logged(logged.info("foo bar"))


def test_assert_not_logged_fail(logot: Logot) -> None:
    logot.capture(Captured("INFO", "foo bar"))
    with pytest.raises(AssertionError) as ex:
        logot.assert_not_logged(logged.info("foo bar"))
    assert str(ex.value) == lines(
        "Logged:",
        "",
        "[INFO] foo bar",
    )


def test_clear(logot: Logot) -> None:
    logot.capture(Captured("INFO", "foo bar"))
    logot.clear()
    logot.assert_not_logged(logged.info("foo bar"))


def test_repr(logot: Logot) -> None:
    assert repr(logot) == "Logot(timeout=3.0, async_waiter=logot.asyncio.AsyncioWaiter)"
