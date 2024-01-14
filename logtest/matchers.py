from __future__ import annotations

import dataclasses
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Sequence
from typing import ClassVar

from logtest._compose import Composable, compose


class Matcher(ABC):
    __slots__ = ()

    def __and__(self, matcher: Matcher) -> AllMatcher:
        return compose(AllMatcher, self, matcher)

    def __or__(self, matcher: Matcher) -> AnyMatcher:
        return compose(AnyMatcher, self, matcher)

    @abstractmethod
    def match(self, record: logging.LogRecord) -> bool:
        raise NotImplementedError


@dataclasses.dataclass()
class _ComposableMatcher(Matcher, Composable[Matcher]):
    __slots__ = ("matchers",)

    _composer: ClassVar[Callable[[Iterable[bool]], bool]]
    matchers: Sequence[Matcher]

    def _decompose(self) -> Sequence[Matcher]:
        return self.matchers

    def match(self, record: logging.LogRecord) -> bool:
        return self.__class__._composer(matcher.match(record) for matcher in self.matchers)


class AllMatcher(_ComposableMatcher):
    __slots__ = ()
    _composer: ClassVar[Callable[[Iterable[bool]], bool]] = all


class AnyMatcher(_ComposableMatcher):
    __slots__ = ()
    _composer: ClassVar[Callable[[Iterable[bool]], bool]] = any
