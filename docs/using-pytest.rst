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


Comparison to ``caplog``
------------------------

:mod:`pytest` includes a ``caplog`` fixture that supports log capture and testing. The above example can be rewritten
using ``caplog`` as:

.. code:: python

   def test_something(caplog: pytest.LogCaptureFixture) -> None:
      do_something()
      assert any(
         record.levelno == logging.INFO and record.message == "Something was done"
         for record in caplog.records
      )

:mod:`logot` improves on ``caplog`` with:

- Support for :doc:`log message matching </log-message-matching>` using ``%``-style placeholders.
- Support for :doc:`log pattern matching </log-pattern-matching>` using *log pattern operators*.
- Support for testing :ref:`threaded <index-testing-threaded>` and :ref:`async <index-testing-async>` code.
- Support for :ref:`3rd-party logging frameworks <integrations-logging>` (e.g. :doc:`loguru </integrations/loguru>`).
- A cleaner, clearer syntax.


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

``--logot-name``, ``logot_name``
   The ``name`` used for automatic :doc:`log capturing </log-capturing>`.

   Defaults to :attr:`logot.Logot.DEFAULT_NAME`.

``--logot-capturer``, ``logot_capturer``
   The default ``capturer`` for the ``logot`` fixture.

   Defaults to :attr:`logot.Logot.DEFAULT_CAPTURER`.

``--logot-timeout``, ``logot_timeout``
   The default ``timeout`` (in seconds) for the ``logot`` fixture.

   Defaults to :attr:`logot.Logot.DEFAULT_TIMEOUT`.

``--logot-async-waiter``, ``logot_async_waiter``
   The default ``async_waiter`` for the ``logot`` fixture.

   Defaults to :attr:`logot.Logot.DEFAULT_ASYNC_WAITER`.

.. note::

   When both CLI and :external+pytest:doc:`configuration <reference/customize>` options are given, the CLI option takes
   precidence.


Available fixtures
------------------

The following fixtures are available in the :mod:`pytest` plugin:

``logot:`` :class:`logot.Logot`
   An initialized :class:`logot.Logot` instance with :doc:`log capturing </log-capturing>` enabled.

``logot_level:`` :class:`str` | :class:`int`
   The ``level`` used for automatic :doc:`log capturing </log-capturing>`.

``logot_name:`` :class:`str` | :data:`None`
   The ``name`` used for automatic :doc:`log capturing </log-capturing>`.

``logot_capturer:`` ``Callable`` [[], :class:`Capturer` ]
   The default ``capturer`` for the ``logot`` fixture.

``logot_timeout:`` :class:`float`
   The default ``timeout`` (in seconds) for the ``logot`` fixture.

``logot_async_waiter:`` ``Callable`` [[], :class:`AsyncWaiter` ]
   The default ``async_waiter`` for the ``logot`` fixture.
