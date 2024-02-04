from __future__ import annotations

import pytest

from logot import Captured, Logot, logged
from tests import capture_soon, lines


def test_wait_for_pass_immediate(logot: Logot) -> None:
    logot.capture(Captured("INFO", "foo bar"))
    logot.wait_for(logged.info("foo bar"))


def test_wait_for_pass_soon(logot: Logot) -> None:
    with capture_soon(logot, Captured("INFO", "foo bar")):
        logot.wait_for(logged.info("foo bar"))


def test_wait_for_fail(logot: Logot) -> None:
    logot.capture(Captured("INFO", "boom!"))
    with pytest.raises(AssertionError) as ex:
        logot.wait_for(logged.info("foo bar"), timeout=0.1)
    assert str(ex.value) == lines(
        "Not logged:",
        "",
        "[INFO] foo bar",
    )
