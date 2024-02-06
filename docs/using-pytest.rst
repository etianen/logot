Using with :mod:`pytest`
========================

.. currentmodule:: logot

:mod:`logot` includes a :mod:`pytest` plugin.

The ``logot`` fixture automatically :doc:`captures logs </log-capturing>` during tests and can be used to make log
assertions:

.. code:: python

   from logot import Logot, logged

   def test_something(logot: Logot) -> None:
      do_something()
      logot.assert_logged(logged.info("Something was done"))


Installing
----------

Ensure :mod:`logot` is installed alongside a compatible :mod:`pytest` version by adding the ``pytest`` extra:

.. code:: bash

   pip install 'logot[pytest]'

.. seealso::

   See :ref:`installing-extras` usage guide.


Configuring
-----------

Use the following CLI and :external+pytest:doc:`configuration <reference/customize>` options to configure the
:mod:`pytest` plugin:

``--logot-level``, ``logot_level``
   The ``level`` used for automatic :doc:`log capturing </log-capturing>`.

   Defaults to :attr:`logot.Logot.DEFAULT_LEVEL`.

``--logot-logger``, ``logot_logger``
   The ``logger`` used for automatic :doc:`log capturing </log-capturing>`.

   Defaults to :attr:`logot.Logot.DEFAULT_LOGGER`.

``--logot-timeout``, ``logot_timeout``
   The default ``timeout`` (in seconds) for the ``logot`` fixture.

   Defaults to :attr:`logot.Logot.DEFAULT_TIMEOUT`.

``--logot-async-waiter``, ``logot_async_waiter``
   The default ``async_waiter`` for the ``logot`` fixture.

   Defaults to :attr:`logot.Logot.DEFAULT_ASYNC_WAITER`.


Available fixtures
------------------

The following fixtures are available in the :mod:`pytest` plugin:

``logot:`` :class:`logot.Logot`
   An initialized :class:`logot.Logot` instance with :doc:`log capturing </log-capturing>` enabled.

   Use this to make log assertions in your tests.

``logot_level:`` :class:`str` | :class:`int`
   The ``level`` used for automatic :doc:`log capturing </log-capturing>`.

   Defaults to :attr:`logot.Logot.DEFAULT_LEVEL`.

``logot_logger:`` :class:`str` | :data:`None`
   The ``logger`` used for automatic :doc:`log capturing </log-capturing>`.

   Defaults to :attr:`logot.Logot.DEFAULT_LOGGER`.

``logot_timeout:`` :class:`float`
   The default ``timeout`` (in seconds) for the ``logot`` fixture.

   Defaults to :attr:`logot.Logot.DEFAULT_TIMEOUT`

``logot_async_waiter:`` ``Callable`` [[], :class:`AsyncWaiter` ]
   The default ``async_waiter`` for the ``logot`` fixture.

   Defaults to :attr:`logot.Logot.DEFAULT_ASYNC_WAITER`.
