from __future__ import annotations

import logging
from typing import Final

from logot._format import format_log
from logot._validate import validate_levelno


class Captured:
    __slots__ = ("levelno", "msg")

    levelno: Final[int]
    msg: Final[str]

    def __init__(self, level: int | str, msg: str) -> None:
        self.levelno = validate_levelno(level)
        self.msg = msg

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Captured) and other.levelno == self.levelno and other.msg == self.msg

    def __repr__(self) -> str:
        return f"Captured({logging.getLevelName(self.levelno)!r}, {self.msg!r})"

    def __str__(self) -> str:
        return format_log(self.levelno, self.msg)
