from __future__ import annotations

import fnmatch
import re
from abc import ABC, abstractmethod


class Matcher(ABC):
    __slots__ = ()

    @abstractmethod
    def match(self, msg: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


class _LiteralMatcher(Matcher):
    __slots__ = ("_msg",)
    _msg: str

    def __init__(self, msg: str) -> None:
        self._msg = msg

    def match(self, msg: str) -> bool:
        return self._msg == msg

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _LiteralMatcher) and other._msg == self._msg

    def __repr__(self) -> str:
        return f"{self._msg!r}"

    def __str__(self) -> str:
        return self._msg


class _RegexMatcher(Matcher):
    __slots__ = ("_pattern",)
    _pattern: re.Pattern[str]

    def __init__(self, pattern: re.Pattern[str]) -> None:
        self._pattern = pattern

    def match(self, msg: str) -> bool:
        return self._pattern.match(msg) is not None

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _RegexMatcher) and other._pattern == self._pattern

    def __repr__(self) -> str:
        return f"regex({self._pattern!r})"

    def __str__(self) -> str:
        return self._pattern.pattern


def regex(msg: str, flags: re.RegexFlag | int = 0) -> Matcher:
    return _RegexMatcher(re.compile(msg, flags))


class _GlobMatcher(Matcher):
    __slots__ = ("_msg", "_pattern")
    _msg: str
    _pattern: re.Pattern[str]

    def __init__(self, msg: str, pattern: re.Pattern[str]) -> None:
        self._msg = msg
        self._pattern = pattern

    def match(self, msg: str) -> bool:
        return self._pattern.match(msg) is not None

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _GlobMatcher) and other._pattern == self._pattern

    def __repr__(self) -> str:
        return f"glob({self._pattern!r})"

    def __str__(self) -> str:
        return self._msg


def glob(msg: str) -> Matcher:
    return _GlobMatcher(msg, re.compile(fnmatch.translate(msg)))
