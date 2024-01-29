from __future__ import annotations

import logging

from logot import Captured


def test_eq_pass() -> None:
    assert Captured("INFO", "foo bar", levelno=logging.INFO) == Captured("INFO", "foo bar", levelno=logging.INFO)


def test_eq_fail() -> None:
    # Different levelnames are not equal.
    assert Captured("INFO", "foo bar", levelno=logging.INFO) != Captured("DEBUG", "foo bar", levelno=logging.INFO)
    # Different messages are not equal.
    assert Captured("INFO", "foo bar", levelno=logging.INFO) != Captured("INFO", "foo", levelno=logging.INFO)
    # Different levelnos are not equal.
    assert Captured("INFO", "foo bar", levelno=logging.INFO) == Captured("INFO", "foo bar", levelno=logging.DEBUG)


def test_repr() -> None:
    assert repr(Captured("INFO", "foo bar", levelno=logging.INFO)) == "Captured('INFO', 'foo bar', levelno=20)"


def test_str() -> None:
    assert str(Captured("INFO", "foo bar", levelno=logging.INFO)) == "[INFO] foo bar"
