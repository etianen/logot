from __future__ import annotations

from logot._format import format_log


class Captured:
    """
    A captured log record.

    Send :class:`Captured` logs to :meth:`Logot.capture` to integrate with
    :ref:`3rd-party logging frameworks <log-capturing-3rd-party>`.

    .. note::

        This class is for integration with :ref:`3rd-party logging frameworks <log-capturing-3rd-party>`. It is not
        generally used when writing tests.

    .. seealso::

        See :ref:`log-capturing-3rd-party` usage guide.

    :param levelname: See :attr:`Captured.levelname`.
    :param msg: See :attr:`Captured.msg`.
    :param levelno: See :attr:`Captured.levelno`.
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

    levelno: int | None
    """
    The log level number (e.g. :data:`logging.DEBUG`).

    This is an *optional* log capture field. When provided, it allows matching
    :doc:`log patterns </log-pattern-matching>` from :func:`logged.log` with a numeric ``level``.
    """

    def __init__(self, levelname: str, msg: str, *, levelno: int | None = None) -> None:
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
