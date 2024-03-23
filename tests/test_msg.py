from __future__ import annotations

from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from logot._capture import Captured
from logot._msg import msg_matcher


def assert_matches(pattern: str, *values: Any) -> None:
    # Use Python printf-style formatting to make a string that *definitely* should match.
    expected = pattern % values
    # Assert the matcher matches the expected string.
    matcher = msg_matcher(pattern)
    assert matcher.match(Captured("DEBUG", expected)), f"{pattern} does not match {expected}"


def test_repr() -> None:
    assert repr(msg_matcher("foo %d bar")) == "'foo %d bar'"


def test_str() -> None:
    assert str(msg_matcher("foo %d bar")) == "foo %d bar"


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
        msg_matcher("foo %s %b")
    assert str(ex.value) == "Unsupported format character 'b' at index 8"


def test_truncated_format() -> None:
    with pytest.raises(ValueError) as ex:
        msg_matcher("foo %s %")
    assert str(ex.value) == "Unsupported format character '' at index 8"
