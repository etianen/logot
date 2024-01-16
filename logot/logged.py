from __future__ import annotations

import logging
from abc import ABC, abstractmethod


class ExpectedLogs(ABC):
    __slots__ = ()

    @abstractmethod
    def _format(self, *, indent: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def _reduce(self, record: logging.LogRecord) -> ExpectedLogs | None:
        raise NotImplementedError

    def __and__(self, logs: ExpectedLogs) -> ExpectedLogs:
        return _UnorderedAllExpectedLogs._from_compose(self, logs)

    def __gt__(self, logs: ExpectedLogs) -> ExpectedLogs:
        return _OrderedAllExpectedLogs._from_compose(self, logs)

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return self._format(indent="")


class _LogRecordExpectedLogs(ExpectedLogs):
    __slots__ = ("_levelno", "_msg")

    def __init__(self, levelno: int, msg: str) -> None:
        self._levelno = levelno
        self._msg = msg

    def _format(self, *, indent: str) -> str:
        return f"{indent}[{logging.getLevelName(self._levelno)}] {self._msg}"

    def _reduce(self, record: logging.LogRecord) -> ExpectedLogs | None:
        if self._levelno == record.levelno and self._msg == record.msg:
            return None
        return self

    def __repr__(self) -> str:
        return f"logot.log({logging.getLevelName(self._levelno)!r}, {self._msg!r})"


class _ComposedExpectedLogs(ExpectedLogs):
    __slots__ = ("_logs",)

    def __init__(self, logs: tuple[ExpectedLogs, ...]) -> None:
        assert len(logs) > 1, "Unreachable"
        self._logs = logs

    @classmethod
    def _from_compose(cls, log_a: ExpectedLogs, log_b: ExpectedLogs) -> ExpectedLogs:
        # Flatten any logs of this type.
        if isinstance(log_a, cls):
            if isinstance(log_b, cls):
                return cls((*log_a._logs, *log_b._logs))
            return cls((*log_a._logs, log_b))
        if isinstance(log_b, cls):
            return cls((log_a, *log_b._logs))
        # Create unflattened logs of this type.
        return cls((log_a, log_b))

    @classmethod
    def _from_reduce(cls, logs: tuple[ExpectedLogs, ...]) -> ExpectedLogs | None:
        # If all logs have been reduced, we're done!
        if not logs:
            return None
        # If there's just a single log left, unwrap it.
        if len(logs) == 1:
            return logs[0]
        # Wrap the remaining logs.
        return cls(logs)


class _OrderedAllExpectedLogs(_ComposedExpectedLogs):
    __slots__ = ()

    def _reduce(self, record: logging.LogRecord) -> ExpectedLogs | None:
        log, *logs = self._logs
        log = log._reduce(record)
        if log is None:
            return _OrderedAllExpectedLogs._from_reduce((*logs,))
        return _OrderedAllExpectedLogs((log, *logs))

    def _format(self, *, indent: str) -> str:
        return "\n".join(expected_log._format(indent=indent) for expected_log in self._logs)

    def __repr__(self) -> str:
        return f"({' > '.join(map(repr, self._logs))})"


class _UnorderedAllExpectedLogs(_ComposedExpectedLogs):
    __slots__ = ()

    def _reduce(self, record: logging.LogRecord) -> ExpectedLogs | None:
        return _UnorderedAllExpectedLogs._from_reduce(expected_log._reduce(record) for expected_log in self._logs)

    def __repr__(self) -> str:
        return f"({' & '.join(map(repr, self._logs))})"
