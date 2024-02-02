from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, Union

if TYPE_CHECKING:
    import logging  # noqa: F401

    from typing_extensions import TypeAlias

T = TypeVar("T")

Level: TypeAlias = str | int

# These type aliases allow using `logging` in annotations without importing `logging` at runtime.
Logger: TypeAlias = "logging.Logger"
LoggerLike: TypeAlias = Union[Logger, str, None]
