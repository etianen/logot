from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod

from logot._capture import Captured


class Matcher(ABC):
    __slots__ = ()

    @abstractmethod
    def match(self, captured: Captured) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return f"({self!r})"


@dataclasses.dataclass(frozen=True, repr=False)
class AnyMatcher(Matcher):
    __slots__ = ("msg",)
    msg: str

    def match(self, captured: Captured) -> bool:
        return True

    def __repr__(self) -> str:
        return "..."

    def __str__(self) -> str:
        return self.msg
