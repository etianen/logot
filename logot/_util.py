from __future__ import annotations

import logging
from typing import NewType

# An integer log level corresponding to a registered log level.
LevelNo = NewType("LevelNo", int)


def to_levelno(level: int | str) -> LevelNo:
    # Handle `int` level.
    if isinstance(level, int):
        if logging.getLevelName(level).startswith("Level "):
            raise ValueError(f"Unknown level: {level!r}")
        return LevelNo(level)
    # Handle `str` level.
    if isinstance(level, str):
        levelno = logging.getLevelName(level)
        if not isinstance(levelno, int):
            raise ValueError(f"Unknown level: {level!r}")
        return LevelNo(levelno)
    # Fail on other types.
    raise TypeError(f"Invalid level: {level!r}")
