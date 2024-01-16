from __future__ import annotations

import logging

import pytest

from logot._util import to_levelno


def test_check_level_int_pass() -> None:
    assert to_levelno(logging.INFO) == logging.INFO


def test_check_level_int_fail() -> None:
    with pytest.raises(ValueError) as ex:
        to_levelno(9999)
    assert str(ex.value) == "Unknown level: 9999"


def test_check_level_str_pass() -> None:
    assert to_levelno("INFO") == logging.INFO


def test_check_level_str_fail() -> None:
    with pytest.raises(ValueError) as ex:
        to_levelno("BOOM")
    assert str(ex.value) == "Unknown level: 'BOOM'"


def test_check_level_type_fail() -> None:
    with pytest.raises(TypeError) as ex:
        to_levelno(1.5)  # type: ignore[arg-type]
    assert str(ex.value) == "Invalid level: 1.5"
