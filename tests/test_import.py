from __future__ import annotations

from logot._import import LazyCallable, import_any, import_any_parsed


def test_import_any() -> None:
    assert import_any(__name__, "test_import_any") is test_import_any


def test_import_any_parsed() -> None:
    assert import_any_parsed(f"{__name__}.test_import_any_parsed") is test_import_any_parsed


def test_lazy_callable_repr() -> None:
    lazy_str = LazyCallable("builtins", "str")
    assert repr(lazy_str) == "builtins.str"


def test_lazy_callable_call() -> None:
    lazy_str = LazyCallable("builtins", "str")
    assert lazy_str(1) == "1"
    assert lazy_str(2) == "2"
