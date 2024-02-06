from __future__ import annotations

from importlib import import_module
from typing import Any


def import_any(module: str, name: str) -> Any:
    module_obj = import_module(module)
    return getattr(module_obj, name)


def import_name(name: str) -> Any:
    module, name = name.rsplit(".", 1)
    return import_any(module, name)
