from __future__ import annotations

import logging

import pytest

from logot import Captured, Logot, logged
from tests import asyncio_test, capture_soon, lines, logger


def test_capturing() -> None:
    assert logger.level == logging.NOTSET
    # Set a fairly non-verbose log level.
    logger.setLevel(logging.WARNING)
    try:
        with Logot().capturing(level=logging.DEBUG, logger="logot") as logot:
            # The logger will have been overridden for the required verbosity.
            assert logger.level == logging.DEBUG
            # Write a log.
            logger.info("foo bar")
            # Assert the log was captured.
            logot.assert_logged(logged.info("foo bar"))
        # When the capture ends, the logging verbosity is restored.
        assert logger.level == logging.WARNING
    finally:
        # Whatever this test does, reset the logger to what it was!
        logger.setLevel(logging.NOTSET)


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


@asyncio_test
async def test_await_for_pass_immediate(logot: Logot) -> None:
    logot.capture(Captured("INFO", "foo bar"))
    await logot.await_for(logged.info("foo bar"))


@asyncio_test
async def test_await_for_pass_soon(logot: Logot) -> None:
    with capture_soon(logot, Captured("INFO", "foo bar")):
        await logot.await_for(logged.info("foo bar"))


@asyncio_test
async def test_await_for_fail(logot: Logot) -> None:
    logot.capture(Captured("INFO", "boom!"))
    with pytest.raises(AssertionError) as ex:
        await logot.await_for(logged.info("foo bar"), timeout=0.1)
    assert str(ex.value) == lines(
        "Not logged:",
        "",
        "[INFO] foo bar",
    )


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
    assert repr(logot) == "Logot(timeout=3.0)"
