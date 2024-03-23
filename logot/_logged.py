from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod

from logot._capture import Captured
from logot._level import CRITICAL_MATCHER, DEBUG_MATCHER, ERROR_MATCHER, INFO_MATCHER, WARNING_MATCHER, level_matcher
from logot._match import Matcher
from logot._msg import msg_matcher
from logot._name import name_matcher
from logot._typing import MISSING, Level, Name


class Logged(ABC):
    """
    A :doc:`log pattern </log-pattern-matching>` passed to :meth:`Logot.wait_for`, :meth:`Logot.await_for` and related
    APIs.

    .. important::

        This is an abstract class and cannot be instantiated. Use the helpers in :mod:`logot.logged` to create log
        patterns.

        :class:`Logged` instances are immutable and can be reused between tests.

    .. seealso::

        See :doc:`/log-pattern-matching` usage guide.
    """

    __slots__ = ()

    def __rshift__(self, logged: Logged) -> Logged:
        return _OrderedAllLogged.from_compose(self, logged)

    def __and__(self, logged: Logged) -> Logged:
        return _UnorderedAllLogged.from_compose(self, logged)

    def __or__(self, logged: Logged) -> Logged:
        return _AnyLogged.from_compose(self, logged)

    def __str__(self) -> str:
        return self._str(indent="")

    @abstractmethod
    def reduce(self, captured: Captured) -> Logged | None:
        """
        Reduces this :doc:`log pattern </log-pattern-matching>` using the given :class:`Captured` log.

        - No match - The same :doc:`log pattern </log-pattern-matching>` is returned.
        - Partial match - A smaller :doc:`log pattern </log-pattern-matching>` is returned.
        - Full match - :data:`None` is returned.

        .. note::

            This method is for building high-level log assertions. It is not generally used when writing tests.

        :param captured: The :class:`Captured` log.
        """
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def _str(self, *, indent: str) -> str:
        raise NotImplementedError


def log(level: Level, msg: str, *, name: Name = MISSING) -> Logged:
    """
    Creates a :doc:`log pattern </log-pattern-matching>` representing a log record at the given ``level`` with the given
    ``msg``.

    :param level: A log level name (e.g. ``"DEBUG"``) or numeric level (e.g. :data:`logging.DEBUG`).
    :param msg: A log :doc:`message pattern </log-message-matching>`.
    :param name: An optional logger name.
    """
    return _log(level_matcher(level), msg, name=name)


def debug(msg: str, *, name: Name = MISSING) -> Logged:
    """
    Creates a :doc:`log pattern </log-pattern-matching>` representing a log record at ``DEBUG`` level with the given
    ``msg``.

    :param msg: A log :doc:`message pattern </log-message-matching>`.
    :param name: An optional logger name.
    """
    return _log(DEBUG_MATCHER, msg, name=name)


def info(msg: str, *, name: Name = MISSING) -> Logged:
    """
    Creates a :doc:`log pattern </log-pattern-matching>` representing a log record at ``INFO`` level with the given
    ``msg``.

    :param msg: A log :doc:`message pattern </log-message-matching>`.
    :param name: An optional logger name.
    """
    return _log(INFO_MATCHER, msg, name=name)


def warning(msg: str, *, name: Name = MISSING) -> Logged:
    """
    Creates a :doc:`log pattern </log-pattern-matching>` representing a log record at ``WARNING`` level with the given
    ``msg``.

    :param msg: A log :doc:`message pattern </log-message-matching>`.
    :param name: An optional logger name.
    """
    return _log(WARNING_MATCHER, msg, name=name)


def error(msg: str, *, name: Name = MISSING) -> Logged:
    """
    Creates a :doc:`log pattern </log-pattern-matching>` representing a log record at ``ERROR`` level with the given
    ``msg``.

    :param msg: A log :doc:`message pattern </log-message-matching>`.
    :param name: An optional logger name.
    """
    return _log(ERROR_MATCHER, msg, name=name)


def critical(msg: str, *, name: Name = MISSING) -> Logged:
    """
    Creates a :doc:`log pattern </log-pattern-matching>` representing a log record at ``CRITICAL`` level with the given
    ``msg``.

    :param msg: A log :doc:`message pattern </log-message-matching>`.
    :param name: An optional logger name.
    """
    return _log(CRITICAL_MATCHER, msg, name=name)


def _log(level_matcher: Matcher, msg: str, *, name: Name) -> _MatcherLogged:
    matchers = [level_matcher, msg_matcher(msg)]
    if name is not MISSING:
        matchers.append(name_matcher(name))
    return _MatcherLogged((*matchers,))


@dataclasses.dataclass(frozen=True, repr=False)
class _MatcherLogged(Logged):
    __slots__ = ("matchers",)
    matchers: tuple[Matcher, ...]

    def reduce(self, captured: Captured) -> Logged | None:
        # Handle full reduction.
        if all(matcher.match(captured) for matcher in self.matchers):
            return None
        # Handle no reduction.
        return self

    def __repr__(self) -> str:
        matchers_repr = ", ".join(map(repr, self.matchers))
        return f"log({matchers_repr})"

    def _str(self, *, indent: str) -> str:
        return " ".join(map(str, self.matchers))


@dataclasses.dataclass(frozen=True, repr=False)
class _ComposedLogged(Logged):
    __slots__ = ("logged_items",)
    logged_items: tuple[Logged, ...]

    def __post_init__(self) -> None:
        assert len(self.logged_items) > 1

    @classmethod
    def from_compose(cls, logged_a: Logged, logged_b: Logged) -> Logged:
        # If possible, flatten nested logged items of the same type.
        if isinstance(logged_a, cls):
            if isinstance(logged_b, cls):
                return cls((*logged_a.logged_items, *logged_b.logged_items))
            return cls((*logged_a.logged_items, logged_b))
        if isinstance(logged_b, cls):
            return cls((logged_a, *logged_b.logged_items))
        # Wrap the logged items without flattening.
        return cls((logged_a, logged_b))

    @classmethod
    def from_reduce(cls, logged_items: tuple[Logged, ...]) -> Logged | None:
        assert logged_items
        # If there is a single logged item, do not wrap it.
        if len(logged_items) == 1:
            return logged_items[0]
        # Wrap the logged items.
        return cls(logged_items)


class _OrderedAllLogged(_ComposedLogged):
    __slots__ = ()

    def reduce(self, captured: Captured) -> Logged | None:
        logged = self.logged_items[0]
        reduced = logged.reduce(captured)
        # Handle full reduction.
        if reduced is None:
            return _OrderedAllLogged.from_reduce(self.logged_items[1:])
        # Handle partial reduction.
        if reduced is not logged:
            return _OrderedAllLogged((reduced, *self.logged_items[1:]))
        # Handle no reduction.
        return self

    def __repr__(self) -> str:
        return f"({' >> '.join(map(repr, self.logged_items))})"

    def _str(self, *, indent: str) -> str:
        return f"\n{indent}".join(logged._str(indent=indent) for logged in self.logged_items)


class _UnorderedAllLogged(_ComposedLogged):
    __slots__ = ()

    def reduce(self, captured: Captured) -> Logged | None:
        for n, logged in enumerate(self.logged_items):
            reduced = logged.reduce(captured)
            # Handle full reduction.
            if reduced is None:
                return _UnorderedAllLogged.from_reduce((*self.logged_items[:n], *self.logged_items[n + 1 :]))
            # Handle partial reduction.
            if reduced is not logged:
                return _UnorderedAllLogged((*self.logged_items[:n], reduced, *self.logged_items[n + 1 :]))
        # Handle no reduction.
        return self

    def __repr__(self) -> str:
        return f"({' & '.join(map(repr, self.logged_items))})"

    def _str(self, *, indent: str) -> str:
        nested_indent = indent + "  "
        logged_items_str = "".join(f"\n{indent}- {logged._str(indent=nested_indent)}" for logged in self.logged_items)
        return f"Unordered:{logged_items_str}"


class _AnyLogged(_ComposedLogged):
    __slots__ = ()

    def reduce(self, captured: Captured) -> Logged | None:
        for n, logged in enumerate(self.logged_items):
            reduced = logged.reduce(captured)
            # Handle full reduction.
            if reduced is None:
                return None
            # Handle partial reduction.
            if reduced is not logged:
                return _AnyLogged((*self.logged_items[:n], reduced, *self.logged_items[n + 1 :]))
        # Handle no reduction.
        return self

    def __repr__(self) -> str:
        return f"({' | '.join(map(repr, self.logged_items))})"

    def _str(self, *, indent: str) -> str:
        nested_indent = indent + "  "
        logged_items_str = "".join(f"\n{indent}- {logged._str(indent=nested_indent)}" for logged in self.logged_items)
        return f"Any:{logged_items_str}"
