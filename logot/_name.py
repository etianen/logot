from __future__ import annotations

import dataclasses

from logot._capture import Captured
from logot._match import Matcher


@dataclasses.dataclass(frozen=True, repr=False)
class _NameMatcher(Matcher):
    __slots__ = ("name",)
    name: str

    def match(self, captured: Captured) -> bool:
        return captured.name == self.name

    def __repr__(self) -> str:
        return f"name={self.name!r}"


def name_matcher(name: str) -> Matcher:
    return _NameMatcher(name)
