from __future__ import annotations

import logging
import threading
from time import sleep

logger = logging.getLogger("logot")


def lines(*lines: str) -> str:
    return "\n".join(lines)


def log_soon(level: int, msg: str) -> None:
    thread = threading.Thread(target=_log_soon, args=(level, msg), daemon=True)
    thread.start()


def _log_soon(level: int, msg: str) -> None:
    sleep(0.1)
    logger.log(level, msg)
