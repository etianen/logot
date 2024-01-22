from __future__ import annotations

import logging

logger = logging.getLogger("logot")


def lines(*lines: str) -> str:
    return "\n".join(lines)
