from __future__ import annotations

from logot._import import import_any, import_any_parsed


def test_import_any() -> None:
    assert import_any(__name__, "test_import_any") is test_import_any


def test_import_any_parsed() -> None:
    assert import_any_parsed(f"{__name__}.test_import_any_parsed") is test_import_any_parsed
