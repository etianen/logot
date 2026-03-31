from __future__ import annotations

import dataclasses

from logot._capture import Captured
from logot._match import Matcher


@dataclasses.dataclass(frozen=True, repr=False)
class _ExcInfoBoolMatcher(Matcher):
    __slots__ = ("exc_info",)
    exc_info: bool

    def match(self, captured: Captured) -> bool:
        return captured.name == self.name

    def __repr__(self) -> str:
        return f"name={self.name!r}"


def name_matcher(name: Name) -> Matcher:
    # Handle `str` or `None` name.
    if name is None or isinstance(name, str):
        return _NameMatcher(name)
    # Handle invalid name.
    raise TypeError(f"Invalid name: {name!r}")
