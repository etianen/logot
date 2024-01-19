from __future__ import annotations

from typing import Any

from hypothesis import given
from hypothesis import strategies as st

from logot._match import compile


def matches(pattern: str, *values: Any) -> bool:
    return compile(pattern).fullmatch(pattern % values) is not None


def test_percent_matches() -> None:
    assert matches("foo %% bar")


@given(st.integers())
def test_int_matches(value: int) -> None:
    assert matches("foo %d bar", value)
    assert matches("foo %i bar", value)
    assert matches("foo %u bar", value)


@given(st.floats())
def test_float_matches(value: float) -> None:
    assert matches("foo %f bar", value)
    assert matches("foo %F bar", value)


@given(st.characters())
def test_char_matches(value: str) -> None:
    assert matches("foo %c bar", value)


@given(st.text())
def test_str_matches(value: str) -> None:
    assert matches("foo %r bar", value)
    assert matches("foo %s bar", value)
    assert matches("foo %a bar", value)
