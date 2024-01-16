from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable


class ExpectedLogs(ABC):
    __slots__ = ()

    @abstractmethod
    def _reduce(self, record: logging.LogRecord) -> ExpectedLogs | None:
        raise NotImplementedError

    @abstractmethod
    def _format(self, *, indent: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return self._format(indent="")


class _RecordExpectedLog(ExpectedLogs):
    __slots__ = ("_levelno", "_msg")

    def __init__(self, levelno: int, msg: str) -> None:
        self._levelno = levelno
        self._msg = msg

    def _reduce(self, record: logging.LogRecord) -> ExpectedLogs | None:
        if self._levelno == record.levelno and self._msg == record.msg:
            return None
        return self

    def _format(self, *, indent: str) -> str:
        return f"{indent}[{logging.getLevelName(self._levelno)}] {self._msg}"

    def __repr__(self) -> str:
        return f"logot.log({logging.getLevelName(self._levelno)!r}, {self._msg!r})"


class _ComposedExpectedLogs(ExpectedLogs):
    __slots__ = ("_expected_logs",)

    def __init__(self, expected_logs: tuple[ExpectedLogs, ...]) -> None:
        assert len(expected_logs) > 1
        self._expected_logs = expected_logs

    @classmethod
    def _from_compose(cls, a: ExpectedLogs, b: ExpectedLogs) -> ExpectedLogs:
        if isinstance(a, cls):
            if isinstance(b, cls):
                return cls((*a._expected_logs, *b._expected_logs))
            return cls((*a._expected_logs, b))
        if isinstance(b, cls):
            return cls((a, *b._expected_logs))
        return cls((a, b))

    @classmethod
    def _from_reduce(cls, expected_logs: Iterable[ExpectedLogs | None]) -> ExpectedLogs | None:
        # Remove all `None` values.
        expected_logs = (*filter(None, expected_logs),)
        # If all expected logs have been reduced, we're done!
        if not expected_logs:
            return None
        # If there is just a single expected log left, unwrap it.
        if len(expected_logs) == 1:
            return expected_logs[0]
        # Wrap up the remaining expected logs.
        return cls(expected_logs)


class _OrderedAllExpectedLogs(_ComposedExpectedLogs):
    __slots__ = ()

    def _reduce(self, record: logging.LogRecord) -> ExpectedLogs | None:
        expected_log, *expected_logs = self._expected_logs
        expected_log = expected_log._reduce(record)
        return _OrderedAllExpectedLogs._from_reduce((expected_log, *expected_logs))

    def _format(self, *, indent: str) -> str:
        return "\n".join(expected_log._format(indent=indent) for expected_log in self._expected_logs)

    def __repr__(self) -> str:
        return f"({' > '.join(map(repr, self._expected_logs))})"


class _UnorderedAllExpectedLogs(_ComposedExpectedLogs):
    __slots__ = ()

    def _reduce(self, record: logging.LogRecord) -> ExpectedLogs | None:
        return _UnorderedAllExpectedLogs._from_reduce(
            expected_log._reduce(record) for expected_log in self._expected_logs
        )

    def __repr__(self) -> str:
        return f"({' & '.join(map(repr, self._expected_logs))})"
