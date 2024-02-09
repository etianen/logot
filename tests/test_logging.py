from __future__ import annotations

import logging

from logot import Logot, logged


def test_capturing() -> None:
    with Logot().capturing() as logot:
        # Ensure log capturing is enabled.
        logging.info("foo bar")
        logot.assert_logged(logged.info("foo bar"))
    # Ensure log capturing is disabled.
    logging.info("foo bar")
    logot.assert_not_logged(logged.info("foo bar"))


def test_capturing_level_pass() -> None:
    with Logot().capturing(level=logging.INFO) as logot:
        logging.info("foo bar")
        logot.assert_logged(logged.info("foo bar"))


def test_capturing_level_fail() -> None:
    with Logot().capturing(level=logging.INFO) as logot:
        logging.debug("foo bar")
        logot.assert_not_logged(logged.debug("foo bar"))


def test_capturing_level_reset() -> None:
    logger = logging.getLogger()
    assert logger.level == logging.WARNING
    # Set a fairly non-verbose log level.
    try:
        with Logot().capturing(level=logging.INFO):
            # The logger will have been overridden for the required verbosity.
            assert logger.level == logging.INFO
        # When the capture ends, the logging verbosity is restored.
        assert logger.level == logging.WARNING
    finally:
        # Whatever this test does, reset the logger to what it was!
        logger.setLevel(logging.NOTSET)


def test_capturing_logger_pass() -> None:
    logger = logging.getLogger("tests")
    with Logot().capturing(logger="tests") as logot:
        logger.info("foo bar")
        logot.assert_logged(logged.info("foo bar"))


def test_capturing_logger_fail() -> None:
    with Logot().capturing(logger="tests") as logot:
        logging.info("foo bar")
        logot.assert_not_logged(logged.info("foo bar"))


def test_capture(logot: Logot) -> None:
    logging.info("foo bar")
    logot.assert_logged(logged.info("foo bar"))


def test_capture_levelno(logot: Logot) -> None:
    logging.log(logging.INFO, "foo bar")
    logot.assert_logged(logged.log(logging.INFO, "foo bar"))
