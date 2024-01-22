from __future__ import annotations

import logging
from typing import cast

import pytest

from logot._util import to_levelno, to_logger, to_timeout


def test_to_levelno_int_pass() -> None:
    assert to_levelno(logging.INFO) == logging.INFO


def test_to_levelno_int_fail() -> None:
    with pytest.raises(ValueError) as ex:
        to_levelno(9999)
    assert str(ex.value) == "Unknown level: 9999"


def test_to_levelno_str_pass() -> None:
    assert to_levelno("INFO") == logging.INFO


def test_to_levelno_str_fail() -> None:
    with pytest.raises(ValueError) as ex:
        to_levelno("BOOM")
    assert str(ex.value) == "Unknown level: 'BOOM'"


def test_to_levelno_type_fail() -> None:
    with pytest.raises(TypeError) as ex:
        to_levelno(cast(int, 1.5))
    assert str(ex.value) == "Invalid level: 1.5"


def test_to_logger_none_pass() -> None:
    assert to_logger(None) is logging.getLogger()


def test_to_logger_str_pass() -> None:
    assert to_logger("logot") is logging.getLogger("logot")


def test_to_logger_logger_pass() -> None:
    assert to_logger(logging.getLogger("logot")) is logging.getLogger("logot")


def test_to_logger_type_fail() -> None:
    with pytest.raises(TypeError) as ex:
        to_logger(cast(str, 1.5))
    assert str(ex.value) == "Invalid logger: 1.5"


def test_to_timeout_numeric_pass() -> None:
    assert to_timeout(1.0) == 1.0


def test_to_timeout_numeric_fail() -> None:
    with pytest.raises(ValueError) as ex:
        to_timeout(-1.0)
    assert str(ex.value) == "Invalid timeout: -1.0"


def test_to_timeout_type_fail() -> None:
    with pytest.raises(TypeError) as ex:
        to_timeout(cast(float, "boom!"))
    assert str(ex.value) == "Invalid timeout: 'boom!'"
