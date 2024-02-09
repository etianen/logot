from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from functools import wraps
from typing import Any, Callable

import pytest

from logot import Captured, Logot, logged
from logot._typing import P
from tests import capture_soon, lines


def asyncio_test(test_fn: Callable[P, Coroutine[Any, Any, None]]) -> Callable[P, None]:
    @wraps(test_fn)
    def asyncio_test_wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        asyncio.run(test_fn(*args, **kwargs))

    return asyncio_test_wrapper


@asyncio_test
async def test_await_for_pass_immediate(logot: Logot) -> None:
    logot.capture(Captured("INFO", "foo bar"))
    await logot.await_for(logged.info("foo bar"))


@asyncio_test
async def test_await_for_pass_soon(logot: Logot) -> None:
    capture_soon(logot, Captured("INFO", "foo bar"))
    await logot.await_for(logged.info("foo bar"))


@asyncio_test
async def test_await_for_fail(logot: Logot) -> None:
    logot.capture(Captured("INFO", "boom!"))
    with pytest.raises(AssertionError) as ex:
        await logot.await_for(logged.info("foo bar"), timeout=0.1)
    assert str(ex.value) == lines(
        "Not logged:",
        "",
        "[INFO] foo bar",
    )
