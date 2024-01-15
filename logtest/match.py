from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from fnmatch import fnmatch, fnmatchcase
from functools import wraps
from inspect import signature
from itertools import chain
from typing import Generic

from typing_extensions import Concatenate, ParamSpec, TypeAlias

P = ParamSpec("P")

_MatcherCallable: TypeAlias = Callable[Concatenate[logging.LogRecord, P], bool]


class Matcher(ABC):
    __slots__ = ()

    @abstractmethod
    def match(self, record: logging.LogRecord) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


class _LevelMatcher(Matcher):
    __slots__ = ("_levelno",)

    def __init__(self, levelno: int) -> None:
        self._levelno = levelno

    def match(self, record: logging.LogRecord) -> bool:
        return record.levelno == self._levelno

    def __repr__(self) -> str:
        return f"level({logging.getLevelName(self._levelno)!r})"

    def __str__(self) -> str:
        return f"[{logging.getLevelName(self._levelno)}]"


def level(level: int | str) -> _LevelMatcher:
    # Convert `str` level to `int`.
    if isinstance(level, str):
        level = logging.getLevelName(level)
        if not isinstance(level, int):
            raise ValueError(f"Unknown log level: {level}")
    # All done!
    return _LevelMatcher(level)


class _MessageMatcher(Matcher):
    __slots__ = ("_message",)

    def __init__(self, message: str) -> None:
        self._message = message

    def match(self, record: logging.LogRecord) -> bool:
        return record.getMessage() == self._message

    def __repr__(self) -> str:
        return f"message({self._message!r})"

    def __str__(self) -> str:
        return self._message


def message(message: str) -> _MessageMatcher:
    return _MessageMatcher(message)


class _CallableMatcher(Matcher, Generic[P]):
    __slots__ = ("_fn", "_args", "_kwargs")

    def __init__(self, fn: _MatcherCallable[...], args: tuple[object, ...], kwargs: dict[str, object]) -> None:
        self._fn = fn
        self._args = args
        self._kwargs = kwargs

    def match(self, record: logging.LogRecord) -> bool:
        return self._fn(record, *self._args, **self._kwargs)

    def __repr__(self) -> str:
        return f"{self}"

    def __str__(self) -> str:
        args_str = ", ".join(chain(map(repr, self._args), (f"{key}={value!r}" for key, value in self._kwargs.items())))
        return f"{self._fn.__qualname__}({args_str})"


def matcher() -> Callable[[_MatcherCallable[P]], Callable[P, Matcher]]:
    def decorator(fn: _MatcherCallable[P]) -> Callable[P, Matcher]:
        @wraps(fn)
        def matcher_wrapper(*args: P.args, **kwargs: P.kwargs) -> Matcher:
            return _CallableMatcher(fn, args, kwargs)

        # Remove the first param from the signature so generated documentation and other introspection is correct.
        sig = signature(matcher_wrapper)
        matcher_wrapper.__signature__ = sig.replace(parameters=[*sig.parameters.values()][1:])  # type: ignore[attr-defined]

        return matcher_wrapper

    return decorator


@matcher()
def glob(record: logging.LogRecord, pattern: str) -> bool:
    return fnmatchcase(record.getMessage(), pattern)


@matcher()
def iglob(record: logging.LogRecord, pattern: str) -> bool:
    return fnmatch(record.getMessage(), pattern)
