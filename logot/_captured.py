from __future__ import annotations

import logging
from typing import Final

from logot._format import format_log
from logot._validate import validate_levelno


class Captured:
    """
    A captured log record.

    Send :class:`Captured` logs to :meth:`Logot.capture` to integrate with
    :ref:`3rd-party logging frameworks <captured-3rd-party>`

    .. note::

        This class is for integration with :ref:`3rd-party logging frameworks <captured-3rd-party>`. It is not generally
        used when writing tests.

    .. seealso::

        See :ref:`captured-3rd-party` usage guide.

    :param level: The log level (e.g. :data:`logging.DEBUG`) or string name (e.g. ``"DEBUG"``).
    :param msg: The log message.
    """

    __slots__ = ("levelno", "msg")

    levelno: Final[int]
    """
    The integer log level (e.g. :data:`logging.DEBUG`).
    """

    msg: Final[str]
    """
    The log message.
    """

    def __init__(self, level: int | str, msg: str) -> None:
        self.levelno = validate_levelno(level)
        self.msg = msg

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Captured) and other.levelno == self.levelno and other.msg == self.msg

    def __repr__(self) -> str:
        return f"Captured({logging.getLevelName(self.levelno)!r}, {self.msg!r})"

    def __str__(self) -> str:
        return format_log(self.levelno, self.msg)
