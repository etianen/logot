from __future__ import annotations

import logging


def format_log(levelno: int, msg: str) -> str:
    return f"[{logging.getLevelName(levelno)}] {msg}"
