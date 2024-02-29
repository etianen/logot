from __future__ import annotations

import dataclasses

from logot._capture import Captured
from logot._match import Matcher
from logot._typing import Name


@dataclasses.dataclass(frozen=True, repr=False)
class _NameMatcher(Matcher):
    __slots__ = ("name",)
    name: Name

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
