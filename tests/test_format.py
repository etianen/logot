from __future__ import annotations

from logot._format import format_log


def test_format_log() -> None:
    assert format_log("INFO", "foo bar") == "[INFO] foo bar"
