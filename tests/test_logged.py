from __future__ import annotations

import logging

from logot import Captured, Logged, logged
from tests import lines


def assert_reduce(logged: Logged | None, *captured_items: Captured) -> None:
    for captured in captured_items:
        # The `Logged` should not have been fully reduced.
        assert logged is not None
        logged = logged._reduce(captured)
    # Once captured items are consumed, the `Logged` should have been fully-reduced.
    assert logged is None


def test_record_logged_eq_pass() -> None:
    assert logged.info("foo bar") == logged.info("foo bar")


def test_record_logged_eq_fail() -> None:
    # Different levels are not equal.
    assert logged.info("foo bar") != logged.debug("foo bar")
    # Different messages are not equal.
    assert logged.info("foo bar") != logged.info("foo")


def test_record_logged_repr() -> None:
    assert repr(logged.log(logging.DEBUG, "foo bar")) == "log('DEBUG', 'foo bar')"
    assert repr(logged.debug("foo bar")) == "log('DEBUG', 'foo bar')"
    assert repr(logged.info("foo bar")) == "log('INFO', 'foo bar')"
    assert repr(logged.warning("foo bar")) == "log('WARNING', 'foo bar')"
    assert repr(logged.error("foo bar")) == "log('ERROR', 'foo bar')"
    assert repr(logged.critical("foo bar")) == "log('CRITICAL', 'foo bar')"


def test_record_logged_str() -> None:
    assert str(logged.log(logging.DEBUG, "foo bar")) == "[DEBUG] foo bar"
    assert str(logged.debug("foo bar")) == "[DEBUG] foo bar"
    assert str(logged.info("foo bar")) == "[INFO] foo bar"
    assert str(logged.warning("foo bar")) == "[WARNING] foo bar"
    assert str(logged.error("foo bar")) == "[ERROR] foo bar"
    assert str(logged.critical("foo bar")) == "[CRITICAL] foo bar"


def test_record_logged_reduce() -> None:
    assert_reduce(
        logged.info("foo bar"),
        Captured(logging.INFO, "boom!"),  # Non-matching.
        Captured(logging.DEBUG, "foo bar"),  # Non-matching.
        Captured(logging.INFO, "foo bar"),  # Matching.
    )


def test_ordered_all_logged_eq_pass() -> None:
    assert (logged.info("foo") >> logged.info("bar")) == (logged.info("foo") >> logged.info("bar"))


def test_ordered_all_logged_eq_fail() -> None:
    # Different orderings are not equal.
    assert (logged.info("foo") >> logged.info("bar")) != (logged.info("bar") >> logged.info("foo"))
    # Different operators are not equal.
    assert (logged.info("foo") >> logged.info("bar")) != (logged.info("foo") & logged.info("bar"))


def test_ordered_all_logged_repr() -> None:
    # Composed `Logged` are flattened from the left.
    assert (
        repr((logged.info("foo") >> logged.info("bar")) >> logged.info("baz"))
        == "(log('INFO', 'foo') >> log('INFO', 'bar') >> log('INFO', 'baz'))"
    )
    # Composed `Logged` are flattened from the right.
    assert (
        repr(logged.info("foo") >> (logged.info("bar") >> logged.info("baz")))
        == "(log('INFO', 'foo') >> log('INFO', 'bar') >> log('INFO', 'baz'))"
    )
    # Composed `Logged` are flattened from the left and right.
    assert (
        repr((logged.info("foo") >> logged.info("bar")) >> (logged.info("baz") >> logged.info("bat")))
        == "(log('INFO', 'foo') >> log('INFO', 'bar') >> log('INFO', 'baz') >> log('INFO', 'bat'))"
    )


def test_ordered_all_logged_str() -> None:
    assert str(logged.info("foo") >> logged.info("bar")) == lines(
        "[INFO] foo",
        "[INFO] bar",
    )
    # Indentation is sane with multiple nested composed `Logged`.
    assert str(
        (logged.info("foo1") & logged.info("foo2"))
        >> (
            (logged.info("bar1a") | logged.info("bar1b"))
            & ((logged.info("bar2a1") >> logged.info("bar2a2")) | (logged.info("bar2b1") >> logged.info("bar2b2")))
        )
    ) == lines(
        "Unordered:",
        "- [INFO] foo1",
        "- [INFO] foo2",
        "Unordered:",
        "- Any:",
        "  - [INFO] bar1a",
        "  - [INFO] bar1b",
        "- Any:",
        "  - [INFO] bar2a1",
        "    [INFO] bar2a2",
        "  - [INFO] bar2b1",
        "    [INFO] bar2b2",
    )


def test_ordered_all_logged_reduce() -> None:
    assert_reduce(
        logged.info("foo") >> logged.info("bar") >> logged.info("baz"),
        Captured(logging.INFO, "boom!"),  # Non-matching.
        Captured(logging.INFO, "baz"),  # Non-matching.
        Captured(logging.INFO, "bar"),  # Non-matching.
        Captured(logging.INFO, "foo"),  # Matching.
        Captured(logging.INFO, "foo"),  # Non-matching.
        Captured(logging.INFO, "bar"),  # Matching.
        Captured(logging.INFO, "baz"),  # Matching.
    )
    assert_reduce(
        (logged.info("foo1") & logged.info("foo2")) >> (logged.info("bar1") & logged.info("bar2")),
        Captured(logging.INFO, "boom!"),  # Non-matching.
        Captured(logging.INFO, "bar2"),  # Non-matching.
        Captured(logging.INFO, "foo2"),  # Matching.
        Captured(logging.INFO, "bar1"),  # Non-matching.
        Captured(logging.INFO, "foo1"),  # Matching.
        Captured(logging.INFO, "bar2"),  # Matching.
        Captured(logging.INFO, "bar1"),  # Matching.
    )


def test_unordered_all_logged_eq_pass() -> None:
    assert (logged.info("foo") & logged.info("bar")) == (logged.info("foo") & logged.info("bar"))


def test_unordered_all_logged_eq_fail() -> None:
    # Different orderings are not equal.
    assert (logged.info("foo") & logged.info("bar")) != (logged.info("bar") & logged.info("foo"))
    # Different operators are not equal.
    assert (logged.info("foo") & logged.info("bar")) != (logged.info("foo") >> logged.info("bar"))


def test_unordered_all_logged_repr() -> None:
    # Composed `Logged` are flattened from the left.
    assert (
        repr((logged.info("foo") & logged.info("bar")) & logged.info("baz"))
        == "(log('INFO', 'foo') & log('INFO', 'bar') & log('INFO', 'baz'))"
    )
    # Composed `Logged` are flattened from the right.
    assert (
        repr(logged.info("foo") & (logged.info("bar") & logged.info("baz")))
        == "(log('INFO', 'foo') & log('INFO', 'bar') & log('INFO', 'baz'))"
    )
    # Composed `Logged` are flattened from the left and right.
    assert (
        repr((logged.info("foo") & logged.info("bar")) & (logged.info("baz") & logged.info("bat")))
        == "(log('INFO', 'foo') & log('INFO', 'bar') & log('INFO', 'baz') & log('INFO', 'bat'))"
    )


def test_unordered_all_logged_str() -> None:
    assert str(logged.info("foo") & logged.info("bar")) == lines(
        "Unordered:",
        "- [INFO] foo",
        "- [INFO] bar",
    )
    # Indentation is sane with multiple nested composed `Logged`.
    assert str(
        (logged.info("foo1") >> logged.info("foo2"))
        & (
            (logged.info("bar1a") | logged.info("bar1b"))
            >> ((logged.info("bar2a1") >> logged.info("bar2a2")) | (logged.info("bar2b1") >> logged.info("bar2b2")))
        )
    ) == lines(
        "Unordered:",
        "- [INFO] foo1",
        "  [INFO] foo2",
        "- Any:",
        "  - [INFO] bar1a",
        "  - [INFO] bar1b",
        "  Any:",
        "  - [INFO] bar2a1",
        "    [INFO] bar2a2",
        "  - [INFO] bar2b1",
        "    [INFO] bar2b2",
    )


def test_unordered_all_logged_reduce() -> None:
    assert_reduce(
        logged.info("foo") & logged.info("bar") & logged.info("baz"),
        Captured(logging.INFO, "boom!"),  # Non-matching.
        Captured(logging.INFO, "baz"),  # Matching.
        Captured(logging.INFO, "baz"),  # Non-matching.
        Captured(logging.INFO, "bar"),  # Matching.
        Captured(logging.INFO, "foo"),  # Matching.
    )
    assert_reduce(
        (logged.info("foo1") >> logged.info("foo2")) & (logged.info("bar1") >> logged.info("bar2")),
        Captured(logging.INFO, "boom!"),  # Non-matching.
        Captured(logging.INFO, "bar2"),  # Non-matching.
        Captured(logging.INFO, "foo2"),  # Non-matching.
        Captured(logging.INFO, "bar1"),  # Matching.
        Captured(logging.INFO, "foo1"),  # Matching.
        Captured(logging.INFO, "foo2"),  # Matching.
        Captured(logging.INFO, "bar2"),  # Matching.
    )


def test_any_logged_eq_pass() -> None:
    assert (logged.info("foo") | logged.info("bar")) == (logged.info("foo") | logged.info("bar"))


def test_any_logged_eq_fail() -> None:
    # Different orderings are not equal.
    assert (logged.info("foo") | logged.info("bar")) != (logged.info("bar") | logged.info("foo"))
    # Different operators are not equal.
    assert (logged.info("foo") | logged.info("bar")) != (logged.info("foo") >> logged.info("bar"))


def test_any_logged_repr() -> None:
    # Composed `Logged` are flattened from the left.
    assert (
        repr((logged.info("foo") | logged.info("bar")) | logged.info("baz"))
        == "(log('INFO', 'foo') | log('INFO', 'bar') | log('INFO', 'baz'))"
    )
    # Composed `Logged` are flattened from the right.
    assert (
        repr(logged.info("foo") | (logged.info("bar") | logged.info("baz")))
        == "(log('INFO', 'foo') | log('INFO', 'bar') | log('INFO', 'baz'))"
    )
    # Composed `Logged` are flattened from the left and right.
    assert (
        repr((logged.info("foo") | logged.info("bar")) | (logged.info("baz") | logged.info("bat")))
        == "(log('INFO', 'foo') | log('INFO', 'bar') | log('INFO', 'baz') | log('INFO', 'bat'))"
    )


def test_any_logged_str() -> None:
    assert str(logged.info("foo") | logged.info("bar")) == lines(
        "Any:",
        "- [INFO] foo",
        "- [INFO] bar",
    )
    # Indentation is sane with multiple nested composed `Logged`.
    assert str(
        (logged.info("foo1") >> logged.info("foo2"))
        | (
            (logged.info("bar1a") & logged.info("bar1b"))
            >> ((logged.info("bar2a1") >> logged.info("bar2a2")) & (logged.info("bar2b1") >> logged.info("bar2b2")))
        )
    ) == lines(
        "Any:",
        "- [INFO] foo1",
        "  [INFO] foo2",
        "- Unordered:",
        "  - [INFO] bar1a",
        "  - [INFO] bar1b",
        "  Unordered:",
        "  - [INFO] bar2a1",
        "    [INFO] bar2a2",
        "  - [INFO] bar2b1",
        "    [INFO] bar2b2",
    )


def test_any_logged_reduce() -> None:
    assert_reduce(
        logged.info("foo") | logged.info("bar") | logged.info("baz"),
        Captured(logging.INFO, "boom!"),  # Non-matching.
        Captured(logging.INFO, "bar"),  # Matching.
    )
    assert_reduce(
        (logged.info("foo1") >> logged.info("foo2")) | (logged.info("bar1") >> logged.info("bar2")),
        Captured(logging.INFO, "boom!"),  # Non-matching.
        Captured(logging.INFO, "bar2"),  # Non-matching.
        Captured(logging.INFO, "foo2"),  # Non-matching.
        Captured(logging.INFO, "bar1"),  # Matching.
        Captured(logging.INFO, "foo1"),  # Matching.
        Captured(logging.INFO, "foo2"),  # Matching.
    )
