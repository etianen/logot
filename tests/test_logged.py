from __future__ import annotations

import logging

from logot import logged


def record(level: int, msg: str) -> logging.LogRecord:
    return logging.LogRecord(name="logot", level=level, pathname=__file__, lineno=0, msg=msg, args=(), exc_info=None)


def assert_reduce(log: logged.Logged | None, *records: logging.LogRecord) -> None:
    for record in records:
        assert log is not None
        log = log._reduce(record)
    assert log is None


def test_log_record_logged_eq_pass() -> None:
    assert logged.info("foo bar") == logged.info("foo bar")


def test_log_record_logged_eq_fail() -> None:
    assert logged.info("foo bar") != logged.debug("foo bar")
    assert logged.info("foo bar") != logged.info("foo")


def test_log_record_logged_repr() -> None:
    assert repr(logged.log(logging.DEBUG, "foo bar")) == "log('DEBUG', 'foo bar')"
    assert repr(logged.debug("foo bar")) == "log('DEBUG', 'foo bar')"
    assert repr(logged.info("foo bar")) == "log('INFO', 'foo bar')"
    assert repr(logged.warning("foo bar")) == "log('WARNING', 'foo bar')"
    assert repr(logged.error("foo bar")) == "log('ERROR', 'foo bar')"
    assert repr(logged.critical("foo bar")) == "log('CRITICAL', 'foo bar')"


def test_log_record_logged_str() -> None:
    assert str(logged.log(logging.DEBUG, "foo bar")) == "[DEBUG] foo bar"
    assert str(logged.debug("foo bar")) == "[DEBUG] foo bar"
    assert str(logged.info("foo bar")) == "[INFO] foo bar"
    assert str(logged.warning("foo bar")) == "[WARNING] foo bar"
    assert str(logged.error("foo bar")) == "[ERROR] foo bar"
    assert str(logged.critical("foo bar")) == "[CRITICAL] foo bar"


def test_log_record_logged_reduce() -> None:
    assert_reduce(logged.info("foo bar"), record(logging.INFO, "foo bar"))
