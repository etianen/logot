from __future__ import annotations

import re

_RE_FORMAT = re.compile(
    r"%"
    r"(?P<key>\(.*?\)|)"
    r"(?P<flag>[\#0\- \+]*)"
    r"(?P<width>[0-9]+|\*|)"
    r"(?P<precision>\.(?:[0-9]+|\*)|)"
    r"(?P<length>[hlL]*)"
    r"(?P<conversion>[diouxXeEfDFgGcrsa%]+)"
)


def _compile(pattern: str) -> re.Pattern[str]:
    return re.compile(_RE_FORMAT.sub(_replace, re.escape(pattern)))


def _replace(match: re.Match[str]) -> str:
    conversion = match["conversion"]
    # Handle escape.
    if conversion == "%":
        return r"%"
    # Handle integer conversion.
    if conversion in "diou":
        return r"\\d+"
    # Handle string conversion.
    if conversion in "rsa":
        return r".+?"
    raise ValueError(f"Unsupported format: {match.group(0)}")
