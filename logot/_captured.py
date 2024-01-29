from __future__ import annotations

from logot._format import format_log


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

    :param levelname: The log level name (e.g. ``"DEBUG"``).
    :param msg: The log message.
    :param levelno: The log level number (e.g. :data:`logging.DEBUG`).
    """

    __slots__ = ("levelname", "msg", "levelno")

    levelname: str
    """
    The log level name (e.g. ``"DEBUG"``).
    """

    msg: str
    """
    The log message.
    """

    levelno: int
    """
    The log level number (e.g. :data:`logging.DEBUG`).
    """

    def __init__(self, levelname: str, msg: str, *, levelno: int) -> None:
        self.levelname = levelname
        self.msg = msg
        self.levelno = levelno

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Captured)
            and other.levelname == self.levelname
            and other.msg == self.msg
            and other.levelno == self.levelno
        )

    def __repr__(self) -> str:
        return f"Captured({self.levelname!r}, {self.msg!r}, levelno={self.levelno!r})"

    def __str__(self) -> str:
        return format_log(self.levelname, self.msg)
