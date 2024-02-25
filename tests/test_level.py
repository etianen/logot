from __future__ import annotations

from typing import cast

import pytest

from logot._level import level_matcher
from logot._typing import Level


def test_eq_pass() -> None:
    assert level_matcher("INFO") == level_matcher("INFO")
    assert level_matcher(20) == level_matcher(20)


def test_eq_fail() -> None:
    assert level_matcher("INFO") != level_matcher("WARNING")
    assert level_matcher(20) != level_matcher(30)
    assert level_matcher("INFO") != level_matcher(20)


def test_repr() -> None:
    assert repr(level_matcher("INFO")) == "'INFO'"
    assert repr(level_matcher(20)) == "20"


def test_str() -> None:
    assert str(level_matcher("INFO")) == "[INFO]"
    assert str(level_matcher(20)) == "[Level 20]"


def test_invalid() -> None:
    with pytest.raises(TypeError) as ex:
        level_matcher(cast(Level, 1.5))
    assert str(ex.value) == "Invalid level: 1.5"
