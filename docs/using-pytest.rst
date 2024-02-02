Using with :mod:`pytest`
========================

.. currentmodule:: logot

:mod:`logot` includes a :mod:`pytest` plugin.

The ``logot`` fixture automatically :doc:`captures logs </log-capturing>` during tests and can be used to make log
assertions:

.. code:: python

   from logot import Logot, logged

   def test_my_app(logot: Logot) -> None:
      app.start()
      logot.wait_for(logged.info("App started"))

.. seealso::

   See :class:`Logot` API reference for default settings.


Installing
----------

Ensure :mod:`logot` is installed alongside a compatible :mod:`pytest` version by adding the ``pytest`` extra:

.. code:: bash

   pip install 'logot[pytest]'

.. seealso::

   See :ref:`installing-extras` usage guide.


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
