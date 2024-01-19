from __future__ import annotations

import re

_RE_FORMAT = re.compile(r"%(.)")

_MATCHERS = {
    "%": r"%",
    # Integer matchers.
    "d": r"\\d+?",
    "i": r"\\d+?",
    "o": r"\\d+?",
    "u": r"\\d+?",
    # Character matchers.
    "c": r".",
    # String matchers.
    "r": r".+?",
    "s": r".+?",
    "a": r".+?",
}


def _replace(match: re.Match[str]) -> str:
    try:
        return _MATCHERS[match.group(1)]
    except KeyError:
        raise ValueError(f"Unsupported format: {match.group(0)}") from None


def compile(pattern: str) -> re.Pattern[str]:
    return re.compile(_RE_FORMAT.sub(_replace, re.escape(pattern)))
