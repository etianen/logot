from __future__ import annotations

import re

# Regex matching a simplified conversion specifier.
_RE_CONVERSION = re.compile(r"%(.)")

# Regex fragments for conversions.
_RE_INT = r"\-?\d+"
_RE_STR = r".*"

# Mapping of simplified conversion specifiers to matching regex.
_CONVERSION_MAP = {
    "%": r"%",
    # Integer conversions.
    "d": _RE_INT,
    "i": _RE_INT,
    "u": _RE_INT,
    # Float conversions.
    "f": r"\-?(?:\d+.\d+|inf|nan)",
    "F": r"\-?(?:\d+.\d+|INF|NAN)",
    # Character conversions.
    "c": r".",
    # String conversions.
    "r": _RE_STR,
    "s": _RE_STR,
    "a": _RE_STR,
}


def _replace(match: re.Match[str]) -> str:
    try:
        return _CONVERSION_MAP[match.group(1)]
    except KeyError:
        raise ValueError(f"Unsupported format: {match.group(0)}") from None


def compile(pattern: str) -> re.Pattern[str]:
    return re.compile(_RE_CONVERSION.sub(_replace, re.escape(pattern)), re.DOTALL)
