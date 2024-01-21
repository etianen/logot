from __future__ import annotations

from logot import logged


def test_log_record_logged_eq_pass() -> None:
    assert logged.info("foo bar") == logged.info("foo bar")


def test_log_record_logged_eq_fail() -> None:
    assert logged.info("foo bar") != logged.debug("foo bar")
    assert logged.info("foo bar") != logged.info("foo")


def test_log_record_logged_repr() -> None:
    assert repr(logged.info("foo bar")) == "log('INFO', 'foo bar')"
