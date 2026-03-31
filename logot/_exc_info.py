from __future__ import annotations

import dataclasses

from logot._capture import Captured
from logot._match import Matcher
from logot._typing import ExcInfo


@dataclasses.dataclass(frozen=True, repr=False)
class _ExcInfoBoolMatcher(Matcher):
    __slots__ = ("exc_info",)
    exc_info: bool

    def match(self, captured: Captured) -> bool:
        return (captured.exc_info is not None) == self.exc_info

    def __repr__(self) -> str:
        return f"exc_info={self.exc_info!r}"


@dataclasses.dataclass(frozen=True, repr=False)
class _ExcInfoExceptionMatcher(Matcher):
    __slots__ = ("exc_info",)
    exc_info: BaseException | None

    def match(self, captured: Captured) -> bool:
        return captured.exc_info == self.exc_info

    def __repr__(self) -> str:
        return f"exc_info={self.exc_info!r}"


def exc_info_matcher(exc_info: ExcInfo) -> Matcher:
    # Handle `bool` name.
    if isinstance(exc_info, bool):
        return _ExcInfoBoolMatcher(exc_info)
    # Handle `none`
    if exc_info is None or isinstance(exc_info, BaseException):
        return _ExcInfoExceptionMatcher(exc_info)
    # Handle invalid name.
    raise TypeError(f"Invalid exc_info: {exc_info!r}")
