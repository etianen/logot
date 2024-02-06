from __future__ import annotations

import asyncio

from logot._wait import AsyncWaiter


class AsyncioWaiter(AsyncWaiter):
    """
    A :class:`logot.AsyncWaiter` implementation for :mod:`asyncio`.

    .. note::

        This is the default :class:`logot.AsyncWaiter` implementation.
    """

    __slots__ = ("_loop", "_future")

    def __init__(self) -> None:
        # Create an unresolved `asyncio.Future`. This will be resolved by `release()`.
        self._loop = asyncio.get_running_loop()
        self._future: asyncio.Future[None] = self._loop.create_future()

    def release(self) -> None:
        self._loop.call_soon_threadsafe(self._resolve)

    async def wait(self, *, timeout: float) -> None:
        timer = self._loop.call_later(timeout, self._resolve)
        try:
            await self._future
        finally:
            timer.cancel()

    def _resolve(self) -> None:
        try:
            self._future.set_result(None)
        except asyncio.InvalidStateError:  # pragma: no cover
            # It's possible that the timeout and the `release()` will both occur in the same tick of the event loop.
            pass
