from __future__ import annotations

import dataclasses


@dataclasses.dataclass(init=False)
class Captured:
    """
    A captured log record.

    Send :class:`Captured` logs to :meth:`Logot.capture` to integrate with
    :ref:`3rd-party logging frameworks <integrations-logging>`.

    .. note::

        This class is for integration with :ref:`3rd-party logging frameworks <integrations-logging>`. It is not
        generally used when writing tests.

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
