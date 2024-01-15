from __future__ import annotations

import logging

import logot
from tests import createLogRecord


def test_level_match_pass() -> None:
    assert logot.match.level(logging.INFO).match(createLogRecord(level=logging.INFO))


def test_level_match_fail() -> None:
    assert not logot.match.level(logging.INFO).match(createLogRecord(level=logging.WARN))


def test_level_repr() -> None:
    assert repr(logot.match.level(logging.INFO)) == "level('INFO')"


def test_level_str() -> None:
    assert str(logot.match.level(logging.INFO)) == "[INFO]"


def test_message_match_pass() -> None:
    assert logot.match.message("Hello world").match(createLogRecord(message="Hello world"))


def test_message_match_fail() -> None:
    assert not logot.match.message("Hello world").match(createLogRecord(message="BOOM"))


def test_message_repr() -> None:
    assert repr(logot.match.message("Hello world")) == "message('Hello world')"


def test_message_str() -> None:
    assert str(logot.match.message("Hello world")) == "Hello world"
