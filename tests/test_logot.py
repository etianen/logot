from __future__ import annotations

import logging

import pytest

from logot import Logot, logged
from tests import lines, log_soon, logger


def test_capturing() -> None:
    assert logger.level == logging.NOTSET
    # Set a fairly non-verbose log level.
    logger.setLevel(logging.WARNING)
    try:
        with Logot().capturing(level=logging.DEBUG, logger=logger) as logot:
            assert isinstance(logot, Logot)
            # The logger will have been overridden for the required verbosity.
            assert logger.level == logging.DEBUG
        # When the capture ends, the logging verbosity is restored.
        assert logger.level == logging.WARNING
    finally:
        # Whatever this test does, reset the logger to what it was!
        logger.setLevel(logging.NOTSET)


def test_assert_logged_pass(logot: Logot) -> None:
    logger.info("foo bar")
    logot.assert_logged(logged.info("foo bar"))


def test_assert_logged_fail(logot: Logot) -> None:
    logger.info("boom!")
    with pytest.raises(AssertionError) as ex:
        logot.assert_logged(logged.info("foo bar"))
    assert str(ex.value) == lines(
        "Not logged:",
        "",
        "[INFO] foo bar",
    )


def test_assert_not_logged_pass(logot: Logot) -> None:
    logger.info("boom!")
    logot.assert_not_logged(logged.info("foo bar"))


def test_assert_not_logged_fail(logot: Logot) -> None:
    logger.info("foo bar")
    with pytest.raises(AssertionError) as ex:
        logot.assert_not_logged(logged.info("foo bar"))
    assert str(ex.value) == lines(
        "Logged:",
        "",
        "[INFO] foo bar",
    )


def test_wait_for_pass_immediate(logot: Logot) -> None:
    logger.info("foo bar")
    logot.wait_for(logged.info("foo bar"))


def test_wait_for_pass_soon(logot: Logot) -> None:
    with log_soon(logging.INFO, "foo bar"):
        logot.wait_for(logged.info("foo bar"))


def test_wait_for_fail(logot: Logot) -> None:
    logger.info("boom!")
    with pytest.raises(AssertionError) as ex:
        logot.wait_for(logged.info("foo bar"), timeout=0.1)
    assert str(ex.value) == lines(
        "Not logged:",
        "",
        "[INFO] foo bar",
    )


async def test_await_for_pass_immediate(logot: Logot) -> None:
    logger.info("foo bar")
    await logot.await_for(logged.info("foo bar"))
