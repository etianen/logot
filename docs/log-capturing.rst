Log capturing
=============

.. currentmodule:: logot

:mod:`logot` makes it easy to capture logs from the stdlib :mod:`logging` module:

.. code:: python

   with Logot().capturing() as logot:
      do_something()
      logot.assert_logged(logged.info("App started"))


Test framework integrations
---------------------------

Use a supported test framework integration for automatic log capturing in tests:

- :doc:`/using-pytest`
- :doc:`/using-unittest`


Capturing :mod:`logging` logs
-----------------------------

The :meth:`Logot.capturing` method defaults to capturing **all** records from the root logger. Customize this with the
``level`` and ``logger`` arguments to :meth:`Logot.capturing`:

.. code:: python

   with Logot().capturing(level=logging.WARNING, logger="app") as logot:
      do_something()
      logot.assert_logged(logged.info("App started"))

For advanced use-cases, multiple :meth:`Logot.capturing` calls on the same :class:`Logot` instance are supported. Be
careful to avoid capturing duplicate logs with overlapping calls to :meth:`Logot.capturing`!

.. seealso::

   See :class:`Logot` and :meth:`Logot.capturing` API reference.


.. _log-capturing-3rd-party:

Capturing 3rd-party logs
------------------------

Any 3rd-party logging library can be integrated with :mod:`logot` by sending :class:`Captured` logs to
:meth:`Logot.capture`:

.. code:: python

   def on_foo_log(logot: Logot, record: FooRecord) -> None:
      logot.capture(Captured(record.levelname, record.msg))

   foo_logger.add_handler(on_foo_log)

.. note::

   Using a context manager to set up and tear down log capture for every test run is *highly recommended*!

.. seealso::

   See :class:`Captured` and :meth:`Logot.capture` API reference.
