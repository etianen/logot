from __future__ import annotations

import re

_RE_FORMAT = re.compile(r"%(.)")

_CONVERSIONS = {
    "%": r"%",
    # Integer conversion.
    "d": r"\\d+?",
    "i": r"\\d+?",
    "o": r"\\d+?",
    "u": r"\\d+?",
    # String conversion.
    "c": r".",
    "r": r".+?",
    "s": r".+?",
    "a": r".+?",
}


def _compile(pattern: str) -> re.Pattern[str]:
    return re.compile(_RE_FORMAT.sub(_replace, re.escape(pattern)))


def _replace(match: re.Match[str]) -> str:
    try:
        return _CONVERSIONS[match.group(1)]
    except KeyError:
        raise ValueError(f"Unsupported format: {match.group(0)}") from None
