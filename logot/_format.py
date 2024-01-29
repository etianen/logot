from __future__ import annotations

import logging


def format_level(level: str | int) -> str:
    # Format `str` level.
    if isinstance(level, str):
        return level
    # Format `int` level.
    if isinstance(level, int):
        levelname: str = logging.getLevelName(level)
        return levelname
    # Handle invalid level.
    raise TypeError(f"Invalid level: {level!r}")


def format_log(levelname: str, msg: str) -> str:
    return f"[{levelname}] {msg}"
