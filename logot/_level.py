from __future__ import annotations

import dataclasses

from logot._capture import Captured
from logot._match import Matcher
from logot._typing import Level


@dataclasses.dataclass(frozen=True, repr=False)
class _LevelNameMatcher(Matcher):
    __slots__ = ("levelname",)
    levelname: str

    def match(self, captured: Captured) -> bool:
        return captured.levelname == self.levelname

    def __repr__(self) -> str:
        return repr(self.levelname)

    def __str__(self) -> str:
        return f"[{self.levelname}]"


DEBUG_MATCHER: Matcher = _LevelNameMatcher("DEBUG")
INFO_MATCHER: Matcher = _LevelNameMatcher("INFO")
WARNING_MATCHER: Matcher = _LevelNameMatcher("WARNING")
ERROR_MATCHER: Matcher = _LevelNameMatcher("ERROR")
CRITICAL_MATCHER: Matcher = _LevelNameMatcher("CRITICAL")


@dataclasses.dataclass(frozen=True, repr=False)
class _LevelNoMatcher(Matcher):
    __slots__ = ("levelno",)
    levelno: int

    def match(self, captured: Captured) -> bool:
        return captured.levelno == self.levelno

    def __repr__(self) -> str:
        return repr(self.levelno)

    def __str__(self) -> str:
        return f"[Level {self.levelno}]"


def level_matcher(level: Level) -> Matcher:
    # Handle `str` level.
    if isinstance(level, str):
        return _LevelNameMatcher(level)
    # Handle `int` level.
    if isinstance(level, int):
        return _LevelNoMatcher(level)
    # Handle invalid level.
    raise TypeError(f"Invalid level: {level!r}")
