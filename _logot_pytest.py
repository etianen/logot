from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    # Don't import `logot` until the fixture runs.
    # This avoids problem with pytest coverage reporting.
    from logot import Logot


@pytest.fixture()
def logot() -> Generator[Logot, None, None]:
    from logot import Logot

    with Logot().capturing() as logot:
        yield logot
