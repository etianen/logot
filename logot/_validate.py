from __future__ import annotations

import logging


def validate_level(level: str | int) -> str | int:
    # Handle `str` or `int` level.
    if isinstance(level, (str, int)):
        return level
    # Handle invalid level.
    raise TypeError(f"Invalid level: {level!r}")


def validate_logger(logger: logging.Logger | str | None) -> logging.Logger:
    # Handle `None` or `str` logger.
    if logger is None or isinstance(logger, str):
        return logging.getLogger(logger)
    # Handle `Logger` logger.
    if isinstance(logger, logging.Logger):
        return logger
    # Handle invalid logger.
    raise TypeError(f"Invalid logger: {logger!r}")


def validate_timeout(timeout: float) -> float:
    # Handle numeric timeout.
    if isinstance(timeout, (float, int)):
        if timeout >= 0.0:
            return float(timeout)
        raise ValueError(f"Invalid timeout: {timeout!r}")
    # Handle invalid timeout.
    raise TypeError(f"Invalid timeout: {timeout!r}")
