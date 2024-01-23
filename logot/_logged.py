from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from logot._match import compile_matcher
from logot._validate import validate_levelno


class Logged(ABC):
    """
    A :doc:`log pattern <logged>` passed to :meth:`Logot.wait_for`, :meth:`Logot.await_for` and similar APIs.

    .. important::

        :class:`Logged` instances are immutable and can be reused between tests.

    .. note::

        This is an abstract class and cannot be instantiated. Use the helpers in :mod:`logot.logged` to create log
        patterns.

    .. seealso::

        See :doc:`logged` usage guide.
    """

    __slots__ = ()

    def __rshift__(self, log: Logged) -> Logged:
        return _OrderedAllLogged.from_compose(self, log)

    def __and__(self, log: Logged) -> Logged:
        return _UnorderedAllLogged.from_compose(self, log)

    def __or__(self, log: Logged) -> Logged:
        return _AnyLogged.from_compose(self, log)

    def __str__(self) -> str:
        return self._str(indent="")

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def _reduce(self, record: logging.LogRecord) -> Logged | None:
        raise NotImplementedError

    @abstractmethod
    def _str(self, *, indent: str) -> str:
        raise NotImplementedError


def log(level: int | str, msg: str) -> Logged:
    """
    Creates a :doc:`log pattern <logged>` representing a log record at the given ``level`` with the given ``msg``.

    :param level: A log level (e.g. ``logging.DEBUG``) or string name (e.g. ``"DEBUG"``).
    :param msg: A log :doc:`message pattern <match>`.
    """
    return _LogRecordLogged(validate_levelno(level), msg)


def debug(msg: str) -> Logged:
    """
    Creates a :doc:`log pattern <logged>` representing a log record at ``DEBUG`` level with the given ``msg``.

    :param msg: A log :doc:`message pattern <match>`.
    """
    return _LogRecordLogged(logging.DEBUG, msg)


def info(msg: str) -> Logged:
    """
    Creates a :doc:`log pattern <logged>` representing a log record at ``INFO`` level with the given ``msg``.

    :param msg: A log :doc:`message pattern <match>`.
    """
    return _LogRecordLogged(logging.INFO, msg)


def warning(msg: str) -> Logged:
    """
    Creates a :doc:`log pattern <logged>` representing a log record at ``WARNING`` level with the given ``msg``.

    :param msg: A log :doc:`message pattern <match>`.
    """
    return _LogRecordLogged(logging.WARNING, msg)


def error(msg: str) -> Logged:
    """
    Creates a :doc:`log pattern <logged>` representing a log record at ``ERROR`` level with the given ``msg``.

    :param msg: A log :doc:`message pattern <match>`.
    """
    return _LogRecordLogged(logging.ERROR, msg)


def critical(msg: str) -> Logged:
    """
    Creates a :doc:`log pattern <logged>` representing a log record at ``CRITICAL`` level with the given ``msg``.

    :param msg: A log :doc:`message pattern <match>`.
    """
    return _LogRecordLogged(logging.CRITICAL, msg)


class _LogRecordLogged(Logged):
    __slots__ = ("_levelno", "_msg", "_matcher")

    def __init__(self, levelno: int, msg: str) -> None:
        self._levelno = levelno
        self._msg = msg
        self._matcher = compile_matcher(msg)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _LogRecordLogged) and other._levelno == self._levelno and other._msg == self._msg

    def __repr__(self) -> str:
        return f"log({logging.getLevelName(self._levelno)!r}, {self._msg!r})"

    def _reduce(self, record: logging.LogRecord) -> Logged | None:
        if self._levelno == record.levelno and self._matcher(record.getMessage()):
            return None
        return self

    def _str(self, *, indent: str) -> str:
        return f"[{logging.getLevelName(self._levelno)}] {self._msg}"


class _ComposedLogged(Logged):
    __slots__ = ("_logs",)

    def __init__(self, logs: tuple[Logged, ...]) -> None:
        assert len(logs) > 1
        self._logs = logs

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other._logs == self._logs

    @classmethod
    def from_compose(cls, log_a: Logged, log_b: Logged) -> Logged:
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
    def from_reduce(cls, logs: tuple[Logged, ...]) -> Logged | None:
        assert logs
        # If there is a single log, do not wrap it.
        if len(logs) == 1:
            return logs[0]
        # Wrap the logs.
        return cls(logs)


class _OrderedAllLogged(_ComposedLogged):
    __slots__ = ()

    def __repr__(self) -> str:
        return f"({' >> '.join(map(repr, self._logs))})"

    def _reduce(self, record: logging.LogRecord) -> Logged | None:
        log = self._logs[0]
        reduced_log = log._reduce(record)
        # Handle full reduction.
        if reduced_log is None:
            return _OrderedAllLogged.from_reduce(self._logs[1:])
        # Handle partial reduction.
        if reduced_log is not log:
            return _OrderedAllLogged((reduced_log, *self._logs[1:]))
        # Handle no reduction.
        return self

    def _str(self, *, indent: str) -> str:
        return f"\n{indent}".join(log._str(indent=indent) for log in self._logs)


class _UnorderedAllLogged(_ComposedLogged):
    __slots__ = ()

    def __repr__(self) -> str:
        return f"({' & '.join(map(repr, self._logs))})"

    def _reduce(self, record: logging.LogRecord) -> Logged | None:
        for n, log in enumerate(self._logs):
            reduced_log = log._reduce(record)
            # Handle full reduction.
            if reduced_log is None:
                return _UnorderedAllLogged.from_reduce((*self._logs[:n], *self._logs[n + 1 :]))
            # Handle partial reduction.
            if reduced_log is not log:
                return _UnorderedAllLogged((*self._logs[:n], reduced_log, *self._logs[n + 1 :]))
        # Handle no reduction.
        return self

    def _str(self, *, indent: str) -> str:
        nested_indent = indent + "  "
        logs_str = "".join(f"\n{indent}- {log._str(indent=nested_indent)}" for log in self._logs)
        return f"Unordered:{logs_str}"


class _AnyLogged(_ComposedLogged):
    __slots__ = ()

    def __repr__(self) -> str:
        return f"({' | '.join(map(repr, self._logs))})"

    def _reduce(self, record: logging.LogRecord) -> Logged | None:
        for n, log in enumerate(self._logs):
            reduced_log = log._reduce(record)
            # Handle full reduction.
            if reduced_log is None:
                return None
            # Handle partial reduction.
            if reduced_log is not log:
                return _AnyLogged((*self._logs[:n], reduced_log, *self._logs[n + 1 :]))
        # Handle no reduction.
        return self

    def _str(self, *, indent: str) -> str:
        nested_indent = indent + "  "
        logs_str = "".join(f"\n{indent}- {log._str(indent=nested_indent)}" for log in self._logs)
        return f"Any:{logs_str}"
