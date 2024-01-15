from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from logot.util import check_level


class Matcher(ABC):
    __slots__ = ()

    @abstractmethod
    def match(self, record: logging.LogRecord) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


class _LevelMatcher(Matcher):
    __slots__ = ("_levelno",)

    def __init__(self, levelno: int) -> None:
        self._levelno = levelno

    def match(self, record: logging.LogRecord) -> bool:
        return record.levelno == self._levelno

    def __repr__(self) -> str:
        return f"level({logging.getLevelName(self._levelno)!r})"

    def __str__(self) -> str:
        return f"[{logging.getLevelName(self._levelno)}]"


def level(level: int | str) -> Matcher:
    return _LevelMatcher(check_level(level))


class _MessageMatcher(Matcher):
    __slots__ = ("_message",)

    def __init__(self, message: str) -> None:
        self._message = message

    def match(self, record: logging.LogRecord) -> bool:
        return record.getMessage() == self._message

    def __repr__(self) -> str:
        return f"message({self._message!r})"

    def __str__(self) -> str:
        return self._message


def message(message: str) -> Matcher:
    return _MessageMatcher(message)
