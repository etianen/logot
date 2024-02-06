# from __future__ import annotations


# class _Capturing:
#     __slots__ = ("_logot", "_handler", "_logger", "_prev_levelno")

#     def __init__(self, logot: Logot, handler: logging.Handler, *, logger: logging.Logger) -> None:
#         self._logot = logot
#         self._handler = handler
#         self._logger = logger

#     def __enter__(self) -> Logot:
#         # If the logger is less verbose than the handler, force it to the necessary verboseness.
#         self._prev_levelno = self._logger.level
#         if self._handler.level < self._logger.level:
#             self._logger.setLevel(self._handler.level)
#         # Add the handler.
#         self._logger.addHandler(self._handler)
#         return self._logot

#     def __exit__(
#         self,
#         exc_type: type[BaseException] | None,
#         exc_value: BaseException | None,
#         traceback: TracebackType | None,
#     ) -> None:
#         # Remove the handler.
#         self._logger.removeHandler(self._handler)
#         # Restore the previous level.
#         self._logger.setLevel(self._prev_levelno)


# class _Handler(logging.Handler):
#     __slots__ = ("_logot",)

#     def __init__(self, level: str | int, logot: Logot) -> None:
#         super().__init__(level)
#         self._logot = logot

#     def emit(self, record: logging.LogRecord) -> None:
#         captured = Captured(record.levelname, record.getMessage(), levelno=record.levelno)
#         self._logot.capture(captured)
