from __future__ import annotations

import asyncio
import logging
import threading
from collections.abc import Coroutine, Generator
from contextlib import contextmanager
from functools import wraps
from time import sleep
from typing import Any, Callable

from typing_extensions import ParamSpec

from logot import Captured, Logot

P = ParamSpec("P")

logger = logging.getLogger("logot")


def asyncio_test(test_fn: Callable[P, Coroutine[Any, Any, None]]) -> Callable[P, None]:
    @wraps(test_fn)
    def asyncio_test_wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        asyncio.run(test_fn(*args, **kwargs))

    return asyncio_test_wrapper


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
