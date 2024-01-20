from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from logot._match import compile_matcher
from logot._util import to_levelno


class Logged(ABC):
    __slots__ = ()

    def __gt__(self, log: Logged) -> Logged:
        return _OrderedAllLogged._from_compose(self, log)

    def __and__(self, log: Logged) -> Logged:
        return _UnorderedAllLogged._from_compose(self, log)

    def __or__(self, log: Logged) -> Logged:
        return _AnyLogged._from_compose(self, log)

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


class _ComposedLogged(Logged):
    __slots__ = ("_logs",)

    def __init__(self, logs: tuple[Logged, ...]) -> None:
        self._logs = logs

    @classmethod
    def _from_compose(cls, log_a: Logged, log_b: Logged) -> Logged:
        # If possible, flatten nested logs of the same type.
        if isinstance(log_a, cls):
            if isinstance(log_b, cls):
                return cls((*log_a._logs, *log_b._logs))
            return cls((*log_a._logs, log_b))
        if isinstance(log_b, cls):
            return cls((log_a, *log_b._logs))
        # Wrap the logs without flattening.
        return cls((log_a, log_b))

    @classmethod
    def _from_reduce(cls, logs: tuple[Logged, ...]) -> Logged | None:
        # If all logs are reduced, signal the reduction as complete.
        if not logs:
            return None
        # If there is a single log, do not wrap it.
        if len(logs) == 1:
            return logs[0]
        # Wrap the logs.
        return cls(logs)


class _OrderedAllLogged(_ComposedLogged):
    __slots__ = ()

    def _reduce(self, record: logging.LogRecord) -> Logged | None:
        log = self._logs[0]
        reduced_log = log._reduce(record)
        # Handle full reduction.
        if reduced_log is None:
            return _OrderedAllLogged._from_reduce(self._logs[1:])
        # Handle partial reduction.
        if reduced_log is not log:
            return _OrderedAllLogged((reduced_log, *self._logs[1:]))
        # Handle no reduction.
        return self


class _UnorderedAllLogged(_ComposedLogged):
    __slots__ = ()


class _AnyLogged(_ComposedLogged):
    __slots__ = ()
