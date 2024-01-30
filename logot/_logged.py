from __future__ import annotations

from abc import ABC, abstractmethod

from logot._captured import Captured
from logot._format import format_level, format_log
from logot._match import compile_matcher
from logot._validate import validate_level


class Logged(ABC):
    """
    A :doc:`log pattern </log-pattern-matching>` passed to :meth:`Logot.wait_for`, :meth:`Logot.await_for` and related
    APIs.

    .. important::

        :class:`Logged` instances are immutable and can be reused between tests.

    .. note::

        This is an abstract class and cannot be instantiated. Use the helpers in :mod:`logot.logged` to create log
        patterns.

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
    def __eq__(self, other: object) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def _reduce(self, captured: Captured) -> Logged | None:
        raise NotImplementedError

    @abstractmethod
    def _str(self, *, indent: str) -> str:
        raise NotImplementedError


def log(level: str | int, msg: str) -> Logged:
    """
    Creates a :doc:`log pattern </log-pattern-matching>` representing a log record at the given ``level`` with the given
    ``msg``.

    :param level: A log level name (e.g. ``"DEBUG"``) or numeric level (e.g. :data:`logging.DEBUG`).
    :param msg: A log :doc:`message pattern </log-message-matching>`.
    """
    return _RecordLogged(validate_level(level), msg)


def debug(msg: str) -> Logged:
    """
    Creates a :doc:`log pattern </log-pattern-matching>` representing a log record at ``DEBUG`` level with the given
    ``msg``.

    :param msg: A log :doc:`message pattern </log-message-matching>`.
    """
    return _RecordLogged("DEBUG", msg)


def info(msg: str) -> Logged:
    """
    Creates a :doc:`log pattern </log-pattern-matching>` representing a log record at ``INFO`` level with the given
    ``msg``.

    :param msg: A log :doc:`message pattern </log-message-matching>`.
    """
    return _RecordLogged("INFO", msg)


def warning(msg: str) -> Logged:
    """
    Creates a :doc:`log pattern </log-pattern-matching>` representing a log record at ``WARNING`` level with the given
    ``msg``.

    :param msg: A log :doc:`message pattern </log-message-matching>`.
    """
    return _RecordLogged("WARNING", msg)


def error(msg: str) -> Logged:
    """
    Creates a :doc:`log pattern </log-pattern-matching>` representing a log record at ``ERROR`` level with the given
    ``msg``.

    :param msg: A log :doc:`message pattern </log-message-matching>`.
    """
    return _RecordLogged("ERROR", msg)


def critical(msg: str) -> Logged:
    """
    Creates a :doc:`log pattern </log-pattern-matching>` representing a log record at ``CRITICAL`` level with the given
    ``msg``.

    :param msg: A log :doc:`message pattern </log-message-matching>`.
    """
    return _RecordLogged("CRITICAL", msg)


class _RecordLogged(Logged):
    __slots__ = ("_level", "_msg", "_matcher")

    def __init__(self, level: str | int, msg: str) -> None:
        self._level = level
        self._msg = msg
        self._matcher = compile_matcher(msg)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _RecordLogged) and other._level == self._level and other._msg == self._msg

    def __repr__(self) -> str:
        return f"log({self._level!r}, {self._msg!r})"

    def _reduce(self, captured: Captured) -> Logged | None:
        # Match `str` level.
        if isinstance(self._level, str):
            if self._level != captured.levelname:
                return self
        # Match `int` level.
        elif isinstance(self._level, int):
            if self._level != captured.levelno:
                return self
        else:  # pragma: no cover
            raise TypeError(f"Invalid level: {self._level!r}")
        # Match message.
        if not self._matcher(captured.msg):
            return self
        # We matched!
        return None

    def _str(self, *, indent: str) -> str:
        return format_log(format_level(self._level), self._msg)


class _ComposedLogged(Logged):
    __slots__ = ("_logged_items",)

    def __init__(self, logged_items: tuple[Logged, ...]) -> None:
        assert len(logged_items) > 1
        self._logged_items = logged_items

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other._logged_items == self._logged_items

    @classmethod
    def from_compose(cls, logged_a: Logged, logged_b: Logged) -> Logged:
        # If possible, flatten nested logged items of the same type.
        if isinstance(logged_a, cls):
            if isinstance(logged_b, cls):
                return cls((*logged_a._logged_items, *logged_b._logged_items))
            return cls((*logged_a._logged_items, logged_b))
        if isinstance(logged_b, cls):
            return cls((logged_a, *logged_b._logged_items))
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

    def __repr__(self) -> str:
        return f"({' >> '.join(map(repr, self._logged_items))})"

    def _reduce(self, captured: Captured) -> Logged | None:
        logged = self._logged_items[0]
        reduced = logged._reduce(captured)
        # Handle full reduction.
        if reduced is None:
            return _OrderedAllLogged.from_reduce(self._logged_items[1:])
        # Handle partial reduction.
        if reduced is not logged:
            return _OrderedAllLogged((reduced, *self._logged_items[1:]))
        # Handle no reduction.
        return self

    def _str(self, *, indent: str) -> str:
        return f"\n{indent}".join(logged._str(indent=indent) for logged in self._logged_items)


class _UnorderedAllLogged(_ComposedLogged):
    __slots__ = ()

    def __repr__(self) -> str:
        return f"({' & '.join(map(repr, self._logged_items))})"

    def _reduce(self, captured: Captured) -> Logged | None:
        for n, logged in enumerate(self._logged_items):
            reduced = logged._reduce(captured)
            # Handle full reduction.
            if reduced is None:
                return _UnorderedAllLogged.from_reduce((*self._logged_items[:n], *self._logged_items[n + 1 :]))
            # Handle partial reduction.
            if reduced is not logged:
                return _UnorderedAllLogged((*self._logged_items[:n], reduced, *self._logged_items[n + 1 :]))
        # Handle no reduction.
        return self

    def _str(self, *, indent: str) -> str:
        nested_indent = indent + "  "
        logged_items_str = "".join(f"\n{indent}- {logged._str(indent=nested_indent)}" for logged in self._logged_items)
        return f"Unordered:{logged_items_str}"


class _AnyLogged(_ComposedLogged):
    __slots__ = ()

    def __repr__(self) -> str:
        return f"({' | '.join(map(repr, self._logged_items))})"

    def _reduce(self, captured: Captured) -> Logged | None:
        for n, logged in enumerate(self._logged_items):
            reduced = logged._reduce(captured)
            # Handle full reduction.
            if reduced is None:
                return None
            # Handle partial reduction.
            if reduced is not logged:
                return _AnyLogged((*self._logged_items[:n], reduced, *self._logged_items[n + 1 :]))
        # Handle no reduction.
        return self

    def _str(self, *, indent: str) -> str:
        nested_indent = indent + "  "
        logged_items_str = "".join(f"\n{indent}- {logged._str(indent=nested_indent)}" for logged in self._logged_items)
        return f"Any:{logged_items_str}"
