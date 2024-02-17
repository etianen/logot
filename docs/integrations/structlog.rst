Using with :mod:`structlog`
============================

.. currentmodule:: logot

:mod:`logot` makes it easy to capture logs from :mod:`structlog`:

.. code:: python

   from logot.structlog import StructlogCapturer

   with Logot(capturer=StructlogCapturer).capturing() as logot:
      do_something()
      logot.assert_logged(logged.info("App started"))

:mod:`logot` preserves the preconfigured :mod:`structlog` processor chain. Events are captured at the end of the chain,
but before the final processor, as it is responsible for emitting the log event to the underlying logging system. For
more information, see the
`structlog documentation <https://www.structlog.org/en/stable/processors.html#adapting-and-rendering>`_.

.. note::

   :class:`logot.structlog.StructlogCapturer` works by changing the :mod:`structlog` configuration. If you have
   `cache_logger_on_first_use` enabled in your :func:`structlog.configure` or :func:`structlog.wrap_logger` call for
   performance reasons, you will need to disable it during tests to enable log capturing.


Installing
----------

Ensure :mod:`logot` is installed alongside a compatible :mod:`structlog` version by adding the ``structlog`` extra:

.. code:: bash

   pip install 'logot[structlog]'

.. seealso::

   See :ref:`installing-extras` usage guide.


Enabling for :mod:`pytest`
--------------------------

Enable :mod:`structlog` support in your :external+pytest:doc:`pytest configuration <reference/customize>`:

.. code:: ini

   # pytest.ini or .pytest.ini
   [pytest]
   logot_capturer = logot.structlog.StructlogCapturer

.. code:: toml

   # pyproject.toml
   [tool.pytest.ini_options]
   logot_capturer = "logot.structlog.StructlogCapturer"

.. seealso::

   See :doc:`/using-pytest` usage guide.


Enabling for :mod:`unittest`
----------------------------

Enable :mod:`structlog` support in your :class:`logot.unittest.LogotTestCase`:

.. code:: python

   from logot.structlog import StructlogCapturer

   class MyAppTest(LogotTestCase):
      logot_capturer = StructlogCapturer

.. seealso::

   See :doc:`/using-unittest` usage guide.


Enabling manually
-----------------

Enable :mod:`structlog` support for your :class:`Logot` instance:

.. code:: python

   from logot.structlog import StructlogCapturer

   logot = Logot(capturer=StructlogCapturer)

Enable :mod:`structlog` support for a single :meth:`Logot.capturing` call:

.. code:: python

   with Logot().capturing(capturer=StructlogCapturer) as logot:
      do_something()

.. seealso::

   See :class:`Logot` and :meth:`Logot.capturing` API reference.
