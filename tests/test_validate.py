from __future__ import annotations

import logging
from typing import cast

import pytest

from logot._validate import validate_level, validate_logger, validate_timeout
from tests import logger


def test_validate_level_str_pass() -> None:
    assert validate_level("INFO") == "INFO"


def test_validate_level_int_pass() -> None:
    assert validate_level(20) == 20


def test_validate_level_type_fail() -> None:
    with pytest.raises(TypeError) as ex:
        validate_level(cast(int, 1.5))
    assert str(ex.value) == "Invalid level: 1.5"


def test_validate_logger_none_pass() -> None:
    assert validate_logger(None) is logging.getLogger()


def test_validate_logger_str_pass() -> None:
    assert validate_logger("logot") is logger


def test_validate_logger_logger_pass() -> None:
    assert validate_logger(logging.getLogger("logot")) is logger


def test_validate_logger_type_fail() -> None:
    with pytest.raises(TypeError) as ex:
        validate_logger(cast(str, 1.5))
    assert str(ex.value) == "Invalid logger: 1.5"


def test_validate_timeout_numeric_pass() -> None:
    assert validate_timeout(1.0) == 1.0


def test_validate_timeout_numeric_fail() -> None:
    with pytest.raises(ValueError) as ex:
        validate_timeout(-1.0)
    assert str(ex.value) == "Invalid timeout: -1.0"


def test_validate_timeout_type_fail() -> None:
    with pytest.raises(TypeError) as ex:
        validate_timeout(cast(float, "boom!"))
    assert str(ex.value) == "Invalid timeout: 'boom!'"
