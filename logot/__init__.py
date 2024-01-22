from __future__ import annotations

import logging
from contextlib import AbstractContextManager
from types import TracebackType
from typing import ClassVar

from logot._util import to_levelno, to_logger


class _Capturing:
    __slots__ = ("_levelno", "_logger")

    def __init__(self, *, levelno: int, logger: logging.Logger) -> None:
        self._levelno = levelno
        self._logger = logger

    def __enter__(self) -> None:
        pass

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        pass


class Logot:
    __slots__ = ()

    DEFAULT_LEVEL: ClassVar[int | str] = logging.NOTSET
    DEFAULT_LOGGER: ClassVar[logging.Logger | str | None] = None
    DEFAULT_TIMEOUT: ClassVar[float] = 3.0

    def __init__(
        self,
        *,
        level: int | str = DEFAULT_LEVEL,
        logger: logging.Logger | str | None = DEFAULT_LOGGER,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        pass

    def capturing(
        self,
        *,
        level: int | str = DEFAULT_LEVEL,
        logger: logging.Logger | str | None = DEFAULT_LOGGER,
    ) -> AbstractContextManager[None]:
        return _Capturing(levelno=to_levelno(level), logger=to_logger(logger))
