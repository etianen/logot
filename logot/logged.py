from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from logot._match import compile_matcher
from logot._util import to_levelno


class Logged(ABC):
    __slots__ = ()

    @abstractmethod
    def _reduce(self, record: logging.LogRecord) -> Logged | None:
        raise NotImplementedError


class _LogRecordLogged(Logged):
    __slots__ = ("_levelno", "_msg", "_matcher")

    def __init__(self, levelno: int, msg: str) -> None:
        self._levelno = levelno
        self._msg = msg
        self._matcher = compile_matcher(msg)

    def _reduce(self, record: logging.LogRecord) -> Logged | None:
        if self._levelno == record.levelno and self._matcher(record.getMessage()):
            return None
        return self

    def __repr__(self) -> str:
        return f"log({logging.getLevelName(self._levelno)!r}, {self._msg!r})"


def log(level: int | str, msg: str) -> Logged:
    return _LogRecordLogged(to_levelno(level), msg)


def debug(msg: str) -> Logged:
    return log(logging.DEBUG, msg)


def info(msg: str) -> Logged:
    return log(logging.INFO, msg)


def warning(msg: str) -> Logged:
    return log(logging.WARNING, msg)


def error(msg: str) -> Logged:
    return log(logging.ERROR, msg)


def critical(msg: str) -> Logged:
    return log(logging.CRITICAL, msg)
