from __future__ import annotations

import trio
from trio.lowlevel import current_trio_token

from logot._wait import AsyncWaiter


class TrioWaiter(AsyncWaiter):
    """
    A :class:`logot.AsyncWaiter` implementation for :mod:`trio`.
    """

    __slots__ = ("_token", "_event")

    def __init__(self) -> None:
        self._token = current_trio_token()
        self._event = trio.Event()

    def release(self) -> None:
        self._token.run_sync_soon(self._event.set)

    async def wait(self, *, timeout: float) -> None:
        with trio.move_on_after(timeout):
            await self._event.wait()
