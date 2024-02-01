from __future__ import annotations

from logot import logged
from logot.unittest import LogotTestCase
from tests import logger


class TestUnitTest(LogotTestCase):
    def test_capture(self) -> None:
        logger.info("foo bar")
        self.logot.assert_logged(logged.info("foo bar"))

    def test_debug(self) -> None:
        TestUnitTest("test_capture").debug()
