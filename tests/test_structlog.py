from __future__ import annotations

from typing import Callable, Iterator

import pytest
import structlog
from structlog.stdlib import LoggerFactory

from logot import Logot, logged
from logot.structlog import StructlogCapturer

logger = structlog.get_logger(__name__)


@pytest.fixture(autouse=True)
def stdlib_logger() -> Iterator[None]:
    config = structlog.get_config()
    structlog.configure(logger_factory=LoggerFactory())
    yield
    structlog.configure(logger_factory=config["logger_factory"])


@pytest.fixture(scope="session")
def logot_capturer() -> Callable[[], StructlogCapturer]:
    return StructlogCapturer


def test_capturing() -> None:
    with Logot(capturer=StructlogCapturer).capturing() as logot:
        # Ensure log capturing is enabled.
        logger.info("foo bar")
        logot.assert_logged(logged.info("foo bar"))
    # Ensure log capturing is disabled.
    logger.info("foo bar")
    logot.assert_not_logged(logged.info("foo bar"))


def test_multiple_capturing() -> None:
    with Logot(capturer=StructlogCapturer).capturing() as logot_1:
        with Logot(capturer=StructlogCapturer).capturing() as logot_2:
            # Ensure log capturing is enabled.
            logger.info("foo bar")
            logot_1.assert_logged(logged.info("foo bar"))
            logot_2.assert_logged(logged.info("foo bar"))
    # Ensure log capturing is disabled.
    logger.info("foo bar")
    logot_1.assert_not_logged(logged.info("foo bar"))
    logot_2.assert_not_logged(logged.info("foo bar"))


def test_capturing_level_pass() -> None:
    with Logot(capturer=StructlogCapturer).capturing(level="INFO") as logot:
        logger.info("foo bar")
        logot.assert_logged(logged.info("foo bar"))


def test_capturing_level_fail() -> None:
    with Logot(capturer=StructlogCapturer).capturing(level="INFO") as logot:
        logger.debug("foo bar")
        logot.assert_not_logged(logged.debug("foo bar"))


def test_capturing_level_int_pass() -> None:
    with Logot(capturer=StructlogCapturer).capturing(level=20) as logot:
        logger.info("foo bar")
        logot.assert_logged(logged.info("foo bar"))


def test_capturing_level_int_fail() -> None:
    with Logot(capturer=StructlogCapturer).capturing(level=20) as logot:
        logger.debug("foo bar")
        logot.assert_not_logged(logged.debug("foo bar"))


def test_capturing_name_exact_pass() -> None:
    with Logot(capturer=StructlogCapturer).capturing(name=__name__) as logot:
        logger.info("foo bar")
        logot.assert_logged(logged.info("foo bar"))


def test_capturing_name_prefix_pass() -> None:
    with Logot(capturer=StructlogCapturer).capturing(name="tests") as logot:
        logger.info("foo bar")
        logot.assert_logged(logged.info("foo bar"))


def test_capturing_name_fail() -> None:
    with Logot(capturer=StructlogCapturer).capturing(name="boom") as logot:
        logger.info("foo bar")
        logot.assert_not_logged(logged.info("foo bar"))


def test_capture(logot: Logot) -> None:
    logger.info("foo bar")
    logot.assert_logged(logged.info("foo bar"))


def test_capture_levelno(logot: Logot) -> None:
    logger.log(20, "foo bar")
    logot.assert_logged(logged.log(20, "foo bar"))


def test_capture_name(logot: Logot) -> None:
    logger.info("foo bar")
    logot.assert_logged(logged.info("foo bar", name=__name__))
