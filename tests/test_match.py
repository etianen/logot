from __future__ import annotations

import pytest

from logot._match import compile


@pytest.mark.parametrize(("pattern", "msg"), (("foo %s baz", "foo bar baz"),))
def test_match(pattern: str, msg: str) -> None:
    assert compile(pattern).match(msg) is not None
