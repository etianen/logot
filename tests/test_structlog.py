from __future__ import annotations

from typing import Callable, Iterator

import pytest
import structlog
from structlog.stdlib import LoggerFactory

from logot import Logot, logged
from logot.structlog import StructlogCapturer

logger = structlog.get_logger()


@pytest.fixture
def stdlib_logger() -> Iterator[None]:
    structlog.configure(logger_factory=LoggerFactory())
    yield
    structlog.reset_defaults()


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


def test_capturing_level_pass() -> None:
    with Logot(capturer=StructlogCapturer).capturing(level="INFO") as logot:
        logger.info("foo bar")
        logot.assert_logged(logged.info("foo bar"))


def test_capturing_level_fail() -> None:
    with Logot(capturer=StructlogCapturer).capturing(level="INFO") as logot:
        logger.debug("foo bar")
        logot.assert_not_logged(logged.debug("foo bar"))


def test_capturing_name_pass(stdlib_logger: None) -> None:
    logger = structlog.get_logger("tests")
    with Logot(capturer=StructlogCapturer).capturing(name="tests") as logot:
        logger.info("foo bar")
        logot.assert_logged(logged.info("foo bar"))


def test_capturing_name_fail(stdlib_logger: None) -> None:
    logger = structlog.get_logger("tests")
    with Logot(capturer=StructlogCapturer).capturing(name="boom") as logot:
        logger.info("foo bar")
        logot.assert_not_logged(logged.info("foo bar"))


def test_capture(logot: Logot) -> None:
    logger.info("foo bar")
    logot.assert_logged(logged.info("foo bar"))


@pytest.mark.skipif(structlog.__version__ < "22", reason="requires structlog>=22")
def test_capture_levelno(logot: Logot) -> None:
    logger.log(20, "foo bar")
    logot.assert_logged(logged.log(20, "foo bar"))
