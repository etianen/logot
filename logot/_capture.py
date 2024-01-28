from __future__ import annotations

import logging
from abc import ABC, abstractmethod


class CapturedLog:
    __slots__ = ()

    levelno: int
    msg: str


class Capture(ABC):
    __slots__ = ()

    def capture(self, record: logging.LogRecord) -> None:
        pass

    @abstractmethod
    def start_capture(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop_capture(self) -> None:
        raise NotImplementedError
