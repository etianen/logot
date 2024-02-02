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


Customizing log capturing
-------------------------

Use the following :mod:`pytest` CLI and :external+pytest:doc:`configuration <reference/customize>` options to
customize automatic :doc:`log capturing </log-capturing>`:

``--logot-level``, ``logot_level``
   The ``level`` used for automatic :doc:`log capturing </log-capturing>`.

   Defaults to :attr:`logot.Logot.DEFAULT_LEVEL`.

``--logot-logger``, ``logot_logger``
   The ``logger`` used for automatic :doc:`log capturing </log-capturing>`.

   Defaults to :attr:`logot.Logot.DEFAULT_LOGGER`.

``--logot-timeout``, ``logot_timeout``
   The default ``timeout`` (in seconds) for the ``logot`` fixture..

   Defaults to :attr:`logot.Logot.DEFAULT_TIMEOUT`.
