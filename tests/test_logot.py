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
    finally:
        # Whatever this test does, reset the logger to what it was!
        logger.setLevel(logging.NOTSET)
