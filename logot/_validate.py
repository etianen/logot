from __future__ import annotations

from logot._typing import Level, Name


def validate_level(level: Level) -> Level:
    # Handle `str` or `int` level.
    if isinstance(level, (str, int)):
        return level
    # Handle invalid level.
    raise TypeError(f"Invalid level: {level!r}")


def validate_name(name: Name) -> Name:
    # Handle `None` or `str` name.
    if name is None or isinstance(name, str):
        return name
    # Handle invalid name.
    raise TypeError(f"Invalid name: {name!r}")


def validate_timeout(timeout: float) -> float:
    # Handle numeric timeout.
    if isinstance(timeout, (float, int)):
        if timeout >= 0.0:
            return float(timeout)
        raise ValueError(f"Invalid timeout: {timeout!r}")
    # Handle invalid timeout.
    raise TypeError(f"Invalid timeout: {timeout!r}")
