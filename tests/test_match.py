from __future__ import annotations

from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from logot._match import compile


def matches(pattern: str, *values: Any) -> bool:
    pattern = f"foo {pattern} bar"
    return compile(pattern).match(pattern % values) is not None


def test_percent_matches() -> None:
    assert matches("foo %%")
