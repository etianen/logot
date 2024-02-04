from __future__ import annotations

import asyncio

from logot._wait import AsyncWaiter


class AsyncioWaiter(AsyncWaiter):
    __slots__ = ("_loop", "_event")

    def __init__(self) -> None:
        self._loop = asyncio.get_running_loop()
        self._event = asyncio.Event()

    def notify(self) -> None:
        self._loop.call_soon_threadsafe(self._event.set)

    async def wait(self, *, timeout: float) -> None:
        timer = self._loop.call_later(timeout, self._event.set)
        try:
            await self._event.wait()
        finally:
            timer.cancel()
