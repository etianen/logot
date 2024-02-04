from __future__ import annotations

import logging
import threading
from collections.abc import Generator
from contextlib import contextmanager
from time import sleep

from logot import Captured, Logot

logger = logging.getLogger("logot")


def lines(*lines: str) -> str:
    return "\n".join(lines)


@contextmanager
def capture_soon(logot: Logot, captured: Captured) -> Generator[None, None, None]:
    thread = threading.Thread(target=_capture_soon, args=(logot, captured), daemon=True)
    thread.start()
    try:
        yield
    finally:
        thread.join()


def _capture_soon(logot: Logot, captured: Captured) -> None:
    sleep(0.1)
    logot.capture(captured)
