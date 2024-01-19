from __future__ import annotations

import pytest

from logot._match import compile


@pytest.mark.parametrize(
    ("pattern", "msg", "matches"),
    (
        # Character conversions match a single character.
        ("foo %c baz", "foo b baz", True),
        # Character conversions do not match multiple characters.
        ("foo %c baz", "foo bar baz", False),
        # Character conversions do not match zero characters.
        ("foo %c baz", "foo  baz", False),
        # String conversions match multiple characters.
        ("foo %r baz", "foo bar baz", True),
        ("foo %s baz", "foo bar baz", True),
        ("foo %a baz", "foo bar baz", True),
    ),
)
def test_match(pattern: str, msg: str, matches: bool) -> None:
    assert (compile(pattern).fullmatch(msg) is not None) is matches
