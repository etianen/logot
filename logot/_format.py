from __future__ import annotations

from logot._typing import Level


def format_level(level: Level) -> str:
    # Format `str` level.
    if isinstance(level, str):
        return level
    # Format `int` level.
    if isinstance(level, int):
        return f"Level {level}"
    # Handle invalid level.
    raise TypeError(f"Invalid level: {level!r}")


def format_log(levelname: str, msg: str) -> str:
    return f"[{levelname}] {msg}"
