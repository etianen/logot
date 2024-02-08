from __future__ import annotations

from collections.abc import Coroutine
from functools import partial, wraps
from typing import Any, Callable

import pytest
import trio

from logot import Captured, Logot, logged
from logot._typing import P
from logot.trio import TrioWaiter
from tests import capture_soon, lines


def trio_test(test_fn: Callable[P, Coroutine[Any, Any, None]]) -> Callable[P, None]:
    @wraps(test_fn)
    def trio_test_wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        trio.run(partial(test_fn, *args, **kwargs))

    return trio_test_wrapper


@pytest.fixture(scope="session")
def logot_async_waiter() -> Callable[[], TrioWaiter]:
    return TrioWaiter


@trio_test
async def test_await_for_pass_immediate(logot: Logot) -> None:
    logot.capture(Captured("INFO", "foo bar"))
    await logot.await_for(logged.info("foo bar"))


@trio_test
async def test_await_for_pass_soon(logot: Logot) -> None:
    with capture_soon(logot, Captured("INFO", "foo bar")):
        await logot.await_for(logged.info("foo bar"))


@trio_test
async def test_await_for_fail(logot: Logot) -> None:
    logot.capture(Captured("INFO", "boom!"))
    with pytest.raises(AssertionError) as ex:
        await logot.await_for(logged.info("foo bar"), timeout=0.1)
    assert str(ex.value) == lines(
        "Not logged:",
        "",
        "[INFO] foo bar",
    )
