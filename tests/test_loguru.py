from __future__ import annotations

from typing import Callable

import pytest
from loguru import logger

from logot import Logot, logged
from logot.loguru import LoguruCapturer
from tests import ExampleException


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


def test_capturing_level_pass() -> None:
    with Logot(capturer=LoguruCapturer).capturing(level="INFO") as logot:
        logger.info("foo bar")
        logot.assert_logged(logged.info("foo bar"))


def test_capturing_level_fail() -> None:
    with Logot(capturer=LoguruCapturer).capturing(level="INFO") as logot:
        logger.debug("foo bar")
        logot.assert_not_logged(logged.debug("foo bar"))


def test_capturing_name_exact_pass() -> None:
    with Logot(capturer=LoguruCapturer).capturing(name=__name__) as logot:
        logger.info("foo bar")
        logot.assert_logged(logged.info("foo bar"))


def test_capturing_name_prefix_pass() -> None:
    with Logot(capturer=LoguruCapturer).capturing(name="tests") as logot:
        logger.info("foo bar")
        logot.assert_logged(logged.info("foo bar"))


def test_capturing_name_fail() -> None:
    with Logot(capturer=LoguruCapturer).capturing(name="boom") as logot:
        logger.info("foo bar")
        logot.assert_not_logged(logged.info("foo bar"))


def test_capture(logot: Logot) -> None:
    logger.info("foo bar")
    logot.assert_logged(logged.info("foo bar"))


def test_capture_levelno(logot: Logot) -> None:
    logger.log(20, "foo bar")
    logot.assert_logged(logged.log(20, "foo bar"))


def test_capture_exc_info_none(logot: Logot) -> None:
    logger.info("foo bar")
    logot.assert_logged(logged.info("foo bar", exc_info=None))


def test_capture_exc_info_true(logot: Logot) -> None:
    try:
        raise ExampleException("foo")
    except Exception:
        logger.exception("foo bar", exc_info=True)
    logot.assert_logged(logged.error("foo bar", exc_info=True))


def test_capture_exc_info_exception(logot: Logot) -> None:
    try:
        raise ExampleException("foo")
    except Exception as ex:
        logger.exception("foo bar", exc_info=ex)
    logot.assert_logged(logged.error("foo bar", exc_info=ExampleException("foo")))


def test_capture_name(logot: Logot) -> None:
    logger.info("foo bar")
    logot.assert_logged(logged.info("foo bar", name=__name__))
