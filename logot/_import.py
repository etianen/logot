from __future__ import annotations

from importlib import import_module
from typing import Any, Callable


def import_any(module: str, name: str) -> Any:
    module_obj = import_module(module)
    return getattr(module_obj, name)


def import_any_parsed(name: str) -> Any:
    module, name = name.rsplit(".", 1)
    return import_any(module, name)


class LazyCallable:
    __slots__ = ("_module", "_name", "_resolved")

    _resolved: Callable[..., Any]

    def __init__(self, module: str, name: str) -> None:
        self._module = module
        self._name = name

    def __call__(self, /, *args: Any, **kwargs: Any) -> Any:
        try:
            resolved = self._resolved
        except AttributeError:
            resolved = self._resolved = import_any(self._module, self._name)
        return resolved(*args, **kwargs)

    def __repr__(self) -> str:
        return f"{self._module}.{self._name}"
