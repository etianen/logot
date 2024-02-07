from __future__ import annotations

import sys
from typing import Any, TypeVar

if sys.version_info >= (3, 10):
    from typing import ParamSpec as ParamSpec
    from typing import TypeAlias as TypeAlias
else:
    from typing_extensions import ParamSpec as ParamSpec
    from typing_extensions import TypeAlias as TypeAlias

P = ParamSpec("P")
T = TypeVar("T")

MISSING: Any = object()
