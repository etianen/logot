from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Callable

from logot._format import format_log
from logot._validate import validate_levelno

CaptureImpl = Callable[["CapturedLog", object], bool]


class CapturedLog:
    __slots__ = ("levelno", "msg")

    levelno: int
    msg: str

    def __init__(self, level: int | str, msg: str) -> None:
        self.levelno = validate_levelno(level)
        self.msg = msg

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CapturedLog) and other.levelno == self.levelno and other.msg == self.msg

    def __repr__(self) -> str:
        return f"CapturedLog(levelno={self.levelno!r}, msg={self.msg!r})"

    def __str__(self) -> str:
        return format_log(self.levelno, self.msg)


class Capture(ABC):
    __slots__ = ("_capture_impl",)

    _capture_impl: CaptureImpl

    @property
    def is_capturing(self) -> bool:
        return hasattr(self, "_capture_impl")

    def capture(self, log: CapturedLog, src: object = None) -> None:
        if not self.is_capturing:
            raise RuntimeError(f"{self!r}: Not capturing")
        # Delegate to the capture impl.
        self._capture_impl(log, src)

    @abstractmethod
    def start_capturing(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop_capturing(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError
