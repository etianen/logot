from __future__ import annotations

from collections.abc import Generator

import pytest

from logot._logot import Logot


@pytest.fixture()
def logot() -> Generator[Logot, None, None]:
    with Logot().capturing() as logot:
        yield logot
