from __future__ import annotations

from logot import match


def test_literal_match_pass() -> None:
    assert match._LiteralMatcher("Hello world").match("Hello world")


def test_literal_match_fail() -> None:
    assert not match._LiteralMatcher("Hello world").match("Boom!")


def test_literal_eq_pass() -> None:
    assert match._LiteralMatcher("Hello world") == match._LiteralMatcher("Hello world")


def test_literal_eq_fail() -> None:
    assert match._LiteralMatcher("Hello world") != match._LiteralMatcher("Boom!")


def test_literal_repr() -> None:
    assert repr(match._LiteralMatcher("Hello world")) == "'Hello world'"


def test_literal_str() -> None:
    assert str(match._LiteralMatcher("Hello world")) == "Hello world"
