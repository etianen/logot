from __future__ import annotations

import logging


def format_level(level: str | int) -> str:
    # Format `str` level.
    if isinstance(level, str):
        return level
    # Format `int` level.
    level: str = logging.getLevelName(level)
    return level


def format_log(levelname: str, msg: str) -> str:
    return f"[{levelname}] {msg}"
