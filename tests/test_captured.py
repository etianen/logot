from __future__ import annotations

import logging

from logot import Captured


def test_eq_pass() -> None:
    assert Captured(logging.INFO, "foo bar") == Captured(logging.INFO, "foo bar")


def test_eq_fail() -> None:
    # Different levels are not equal.
    assert Captured(logging.INFO, "foo bar") != Captured(logging.DEBUG, "foo bar")
    # Different messages are not equal.
    assert Captured(logging.INFO, "foo bar") != Captured(logging.INFO, "foo")


def test_repr() -> None:
    assert repr(Captured(logging.INFO, "foo bar")) == "Captured('INFO', 'foo bar')"


def test_str() -> None:
    assert str(Captured(logging.INFO, "foo bar")) == "[INFO] foo bar"
