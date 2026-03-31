from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod

from logot._capture import Captured


class Matcher(ABC):
    """
    Protocol used for matching :doc:`log patterns </log-pattern-matching>` from :func:`logged.log` with custom
    ``*matchers``.

    Subclasses should typically be a :func:`dataclasses.dataclass` with ``frozen=True`` to ensure immutability and
    provide an automatic ``__repr__`` implementation.

    .. note::

        This class is for creating custom matching logic. It is not generally used when writing tests.
    """

    __slots__ = ()

    @abstractmethod
    def match(self, captured: Captured) -> bool:
        """
        Tests whether the given :class:`Captured` log record matches.

        :param captured: The :class:`Captured` log record.
        """
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
