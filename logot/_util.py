from __future__ import annotations

import logging


def to_levelno(level: int | str) -> int:
    # Handle `int` level.
    if isinstance(level, int):
        if logging.getLevelName(level).startswith("Level "):
            raise ValueError(f"Unknown level: {level!r}")
        return level
    # Handle `str` level.
    if isinstance(level, str):
        levelno = logging.getLevelName(level)
        if not isinstance(levelno, int):
            raise ValueError(f"Unknown level: {level!r}")
        return levelno
    # Fail on other types.
    raise TypeError(f"Invalid level: {level!r}")
