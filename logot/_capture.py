from __future__ import annotations

import dataclasses
import sys
from types import TracebackType
from typing import Any

from logot._typing import Name, Wildcard


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
    :param name: See :attr:`Captured.name`.
    """

    __slots__ = ("levelname", "msg", "exc_info", "levelno", "name", "record")

    levelname: str
    """
    The log level name (e.g. ``"DEBUG"``).
    """

    msg: str
    """
    The log message.
    """

    exc_info: Wildcard[BaseException | None]
    """
    The log exception.

    This is an *optional* log capture field. When provided, it allows matching
    :doc:`log patterns </log-pattern-matching>` from :func:`logged.log` with an ``exc_info``.
    """

    levelno: Wildcard[int | None]
    """
    The log level number (e.g. :data:`logging.DEBUG`).

    This is an *optional* log capture field. When provided, it allows matching
    :doc:`log patterns </log-pattern-matching>` from :func:`logged.log` with a numeric ``level``.
    """

    name: Wildcard[Name]
    """
    The logger name.

    This is an *optional* log capture field. When provided, it allows matching
    :doc:`log patterns </log-pattern-matching>` from :func:`logged.log` with a ``name``.
    """

    record: Wildcard[Any]
    """
    The captured log record.

    This is an *optional* log capture field. When provided, it allows matching
    :doc:`log patterns </log-pattern-matching>` from :func:`logged.log` with an ``*args`` custom matcher.

    .. note::

        This is the underlying log record emitted by the :ref:`logging framework <integrations-logging>`.
    """

    def __init__(
        self,
        levelname: str,
        msg: str,
        *,
        exc_info: Wildcard[BaseException | None] = ...,
        levelno: Wildcard[int] = ...,
        name: Wildcard[str | None] = ...,
        record: Wildcard[Any] = ...,
    ) -> None:
        self.levelname = levelname
        self.msg = msg
        self.exc_info = exc_info
        self.levelno = levelno
        self.name = name
        self.record = record


def capture_exc_info(
    exc_info: bool
    | None
    | BaseException
    | tuple[type[BaseException] | None, BaseException | None, TracebackType | None],
) -> BaseException | None:
    if exc_info is None or exc_info is False:
        return None
    if isinstance(exc_info, BaseException):
        return exc_info
    if exc_info is True:
        exc_info = sys.exc_info()
    return exc_info[1]
