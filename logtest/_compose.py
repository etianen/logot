from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, TypeVar

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class Composable(Protocol[T_co]):
    __slots__ = ()

    def __init__(self, items: Sequence[T_co]) -> None:
        ...

    def _decompose(self) -> Sequence[T_co]:
        ...


def compose(cls: type[Composable[T]], a: T, b: T) -> Composable[T]:
    if isinstance(a, cls):
        if isinstance(b, cls):
            return cls((*a._decompose(), *b._decompose()))
        return cls((*a._decompose(), b))
    if isinstance(b, cls):
        return cls((a, *b._decompose()))
    return cls((a, b))
