from __future__ import annotations

from typing import cast

import pytest

from logot._exc_info import exc_info_matcher
from logot._typing import ExcInfo


def test_repr() -> None:
    assert repr(exc_info_matcher(True)) == "exc_info=True"
    assert repr(exc_info_matcher(False)) == "exc_info=False"
    assert repr(exc_info_matcher(None)) == "exc_info=None"


def test_invalid() -> None:
    with pytest.raises(TypeError) as ex:
        exc_info_matcher(cast(ExcInfo, 1.5))
    assert str(ex.value) == "Invalid exc_info: 1.5"
