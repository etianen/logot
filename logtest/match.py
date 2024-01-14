from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Mapping, Sequence
from functools import wraps
from itertools import chain
from typing import Any, ClassVar, Final

from typing_extensions import Concatenate, ParamSpec, TypeAlias

from logtest._compose import Composable

P = ParamSpec("P")

_MatcherComposer: TypeAlias = Callable[[Iterable[bool]], bool]
MatcherCallable: TypeAlias = Callable[Concatenate[logging.LogRecord, P], bool]


class Matcher(ABC):
    __slots__ = ()

    def __and__(self, matcher: Matcher) -> AllMatcher:
        return AllMatcher._compose(self, matcher)

    def __or__(self, matcher: Matcher) -> AnyMatcher:
        return AnyMatcher._compose(self, matcher)

    @abstractmethod
    def match(self, record: logging.LogRecord) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


class _ComposableMatcher(Matcher, Composable[Matcher]):
    __slots__ = ("matchers",)

    _composer: ClassVar[Callable[[Iterable[bool]], bool]]
    _operator_str: ClassVar[str]

    matchers: Final[Sequence[Matcher]]

    def __init__(self, matchers: Sequence[Matcher]) -> None:
        self.matchers = matchers

    def _decompose(self) -> Sequence[Matcher]:
        return self.matchers

    def match(self, record: logging.LogRecord) -> bool:
        return self.__class__._composer(matcher.match(record) for matcher in self.matchers)

    def __repr__(self) -> str:
        return f" {self._operator_str} ".join(map(repr, self.matchers))

    def __str__(self) -> str:
        return f" {self._operator_str} ".join(map(str, self.matchers))


class AllMatcher(_ComposableMatcher):
    __slots__ = ()
    _composer: ClassVar[_MatcherComposer] = all
    _operator_str: ClassVar[str] = "&"


class AnyMatcher(_ComposableMatcher):
    __slots__ = ()
    _composer: ClassVar[_MatcherComposer] = any
    _operator_str: ClassVar[str] = "|"


class LevelMatcher(Matcher):
    __slots__ = ("levelno",)

    levelno: Final[int]

    def __init__(self, levelno: int) -> None:
        self.levelno = levelno

    def match(self, record: logging.LogRecord) -> bool:
        return record.levelno == self.levelno

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.levelno!r})"

    def __str__(self) -> str:
        return f"[{logging.getLevelName(self.levelno)}]"


def level(level: int | str) -> LevelMatcher:
    # Convert `str` levels to `int`.
    if isinstance(level, str):
        level = logging.getLevelName(level)
        if not isinstance(level, int):
            raise ValueError(f"Unknown log level: {level}")
    # All done!
    return LevelMatcher(level)


class MessageMatcher(Matcher):
    __slots__ = ("message",)

    message: Final[str]

    def __init__(self, message: str) -> None:
        self.message = message

    def match(self, record: logging.LogRecord) -> bool:
        return record.getMessage() == self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r})"

    def __str__(self) -> str:
        return self.message


def message(message: str) -> MessageMatcher:
    return MessageMatcher(message)


class _CallableMatcher(Matcher):
    __slots__ = ("_fn", "_args", "_kwargs")

    _fn: Final[MatcherCallable[Any]]
    _args: Final[tuple[Any, ...]]
    _kwargs: Final[Mapping[str, Any]]

    def __init__(self, fn: MatcherCallable[Any], args: tuple[Any, ...], kwargs: Mapping[str, Any]) -> None:
        self._fn = fn
        self._args = args
        self._kwargs = kwargs

    def match(self, record: logging.LogRecord) -> bool:
        return self._fn(record, *self._args, **self._kwargs)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        args_str = ", ".join(chain(map(repr, self._args), (f"{key}={value!r}" for key, value in self._kwargs.items())))
        return f"{self._fn.__name__}({args_str})"


def matcher() -> Callable[[MatcherCallable[P]], Matcher]:
    def decorator(fn: MatcherCallable[P]) -> Callable[P, Matcher]:
        @wraps(fn)
        def matcher_wrapper(*args: P.args, **kwargs: P.kwargs) -> Matcher:
            return _CallableMatcher(fn, args, kwargs)

        return matcher_wrapper

    return decorator
