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
