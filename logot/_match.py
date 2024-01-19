from __future__ import annotations

import re

_RE_FORMAT = re.compile(r"%(.)")

_CONVERSION_INT = r"\-?\d+"
_CONVERSION_FLOAT = r"\-?\d+"
_CONVERSION_STR = r".+"
_CONVERSION_MAP = {
    "%": r"%",
    # Integer conversions.
    "d": _CONVERSION_INT,
    "i": _CONVERSION_INT,
    "u": _CONVERSION_INT,
    # Float conversions.
    "f": _CONVERSION_FLOAT,
    "F": _CONVERSION_FLOAT,
    # Character conversions.
    "c": r".",
    # String conversions.
    "r": _CONVERSION_STR,
    "s": _CONVERSION_STR,
    "a": _CONVERSION_STR,
}


def _replace(match: re.Match[str]) -> str:
    try:
        return _CONVERSION_MAP[match.group(1)]
    except KeyError:
        raise ValueError(f"Unsupported format: {match.group(0)}") from None


def compile(pattern: str) -> re.Pattern[str]:
    return re.compile(_RE_FORMAT.sub(_replace, re.escape(pattern)))
