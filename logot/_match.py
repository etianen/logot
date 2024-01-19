from __future__ import annotations

import re

# Regex matching a simplified conversion specifier.
_RE_CONVERSION = re.compile(r"%(.)")

# Mapping of conversion types to regex matchers.
_CONVERSION_INT = r"\-?\d+"
_CONVERSION_STR = r".*"
_CONVERSION_MAP = {
    # Integer conversion.
    "d": _CONVERSION_INT,
    "i": _CONVERSION_INT,
    "o": r"\-?[0-8]+",
    "u": _CONVERSION_INT,
    "x": r"\-?[\da-f]+",
    "X": r"\-?[\dA-F]+",
    # Float conversion.
    "e": r"\-?(?:\d+.\d+e[\-\+]+\d{2,3}|inf|nan)",
    "E": r"\-?(?:\d+.\d+E[\-\+]+\d{2,3}|INF|NAN)",
    "f": r"\-?(?:\d+.\d+|inf|nan)",
    "F": r"\-?(?:\d+.\d+|INF|NAN)",
    "g": r"\-?(?:\d+(?:.\d+|)(?:e[\-\+]+\d{2,3}|)|inf|nan)",
    "G": r"\-?(?:\d+(?:.\d+|)(?:E[\-\+]+\d{2,3}|)|INF|NAN)",
    # Character conversion.
    "c": r".",
    # String conversion.
    "r": _CONVERSION_STR,
    "s": _CONVERSION_STR,
    "a": _CONVERSION_STR,
    # Percent conversion.
    "%": r"%",
}


def _compile_replace(match: re.Match[str]) -> str:
    try:
        return _CONVERSION_MAP[match.group(1)]
    except KeyError:
        raise ValueError(f"Unsupported format: {match.group(1)!r}") from None


def compile(pattern: str) -> re.Pattern[str]:
    # Escape the pattern. This leaves simplified conversion specifiers intact.
    pattern = re.escape(pattern)
    # Substitute simplified conversion specifiers with regex matchers.
    pattern = _RE_CONVERSION.sub(_compile_replace, pattern)
    # Compile to regex.
    return re.compile(pattern, re.DOTALL)
