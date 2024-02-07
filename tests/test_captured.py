from __future__ import annotations

from logot import Captured


def test_eq_pass() -> None:
    assert Captured("INFO", "foo bar") == Captured("INFO", "foo bar")


def test_eq_fail() -> None:
    # Different levelnames are not equal.
    assert Captured("INFO", "foo bar") != Captured("DEBUG", "foo bar")
    # Different messages are not equal.
    assert Captured("INFO", "foo bar") != Captured("INFO", "foo")
    # Different levelnos are not equal.
    assert Captured("INFO", "foo bar") != Captured("INFO", "foo bar", levelno=10)


def test_repr() -> None:
    assert repr(Captured("INFO", "foo bar")) == "Captured('INFO', 'foo bar', levelno=None)"


def test_str() -> None:
    assert str(Captured("INFO", "foo bar")) == "[INFO] foo bar"
