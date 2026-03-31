from __future__ import annotations

import dataclasses
from threading import Thread
from time import sleep

from logot import Captured, Logot, Matcher


@dataclasses.dataclass()
class ExampleException(Exception):
    msg: str


@dataclasses.dataclass(frozen=True)
class CustomMatcher(Matcher):
    __slots__ = ()

    def match(self, captured: Captured) -> bool:
        return True


def lines(*lines: str) -> str:
    return "\n".join(lines)


def capture_soon(logot: Logot, captured: Captured) -> None:
    thread = Thread(target=_capture_soon, args=(logot, captured), daemon=True)
    thread.start()


def _capture_soon(logot: Logot, captured: Captured) -> None:
    sleep(0.1)
    logot.capture(captured)
