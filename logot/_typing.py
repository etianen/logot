from __future__ import annotations

import sys

if sys.version_info >= (3, 10):
    from typing import TypeAlias as TypeAlias
else:
    from typing_extensions import TypeAlias as TypeAlias
