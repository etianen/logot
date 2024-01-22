from __future__ import annotations

import logging

from logot import Logot


def test_capturing() -> None:
    logger = logging.getLogger("logot")
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
