from __future__ import annotations

from typing import cast

import pytest

from logot._format import format_level, format_log


def test_format_level_str() -> None:
    assert format_level("INFO") == "INFO"


def test_format_level_int() -> None:
    assert format_level(20) == "Level 20"


def test_validate_logger_type_fail() -> None:
    with pytest.raises(TypeError) as ex:
        format_level(cast(str, 1.5))
    assert str(ex.value) == "Invalid level: 1.5"


def test_format_log() -> None:
    assert format_log("INFO", "foo bar") == "[INFO] foo bar"
