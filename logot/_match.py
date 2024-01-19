from __future__ import annotations

import re

# Regex matching a simplified conversion specifier.
_RE_CONVERSION = re.compile(r"%(.)")

# Regex fragments for matchers.
_RE_INT = r"\-?\d+"
_RE_STR = r".*"

# Mapping of conversion types to matcher regex.
_CONVERSION_MAP = {
    "%": r"%",
    # Integer conversions.
    "d": _RE_INT,
    "i": _RE_INT,
    "u": _RE_INT,
    # Float conversions.
    "e": r"\-?(?:\d+.\d+e[\-\+]+\d{2,3}|inf|nan)",
    "E": r"\-?(?:\d+.\d+E[\-\+]+\d{2,3}|INF|NAN)",
    "f": r"\-?(?:\d+.\d+|inf|nan)",
    "F": r"\-?(?:\d+.\d+|INF|NAN)",
    "g": r"\-?(?:\d+(?:.\d+|)(?:e[\-\+]+\d{2,3}|)|inf|nan)",
    "G": r"\-?(?:\d+(?:.\d+|)(?:E[\-\+]+\d{2,3}|)|INF|NAN)",
    # Character conversions.
    "c": r".",
    # String conversions.
    "r": _RE_STR,
    "s": _RE_STR,
    "a": _RE_STR,
}


def _compile_replace(match: re.Match[str]) -> str:
    try:
        return _CONVERSION_MAP[match.group(1)]
    except KeyError:
        raise ValueError(f"Unsupported format: {match.group(0)}") from None


def compile(pattern: str) -> re.Pattern[str]:
    return re.compile(_RE_CONVERSION.sub(_compile_replace, re.escape(pattern)), re.DOTALL)
