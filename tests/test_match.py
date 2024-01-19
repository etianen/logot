from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from logot._match import compile


@pytest.mark.parametrize(
    ("pattern", "matches", "not_matches"),
    (
        # Integer conversions match multiple digits.
        ("foo %d baz", "foo 123 baz", True),
        ("foo %i baz", "foo 123 baz", True),
        ("foo %u baz", "foo 123 baz", True),
        # Integer conversions match signed digits.
        ("foo %d baz", "foo -123 baz", True),
        ("foo %i baz", "foo -123 baz", True),
        ("foo %u baz", "foo -123 baz", True),
        # Integer conversions no not match zero digits.
        ("foo %d baz", "foo  baz", False),
        ("foo %i baz", "foo  baz", False),
        ("foo %u baz", "foo  baz", False),
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
        # String conversions do not match zero characters.
        ("foo %r baz", "foo  baz", False),
        ("foo %s baz", "foo  baz", False),
        ("foo %a baz", "foo  baz", False),
    ),
)
def test_match(pattern: str, msg: str, matches: bool) -> None:
    assert (compile(pattern).fullmatch(msg) is not None) is matches
