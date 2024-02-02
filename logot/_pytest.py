from __future__ import annotations

from collections.abc import Generator
from typing import Any

import pytest

from logot._logot import Logot


def pytest_addoption(parser: pytest.Parser, pluginmanager: pytest.PytestPluginManager) -> None:
    group = parser.getgroup("logot")
    _addoption(
        parser,
        group,
        name="level",
        default=Logot.DEFAULT_LEVEL,
        help="Level used for automatic `logot` log capturing",
    )
    _addoption(
        parser,
        group,
        name="logger",
        default=Logot.DEFAULT_LOGGER,
        help="Logger used for automatic `logot` log capturing",
    )
    _addoption(
        parser,
        group,
        name="timeout",
        default=Logot.DEFAULT_TIMEOUT,
        help="Default timeout (in seconds) for `logot`",
    )


@pytest.fixture()
def logot() -> Generator[Logot, None, None]:
    with Logot().capturing() as logot:
        yield logot


def _addoption(parser: pytest.Parser, group: pytest.OptionGroup, *, name: str, default: Any, help: str) -> None:
    qualname = f"logot_{name}"
    parser.addini(
        qualname,
        help=help,
        default=str(default),
    )
    group.addoption(
        f"--logot-{name.replace('_', '-')}",
        dest=qualname,
        metavar=name.upper(),
        help=help,
    )
