from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, TypeVar, Union

if sys.version_info >= (3, 10):
    from types import EllipsisType
    from typing import ParamSpec as ParamSpec
    from typing import TypeAlias as TypeAlias
else:
    from typing_extensions import ParamSpec as ParamSpec
    from typing_extensions import TypeAlias as TypeAlias

    EllipsisType: TypeAlias = Any

P = ParamSpec("P")
T = TypeVar("T")

# TODO: Use `UnionType` when we only need to support Python 3.10+.
Level: TypeAlias = Union[str, int]
Name: TypeAlias = Union[str, None]

if TYPE_CHECKING:  # pragma: no cover
    # TODO: Use `UnionType` when we only need to support Python 3.10+.
    Wildcard: TypeAlias = Union[T, EllipsisType]
else:  # pragma: no cover
    # Hide `| EllipsisType` from the docs.
    class Wildcard:
        def __class_getitem__(cls, key):
            return key
