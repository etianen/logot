from __future__ import annotations

from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from logot._match import compile


def matches(pattern: str, *values: Any) -> bool:
    return compile(pattern).match(pattern % values) is not None


def test_percent_matches() -> None:
    assert compile("foo %% bar").match("foo % bar")


def test_percent_not_matches() -> None:
    assert not compile("foo %% bar").match("foo baz bar")


@given(st.integers())
def test_int_matches(value: int) -> None:
    assert matches("foo %d bar", value)
    assert matches("foo %i bar", value)
    assert matches("foo %u bar", value)
