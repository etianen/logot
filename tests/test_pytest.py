from __future__ import annotations

import pytest

from logot import Logot
from logot._types import Level, LoggerLike


def test_level_default(logot_level: Level) -> None:
    assert logot_level == Logot.DEFAULT_LEVEL


def test_logger_default(logot_logger: LoggerLike) -> None:
    assert logot_logger == Logot.DEFAULT_LOGGER


def test_timeout_default(logot_timeout: float) -> None:
    assert logot_timeout == Logot.DEFAULT_TIMEOUT
