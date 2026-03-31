from __future__ import annotations

import dataclasses

from logot._capture import Captured
from logot._match import Matcher
from logot._typing import ExcInfo


@dataclasses.dataclass(frozen=True, repr=False)
class _ExcInfoTrueMatcher(Matcher):
    __slots__ = ()

    def match(self, captured: Captured) -> bool:
        return isinstance(captured.exc_info, BaseException)

    def __repr__(self) -> str:
        return "exc_info=True"


@dataclasses.dataclass(frozen=True, repr=False)
class _ExcInfoExceptionMatcher(Matcher):
    __slots__ = ("exc_info",)
    exc_info: BaseException | None

    def match(self, captured: Captured) -> bool:
        return captured.exc_info == self.exc_info

    def __repr__(self) -> str:
        return f"exc_info={self.exc_info!r}"


_TRUE_MATCHER = _ExcInfoTrueMatcher()
_NONE_MATCHER = _ExcInfoExceptionMatcher(None)


def exc_info_matcher(exc_info: ExcInfo) -> Matcher:
    # Handle `bool` name.
    if exc_info is True:
        return _TRUE_MATCHER
    if exc_info in (False, None):
        return _NONE_MATCHER
    # Handle `none`
    if isinstance(exc_info, BaseException):
        return _ExcInfoExceptionMatcher(exc_info)
    # Handle invalid name.
    raise TypeError(f"Invalid exc_info: {exc_info!r}")
