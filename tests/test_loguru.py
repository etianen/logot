from __future__ import annotations

from typing import Callable

import pytest
from loguru import logger

from logot import Logot, logged
from logot.loguru import LoguruCapturer


@pytest.fixture(scope="session")
def logot_capturer() -> Callable[[], LoguruCapturer]:
    return LoguruCapturer


def test_capturing() -> None:
    with Logot(capturer=LoguruCapturer).capturing() as logot:
        # Ensure log capturing is enabled.
        logger.info("foo bar")
        logot.assert_logged(logged.info("foo bar"))
    # Ensure log capturing is disabled.
    logger.info("foo bar")
    logot.assert_not_logged(logged.info("foo bar"))


def test_capturing_level() -> None:
    with Logot(capturer=LoguruCapturer).capturing(level="INFO") as logot:
        # Ensure log capturing is enabled for `INFO`.
        logger.info("foo bar")
        logot.assert_logged(logged.info("foo bar"))
        # Ensure log capturing is disabled for `DEBUG`.
        logger.debug("foo bar")
        logot.assert_not_logged(logged.debug("foo bar"))


def test_capture(logot: Logot) -> None:
    logger.info("foo bar")
    logot.assert_logged(logged.info("foo bar"))


def test_capture_levelno(logot: Logot) -> None:
    logger.log(20, "foo bar")
    logot.assert_logged(logged.log(20, "foo bar"))
