from __future__ import annotations

from types import EllipsisType
from typing import TYPE_CHECKING, TypeVar
from typing import ParamSpec as ParamSpec
from typing import TypeAlias as TypeAlias

P = ParamSpec("P")
T = TypeVar("T")

Level: TypeAlias = str | int
Name: TypeAlias = str | None

if TYPE_CHECKING:  # pragma: no cover
    Wildcard: TypeAlias = T | EllipsisType
else:  # pragma: no cover
    # Hide `| EllipsisType` from the docs.
    class Wildcard:
        def __class_getitem__(cls, key):
            return key
