Using with :mod:`loguru`
========================

.. currentmodule:: logot

:mod:`logot` makes it easy to capture logs from :mod:`loguru`:

.. code:: python

   from logot.loguru import LoguruCapturer

   with Logot(capturer=LoguruCapturer).capturing() as logot:
      do_something()
      logot.assert_logged(logged.info("App started"))


Installing
----------

Ensure :mod:`logot` is installed alongside a compatible :mod:`loguru` version by adding the ``loguru`` extra:

.. code:: bash

   pip install 'logot[loguru]'

.. seealso::

   See :ref:`installing-extras` usage guide.


Enabling for :mod:`pytest`
--------------------------

Enable :mod:`loguru` support in your :external+pytest:doc:`pytest configuration <reference/customize>`:

.. code:: ini

   # pytest.ini or .pytest.ini
   [pytest]
   logot_capturer = logot.loguru.LoguruCapturer

.. code:: toml

   # pyproject.toml
   [tool.pytest.ini_options]
   logot_capturer = "logot.loguru.LoguruCapturer"

.. seealso::

   See :doc:`/using-pytest` usage guide.


Enabling for :mod:`unittest`
----------------------------

Enable :mod:`loguru` support in your :class:`logot.unittest.LogotTestCase`:

.. code:: python

   from logot.loguru import LoguruCapturer

   class MyAppTest(LogotTestCase):
      logot_capturer = LoguruCapturer

.. seealso::

   See :doc:`/using-unittest` usage guide.


Enabling manually
-----------------

Enable :mod:`loguru` support for your :class:`Logot` instance:

.. code:: python

   from logot.loguru import LoguruCapturer

   logot = Logot(capturer=LoguruCapturer)

Enable :mod:`loguru` support for a single :meth:`Logot.capturing` call:

.. code:: python

   with Logot().capturing(capturer=LoguruCapturer) as logot:
      do_something()

.. seealso::

   See :class:`Logot` and :meth:`Logot.capturing` API reference.
