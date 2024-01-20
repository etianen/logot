from __future__ import annotations

import re
from collections.abc import Callable
from functools import partial

# Compiled matcher callable.
Matcher = Callable[[str], bool]

# Regex matching a simplified conversion specifier.
_RE_CONVERSION = re.compile(r"%(.|$)")

# Mapping of conversion types to regex matchers.
_CONVERSION_INT = r"\-?\d+"
_CONVERSION_STR = r".*?"
_CONVERSION_MAP = {
    # Integer conversion.
    "d": _CONVERSION_INT,
    "i": _CONVERSION_INT,
    "o": r"\-?[0-8]+",
    "u": _CONVERSION_INT,
    "x": r"\-?[\da-f]+",
    "X": r"\-?[\dA-F]+",
    # Float conversion.
    "e": r"\-?(?:\d+\.\d+e[\-\+]\d{2,3}|inf|nan)",
    "E": r"\-?(?:\d+\.\d+E[\-\+]\d{2,3}|INF|NAN)",
    "f": r"\-?(?:\d+\.\d+|inf|nan)",
    "F": r"\-?(?:\d+\.\d+|INF|NAN)",
    "g": r"\-?(?:\d+(?:\.\d+)?(?:e[\-\+]\d{2,3})?|inf|nan)",
    "G": r"\-?(?:\d+(?:\.\d+)?(?:E[\-\+]\d{2,3})?|INF|NAN)",
    # Character conversion.
    "c": r".",
    # String conversion.
    "r": _CONVERSION_STR,
    "s": _CONVERSION_STR,
    "a": _CONVERSION_STR,
    # Percent conversion.
    "%": r"%",
}


def _match_regex(pattern: re.Pattern[str], value: str) -> bool:
    return pattern.fullmatch(value) is not None


def compile_matcher(pattern: str) -> Matcher:
    parts: list[str] = _RE_CONVERSION.split(pattern)
    # If there is at least one matching conversion specifier, this might require a regex matcher.
    if parts:
        is_regex = False
        # Replace conversion types with regex matchers.
        for n in range(1, len(parts), 2):
            part = parts[n]
            try:
                parts[n] = _CONVERSION_MAP[part]
            except KeyError:
                raise ValueError(f"Unsupported format character {part!r}") from None
            # Possibly mark matcher as regex.
            is_regex |= part != "%"
        # Create regex matcher.
        if is_regex:
            # Escape all non-regex parts.
            parts[::2] = map(re.escape, parts[::2])
            # Compile to regex.
            return partial(_match_regex, re.compile("".join(parts), re.DOTALL))
    # Create simple matcher.
    return "".join(parts).__eq__
