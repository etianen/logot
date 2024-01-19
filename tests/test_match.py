from __future__ import annotations

from logot._match import _compile


def assert_matches(pattern: str, msg: str) -> None:
    assert _compile(pattern).match(msg) is not None


def test_match_s() -> None:
    assert_matches("foo %s baz", "foo bar baz")


def test_match_percent() -> None:
    assert_matches("foo %% baz", "foo % baz")
