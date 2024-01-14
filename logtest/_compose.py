from __future__ import annotations

from abc import abstractmethod
from collections.abc import Sequence
from typing import Protocol, TypeVar

from typing_extensions import Self

T = TypeVar("T")


class Composable(Protocol[T]):
    __slots__ = ()

    @classmethod
    def _compose(cls, a: T, b: T) -> Self:
        if isinstance(a, cls):
            if isinstance(b, cls):
                return cls((*a._decompose(), *b._decompose()))
            return cls((*a._decompose(), b))
        if isinstance(b, cls):
            return cls((a, *b._decompose()))
        return cls((a, b))

    @abstractmethod
    def __init__(self, items: Sequence[T]) -> None:
        raise NotImplementedError

    @abstractmethod
    def _decompose(self) -> Sequence[T]:
        raise NotImplementedError
