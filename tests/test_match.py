from __future__ import annotations

import pytest

from logot._match import compile


@pytest.mark.parametrize(
    ("pattern", "msg"),
    (
        ("foo %c baz", "foo b baz"),
        ("foo %r baz", "foo bar baz"),
        ("foo %s baz", "foo bar baz"),
        ("foo %a baz", "foo bar baz"),
    ),
)
def test_match(pattern: str, msg: str) -> None:
    assert compile(pattern).fullmatch(msg) is not None
