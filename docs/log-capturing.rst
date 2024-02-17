Log capturing
=============

.. currentmodule:: logot

:mod:`logot` makes it easy to capture logs from the stdlib :mod:`logging` module:

.. code:: python

   with Logot().capturing() as logot:
      do_something()
      logot.assert_logged(logged.info("App started"))

.. seealso::

   See :ref:`integrations-logging` for other supported logging frameworks (e.g. :doc:`loguru </integrations/loguru>`, :doc:`structlog </integrations/structlog>`).


Test framework integrations
---------------------------

Use a supported test framework integration for automatic log capturing in tests:

- :doc:`/using-pytest`
- :doc:`/using-unittest`


Configuring
-----------

The :meth:`Logot.capturing` method defaults to capturing **all** records from the root logger. Customize this with the
``level`` and ``name`` arguments to :meth:`Logot.capturing`:

.. code:: python

   with Logot().capturing(level=logging.WARNING, name="app") as logot:
      do_something()
      logot.assert_logged(logged.info("App started"))

For advanced use-cases, multiple :meth:`Logot.capturing` calls on the same :class:`Logot` instance are supported. Be
careful to avoid capturing duplicate logs with overlapping calls to :meth:`Logot.capturing`!

.. seealso::

   See :class:`Logot` and :meth:`Logot.capturing` API reference.
