from __future__ import annotations

from logot._typing import MISSING


def test_missing_repr() -> None:
    assert repr(MISSING) == "..."
