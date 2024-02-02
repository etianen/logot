from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    # Avoid importing `logging` just for type checking.
    import logging  # noqa: F401

    from typing_extensions import TypeAlias

T = TypeVar("T")

LevelNo: TypeAlias = int
LevelName: TypeAlias = str
Level: TypeAlias = str | int

Logger: TypeAlias = "logging.Logger"
LoggerLike: TypeAlias = Logger | str | None
