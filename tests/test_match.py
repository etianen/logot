from __future__ import annotations

import logging

import logtest
from tests import createLogRecord


def test_level_match_pass() -> None:
    assert logtest.match.level(logging.INFO).match(createLogRecord(level=logging.INFO))


def test_level_match_fail() -> None:
    assert not logtest.match.level(logging.INFO).match(createLogRecord(level=logging.DEBUG))
    assert not logtest.match.level(logging.INFO).match(createLogRecord(level=logging.WARN))


def test_level_repr() -> None:
    assert repr(logtest.match.level(logging.INFO)) == "level('INFO')"


def test_level_str() -> None:
    assert str(logtest.match.level(logging.INFO)) == "[INFO]"
