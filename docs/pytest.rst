Using with :mod:`pytest`
========================

.. currentmodule:: logot

:mod:`logot` includes a :mod:`pytest` plugin. Just use the ``logot`` fixture in your tests:

.. code:: python

   from logot import Logot, logged

   def test_my_app(logot: Logot) -> None:
      app.start()
      logot.wait_for(logged.info("App started"))

.. note::

   The ``logot`` fixture is configured with default settings and captures all logs in the root logger.

.. seealso::

   See :class:`Logot` API reference for default settings.


Customizing the ``logot`` fixture
---------------------------------

To customize the ``logot`` fixure, simply override it in your own ``conftest.py``:

.. code:: python

   import pytest
   from logot import Logot, logged

   @pytest.fixture()
   def logot():
      with Logot(timeout=30.0).capturing(level=logging.WARNING) as logot:
         yield logot

.. seealso::

   See :class:`Logot` and :meth:`Logot.capturing` API reference.
