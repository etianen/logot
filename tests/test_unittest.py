from __future__ import annotations

import logging

from logot import logged
from logot.unittest import LogotTestCase


class TestUnitTest(LogotTestCase):
    def test_capture(self) -> None:
        logging.info("foo bar")
        self.logot.assert_logged(logged.info("foo bar"))

    def test_debug(self) -> None:
        TestUnitTest("test_capture").debug()
