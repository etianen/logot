from __future__ import annotations

from collections.abc import Generator
from typing import Any, Callable

import pytest

from logot._logot import Logot
from logot._types import T

MISSING: Any = object()


def pytest_addoption(parser: pytest.Parser, pluginmanager: pytest.PytestPluginManager) -> None:
    group = parser.getgroup("logot")
    _addoption(
        parser,
        group,
        name="level",
        help="Level used for automatic `logot` log capturing",
    )
    _addoption(
        parser,
        group,
        name="logger",
        help="Logger used for automatic `logot` log capturing",
    )
    _addoption(
        parser,
        group,
        name="timeout",
        help="Default timeout (in seconds) for `logot`",
    )


@pytest.fixture()
def logot() -> Generator[Logot, None, None]:
    with Logot().capturing() as logot:
        yield logot


@pytest.fixture()
def logot_level(request: pytest.FixtureRequest) -> str:
    return _getoption(request.config, name="level", parser=str, default=Logot.DEFAULT_LEVEL)


def _addoption(parser: pytest.Parser, group: pytest.OptionGroup, *, name: str, help: str) -> None:
    qualname = f"logot_{name}"
    parser.addini(qualname, default=MISSING, help=help)
    group.addoption(
        f"--logot-{name.replace('_', '-')}",
        dest=qualname,
        metavar=name.upper(),
        help=help,
    )


def _getoption(request: pytest.FixtureRequest, *, name: str, parser: Callable[[str], T], default: T) -> T:
    qualname = f"logot_{name}"
    # Try to get the value from the command line, followed by the config file.
    value: str = request.config.getoption(qualname, default=MISSING)
    if value is MISSING:
        value = request.config.getini(qualname)
        if value is MISSING:
            # Give up and return the default.
            return default
    # Parse and return the value.
    try:
        return parser(value)
    except (ValueError, TypeError) as ex:
        raise pytest.UsageError(f"Invalid {qualname}: {ex}")
