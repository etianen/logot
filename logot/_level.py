from __future__ import annotations

from logot._capture import Captured
from logot._match import Matcher
from logot._typing import Level


class _LevelNameMatcher(Matcher):
    __slots__ = ("_levelname",)

    def __init__(self, levelname: str) -> None:
        self._levelname = levelname

    def match(self, captured: Captured) -> bool:
        return captured.levelname == self._levelname

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _LevelNameMatcher) and other._levelname == self._levelname

    def __repr__(self) -> str:
        return repr(self._levelname)

    def __str__(self) -> str:
        return f"[{self._levelname}]"


DEBUG_MATCHER: Matcher = _LevelNameMatcher("DEBUG")
INFO_MATCHER: Matcher = _LevelNameMatcher("INFO")
WARNING_MATCHER: Matcher = _LevelNameMatcher("WARNING")
ERROR_MATCHER: Matcher = _LevelNameMatcher("ERROR")
CRITICAL_MATCHER: Matcher = _LevelNameMatcher("CRITICAL")


class _LevelNoMatcher(Matcher):
    __slots__ = ("_levelno",)

    def __init__(self, levelno: int) -> None:
        self._levelno = levelno

    def match(self, captured: Captured) -> bool:
        return captured.levelno == self._levelno

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _LevelNoMatcher) and other._levelno == self._levelno

    def __repr__(self) -> str:
        return repr(self._levelno)

    def __str__(self) -> str:
        return f"[Level {self._levelno}]"


def level_matcher(level: Level) -> Matcher:
    # Handle `str` level.
    if isinstance(level, str):
        return _LevelNameMatcher(level)
    # Handle `int` level.
    if isinstance(level, int):
        return _LevelNoMatcher(level)
    # Handle invalid level.
    raise TypeError(f"Invalid level: {level!r}")
