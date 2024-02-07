from __future__ import annotations

import logging

from logot import Logot, logged
from tests import logger


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
