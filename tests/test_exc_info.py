from __future__ import annotations

from typing import cast

import pytest

from logot._exc_info import exc_info_matcher
from logot._typing import ExcInfo
from tests import ExampleException


def test_repr() -> None:
    assert repr(exc_info_matcher(True)) == "exc_info=True"
    assert repr(exc_info_matcher(False)) == "exc_info=False"
    ex = ExampleException("foo")
    assert repr(exc_info_matcher(ex)) == f"exc_info={ex!r}"
    assert repr(exc_info_matcher(None)) == "exc_info=None"


def test_invalid() -> None:
    with pytest.raises(TypeError) as ex:
        exc_info_matcher(cast(ExcInfo, 1.5))
    assert str(ex.value) == "Invalid exc_info: 1.5"
