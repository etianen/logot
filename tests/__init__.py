from __future__ import annotations

from _thread import start_new_thread
from time import sleep

from logot import Captured, Logot


def lines(*lines: str) -> str:
    return "\n".join(lines)


def capture_soon(logot: Logot, captured: Captured) -> None:
    start_new_thread(_capture_soon, (logot, captured))


def _capture_soon(logot: Logot, captured: Captured) -> None:
    sleep(0.1)
    logot.capture(captured)
