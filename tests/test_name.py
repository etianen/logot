from __future__ import annotations

from typing import cast

import pytest

from logot._name import name_matcher
from logot._typing import Name


def test_repr() -> None:
    assert repr(name_matcher(None)) == "name=None"
    assert repr(name_matcher("tests")) == "name='tests'"


def test_invalid() -> None:
    with pytest.raises(TypeError) as ex:
        name_matcher(cast(Name, 1.5))
    assert str(ex.value) == "Invalid name: 1.5"
