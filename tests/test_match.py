from __future__ import annotations

from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from logot._match import compile


def assert_matches(pattern: str, *values: Any) -> None:
    # Use Python printf-style formatting to make a string that *definitely* should match.
    expected = pattern % values
    # Assert the matcher matches the expected string.
    matcher = compile(pattern)
    assert matcher(expected) is not None, f"{pattern} does not match {expected}"


@given(st.integers())
def test_int_matches(value: int) -> None:
    assert_matches("foo %d bar", value)
    assert_matches("foo %i bar", value)
    assert_matches("foo %o bar", value)
    assert_matches("foo %u bar", value)
    assert_matches("foo %x bar", value)
    assert_matches("foo %X bar", value)


@given(st.floats())
def test_float_matches(value: float) -> None:
    assert_matches("foo %e bar", value)
    assert_matches("foo %E bar", value)
    assert_matches("foo %f bar", value)
    assert_matches("foo %F bar", value)
    assert_matches("foo %g bar", value)
    assert_matches("foo %G bar", value)


@given(st.characters())
def test_char_matches(value: str) -> None:
    assert_matches("foo %c bar", value)


@given(st.text())
def test_str_matches(value: str) -> None:
    assert_matches("foo %r bar", value)
    assert_matches("foo %s bar", value)
    assert_matches("foo %a bar", value)


def test_percent_matches() -> None:
    assert_matches("foo %% bar")


def test_unsupported_format() -> None:
    with pytest.raises(ValueError) as ex:
        compile("%b")
    assert str(ex.value) == "Unsupported format character 'b'"


def test_truncated_format() -> None:
    with pytest.raises(ValueError) as ex:
        compile("%")
    assert str(ex.value) == "Unsupported format character ''"
