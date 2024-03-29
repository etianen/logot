from __future__ import annotations

import dataclasses
import re

from logot._capture import Captured
from logot._match import Matcher

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


@dataclasses.dataclass(frozen=True, repr=False)
class _MessageMatcher(Matcher):
    __slots__ = ("msg",)
    msg: str

    def match(self, captured: Captured) -> bool:
        return captured.msg == self.msg

    def __repr__(self) -> str:
        return repr(self.msg)

    def __str__(self) -> str:
        return self.msg


class _MessagePatternMatcher(_MessageMatcher):
    __slots__ = ("_pattern",)

    def __init__(self, msg: str, pattern: re.Pattern[str]) -> None:
        super().__init__(msg)
        self._pattern = pattern

    def match(self, captured: Captured) -> bool:
        return self._pattern.fullmatch(captured.msg) is not None


def msg_matcher(msg: str) -> Matcher:
    parts: list[str] = _RE_CONVERSION.split(msg)
    parts_len = len(parts)
    # If there is more than one part, at least one conversion specifier was found and we might need a regex matcher.
    if parts_len > 1:
        is_regex = False
        # Replace conversion types with regex matchers.
        for n in range(1, parts_len, 2):
            part = parts[n]
            try:
                parts[n] = _CONVERSION_MAP[part]
            except KeyError:
                part_index = sum(map(len, parts[:n:2])) + ((n // 2) * 2) + 1
                raise ValueError(f"Unsupported format character {part!r} at index {part_index}") from None
            # A "%" is used as an escape sequence, and doesn't require a regex matcher. Anything else does.
            is_regex |= part != "%"
        # Create regex matcher.
        if is_regex:
            parts[::2] = map(re.escape, parts[::2])
            pattern = re.compile("".join(parts), re.DOTALL)
            return _MessagePatternMatcher(msg, pattern)
        # Recreate the pattern with all escape sequences replaced.
        msg = "".join(parts)
    # Create simple matcher.
    return _MessageMatcher(msg)
