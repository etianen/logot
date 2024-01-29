from __future__ import annotations

import logging
import threading
from collections.abc import Generator
from contextlib import contextmanager
from time import sleep

from logot import Captured

logger = logging.getLogger("logot")


def log(levelname: str, msg: str, *, levelno: int | None = None) -> Captured:
    # Look up default `levelno` from `logging`.
    if levelno is None:
        levelno = logging.getLevelName(levelname)
        assert isinstance(levelno, int)
    # All done!
    return Captured(levelname, msg, levelno=levelno)


def lines(*lines: str) -> str:
    return "\n".join(lines)


@contextmanager
def log_soon(level: int, msg: str) -> Generator[None, None, None]:
    thread = threading.Thread(target=_log_soon, args=(level, msg), daemon=True)
    thread.start()
    try:
        yield
    finally:
        thread.join()


def _log_soon(level: int, msg: str) -> None:
    sleep(0.1)
    logger.log(level, msg)
