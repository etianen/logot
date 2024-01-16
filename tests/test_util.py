from __future__ import annotations

import logging

import pytest

from logot._util import _check_level


def test_check_level_int_pass() -> None:
    assert _check_level(logging.INFO) == logging.INFO


def test_check_level_int_fail() -> None:
    with pytest.raises(ValueError) as ex:
        _check_level(9999)
    assert str(ex.value) == "Unknown level: 9999"


def test_check_level_str_pass() -> None:
    assert _check_level("INFO") == logging.INFO


def test_check_level_str_fail() -> None:
    with pytest.raises(ValueError) as ex:
        _check_level("BOOM")
    assert str(ex.value) == "Unknown level: 'BOOM'"


def test_check_level_type_fail() -> None:
    with pytest.raises(TypeError) as ex:
        _check_level(1.5)  # type: ignore[arg-type]
    assert str(ex.value) == "Invalid level: 1.5"
