from __future__ import annotations

import sys
from typing import Any, TypeVar, Union

if sys.version_info >= (3, 10):
    from typing import ParamSpec as ParamSpec
    from typing import TypeAlias as TypeAlias
else:
    from typing_extensions import ParamSpec as ParamSpec
    from typing_extensions import TypeAlias as TypeAlias

P = ParamSpec("P")
T = TypeVar("T")

# TODO: Use `UnionType` when we only need to support Python 3.10+.
Level: TypeAlias = Union[str, int]
Name: TypeAlias = Union[str, None]


class _Missing:
    __slots__ = ()

    def __repr__(self) -> str:
        return "..."


MISSING: Any = _Missing()
