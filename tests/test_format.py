from __future__ import annotations

import logging

from logot._format import format_level, format_log


def test_format_level_str() -> None:
    assert format_level("INFO") == "INFO"


def test_format_level_int() -> None:
    assert format_level(logging.INFO) == "INFO"


def test_format_log() -> None:
    assert format_log("INFO", "foo bar") == "[INFO] foo bar"
