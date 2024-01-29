from __future__ import annotations

from logot import Captured


def test_eq_pass() -> None:
    assert Captured("INFO", "foo bar", levelno=20) == Captured("INFO", "foo bar", levelno=20)


def test_eq_fail() -> None:
    # Different levelnames are not equal.
    assert Captured("INFO", "foo bar", levelno=20) != Captured("DEBUG", "foo bar", levelno=20)
    # Different messages are not equal.
    assert Captured("INFO", "foo bar", levelno=20) != Captured("INFO", "foo", levelno=20)
    # Different levelnos are not equal.
    assert Captured("INFO", "foo bar", levelno=20) != Captured("INFO", "foo bar", levelno=10)


def test_repr() -> None:
    assert repr(Captured("INFO", "foo bar", levelno=20)) == "Captured('INFO', 'foo bar', levelno=20)"


def test_str() -> None:
    assert str(Captured("INFO", "foo bar", levelno=20)) == "[INFO] foo bar"
