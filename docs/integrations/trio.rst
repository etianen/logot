Using with :mod:`trio`
======================

.. currentmodule:: logot

Use :meth:`Logot.await_for` to pause your test until the expected logs arrive or the ``timeout`` expires:

.. code:: python

   from logot import Logot, logged

   async def test_app(logot: Logot) -> None:
      async with trio.open_nursery() as nursery:
         nursery.start_soon(app.start())
         await logot.await_for(logged.info("App started"))

.. include:: /include/testing-async-notes.rst


Installing
----------

Ensure :mod:`logot` is installed alongside a compatible :mod:`trio` version by adding the ``trio`` extra:

.. code:: bash

   pip install 'logot[trio]'

.. seealso::

   See :ref:`installing-extras` usage guide.


Enabling for :mod:`pytest`
--------------------------

Enable :mod:`trio` support in your :external+pytest:doc:`pytest configuration <reference/customize>`:

.. code:: ini

   # pytest.ini or .pytest.ini
   [pytest]
   logot_async_waiter = logot.trio.TrioWaiter

.. code:: toml

   # pyproject.toml
   [tool.pytest.ini_options]
   logot_async_waiter = "logot.trio.TrioWaiter"

.. seealso::

   See :doc:`/using-pytest` usage guide.


Enabling for :mod:`unittest`
----------------------------

Enable :mod:`trio` support in your :class:`logot.unittest.LogotTestCase`:

.. code:: python

   from logot.trio import TrioWaiter

   class MyAppTest(LogotTestCase):
      logot_async_waiter = TrioWaiter

.. seealso::

   See :doc:`/using-unittest` usage guide.


Enabling manually
-----------------

Enable :mod:`trio` support for your :class:`Logot` instance:

.. code:: python

   from logot.trio import TrioWaiter

   logot = Logot(async_waiter=TrioWaiter)

Enable :mod:`trio` support for a single :meth:`Logot.await_for` call:

.. code:: python

   await logot.await_for(logged.info("App started"), async_waiter=TrioWaiter)

.. seealso::

   See :class:`Logot` and :meth:`Logot.await_for` API reference.
