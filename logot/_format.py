from __future__ import annotations


def format_log(levelname: str, msg: str) -> str:
    return f"[{levelname}] {msg}"
