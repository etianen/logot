from __future__ import annotations

from logot._match import _compile


def assert_matches(pattern: str, msg: str) -> None:
    assert _compile(pattern).match(msg) is not None


def assert_not_matches(pattern: str, msg: str) -> None:
    assert _compile(pattern).fullmatch(msg) is None


def test_s_match() -> None:
    assert_matches("foo %s baz", "foo bar baz")


def test_s_not_match() -> None:
    assert_not_matches("foo %s baz", "foo bar foo")


def test_percent_match() -> None:
    assert_matches("foo %% baz", "foo % baz")


def test_percent_not_match() -> None:
    assert_matches("foo %% baz", "foo bar baz")
