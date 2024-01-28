from __future__ import annotations

import logging

from logot._format import format_log


def test_format_log() -> None:
    assert format_log(logging.INFO, "foo bar") == "[INFO] foo bar"
