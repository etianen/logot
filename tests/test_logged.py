from __future__ import annotations

from logot import Captured, Logged, logged
from tests import lines


def assert_reduce(logged: Logged | None, *captured_items: Captured) -> None:
    for captured in captured_items:
        # The `Logged` should not have been fully reduced.
        assert logged is not None
        logged = logged.reduce(captured)
    # Once captured items are consumed, the `Logged` should have been fully-reduced.
    assert logged is None


def test_matcher_logged_eq_pass() -> None:
    assert logged.info("foo bar") == logged.info("foo bar")


def test_matcher_logged_eq_fail() -> None:
    # Different levels are not equal.
    assert logged.info("foo bar") != logged.debug("foo bar")
    # Different messages are not equal.
    assert logged.info("foo bar") != logged.info("foo")


def test_matcher_logged_repr() -> None:
    assert repr(logged.log(10, "foo bar")) == "log(10, 'foo bar')"
    assert repr(logged.log("DEBUG", "foo bar")) == "log('DEBUG', 'foo bar')"
    assert repr(logged.debug("foo bar")) == "log('DEBUG', 'foo bar')"
    assert repr(logged.info("foo bar")) == "log('INFO', 'foo bar')"
    assert repr(logged.warning("foo bar")) == "log('WARNING', 'foo bar')"
    assert repr(logged.error("foo bar")) == "log('ERROR', 'foo bar')"
    assert repr(logged.critical("foo bar")) == "log('CRITICAL', 'foo bar')"


def test_matcher_logged_str() -> None:
    assert str(logged.log(10, "foo bar")) == "[Level 10] foo bar"
    assert str(logged.log("DEBUG", "foo bar")) == "[DEBUG] foo bar"
    assert str(logged.debug("foo bar")) == "[DEBUG] foo bar"
    assert str(logged.info("foo bar")) == "[INFO] foo bar"
    assert str(logged.warning("foo bar")) == "[WARNING] foo bar"
    assert str(logged.error("foo bar")) == "[ERROR] foo bar"
    assert str(logged.critical("foo bar")) == "[CRITICAL] foo bar"


def test_matcher_logged_reduce() -> None:
    # Test `str` level.
    assert_reduce(
        logged.log("INFO", "foo bar"),
        Captured("INFO", "boom!"),  # Non-matching.
        Captured("DEBUG", "foo bar"),  # Non-matching.
        Captured("INFO", "foo bar"),  # Matching.
    )
    # Test `int` level.
    assert_reduce(
        logged.log(20, "foo bar"),
        Captured("INFO", "foo bar"),  # Non-matching (needs levelno).
        Captured("INFO", "foo bar", levelno=20),  # Matching.
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
        Captured("INFO", "boom!"),  # Non-matching.
        Captured("INFO", "baz"),  # Non-matching.
        Captured("INFO", "bar"),  # Non-matching.
        Captured("INFO", "foo"),  # Matching.
        Captured("INFO", "foo"),  # Non-matching.
        Captured("INFO", "bar"),  # Matching.
        Captured("INFO", "baz"),  # Matching.
    )
    assert_reduce(
        (logged.info("foo1") & logged.info("foo2")) >> (logged.info("bar1") & logged.info("bar2")),
        Captured("INFO", "boom!"),  # Non-matching.
        Captured("INFO", "bar2"),  # Non-matching.
        Captured("INFO", "foo2"),  # Matching.
        Captured("INFO", "bar1"),  # Non-matching.
        Captured("INFO", "foo1"),  # Matching.
        Captured("INFO", "bar2"),  # Matching.
        Captured("INFO", "bar1"),  # Matching.
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
        Captured("INFO", "boom!"),  # Non-matching.
        Captured("INFO", "baz"),  # Matching.
        Captured("INFO", "baz"),  # Non-matching.
        Captured("INFO", "bar"),  # Matching.
        Captured("INFO", "foo"),  # Matching.
    )
    assert_reduce(
        (logged.info("foo1") >> logged.info("foo2")) & (logged.info("bar1") >> logged.info("bar2")),
        Captured("INFO", "boom!"),  # Non-matching.
        Captured("INFO", "bar2"),  # Non-matching.
        Captured("INFO", "foo2"),  # Non-matching.
        Captured("INFO", "bar1"),  # Matching.
        Captured("INFO", "foo1"),  # Matching.
        Captured("INFO", "foo2"),  # Matching.
        Captured("INFO", "bar2"),  # Matching.
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
        Captured("INFO", "boom!"),  # Non-matching.
        Captured("INFO", "bar"),  # Matching.
    )
    assert_reduce(
        (logged.info("foo1") >> logged.info("foo2")) | (logged.info("bar1") >> logged.info("bar2")),
        Captured("INFO", "boom!"),  # Non-matching.
        Captured("INFO", "bar2"),  # Non-matching.
        Captured("INFO", "foo2"),  # Non-matching.
        Captured("INFO", "bar1"),  # Matching.
        Captured("INFO", "foo1"),  # Matching.
        Captured("INFO", "foo2"),  # Matching.
    )
