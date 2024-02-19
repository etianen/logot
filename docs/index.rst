Log-based testing 🪵
====================

.. currentmodule:: logot

:mod:`logot` makes it easy to test whether your code is logging correctly:

.. code:: python

   from logot import Logot, logged

   def test_something(logot: Logot) -> None:
      do_something()
      logot.assert_logged(logged.info("Something was done"))

.. note::

   :mod:`logot` integrates with popular testing (:doc:`pytest </using-pytest>`, :doc:`unittest </using-unittest>`),
   asynchronous (:ref:`asyncio <index-testing-threaded>`, :ref:`3rd-party <integrations-async>`) and logging frameworks
   (:doc:`logging </log-capturing>`, :ref:`3rd-party <integrations-logging>`). It can be extended to support many
   others. 💪


Why test logging? 🤔
--------------------

Good logging ensures your code is debuggable at runtime, but why bother actually *testing* your logs?

Sometimes, testing logs is the only *reasonable* way to known your code has actually run correctly! This is particularly
the case in *threaded* or *asynchronous* code.

For example, imagine the following code running in a thread:

.. code:: python

   def poll_daemon(app: App) -> None:
      while not app.stopping:
         sleep(app.poll_interval)
         logger.debug("Poll started")
         try:
            app.data = app.get("http://is-everything-ok.com/")
         except HTTPError:
            logger.exception("Poll error")
         else:
            logger.debug("Poll finished")

.. note::

   While it's *possible* to rewrite this code in a way that can be tested without :mod:`logot`, that risks making the
   code less clear or more verbose. For complex threaded or asynchronous code, this can quickly become burdensome. 👎

Testing this code with :mod:`logot` is easy!

.. code:: python

   from logot import Logot, logged

   def test_poll_daemon(logot: Logot) -> None:
      app.start_poll()
      for _ in range(3):
         logot.wait_for(logged.info("Poll started"))
         logot.wait_for(logged.info("Poll finished"))


.. _index-testing-threaded:

Testing threaded code
---------------------

Use :meth:`Logot.wait_for` to pause your test until the expected logs arrive or the ``timeout`` expires:

.. code:: python

   from logot import Logot, logged

   def test_app(logot: Logot) -> None:
      app.start()
      logot.wait_for(logged.info("App started"))

.. note::

   Use the ``timeout`` argument to :meth:`Logot.wait_for` to configure how long to wait before the test fails. This can
   be configured globally with the ``timeout`` argument to :class:`Logot`, defaulting to :attr:`Logot.DEFAULT_TIMEOUT`.

.. seealso::

   See :doc:`/log-pattern-matching` for examples of how to wait for logs that may arrive in an unpredictable order.


.. _index-testing-async:

Testing asynchronous code
-------------------------

Use :meth:`Logot.await_for` to pause your test until the expected logs arrive or the ``timeout`` expires:

.. code:: python

   from logot import Logot, logged

   async def test_app(logot: Logot) -> None:
      asyncio.create_task(app.start())
      await logot.await_for(logged.info("App started"))

.. note::

   Use the ``timeout`` argument to :meth:`Logot.await_for` to configure how long to wait before the test fails. This can
   be configured globally with the ``timeout`` argument to :class:`Logot`, defaulting to :attr:`Logot.DEFAULT_TIMEOUT`.

.. seealso::

   See :doc:`/log-pattern-matching` for examples of how to wait for logs that may arrive in an unpredictable order.

   See :ref:`integrations-async` for other supported asynchronous frameworks.


Testing synchronous code
------------------------

Use :meth:`Logot.assert_logged` to fail *immediately* if the expected logs have not arrived:

.. code:: python

   from logot import Logot, logged

   def test_something(logot: Logot) -> None:
      do_something()
      logot.assert_logged(logged.info("Something was done"))

.. note::

   You can also use :meth:`Logot.wait_for` to test for expected logs, but since this only fails after a ``timeout``,
   using :meth:`Logot.assert_logged` will give more immediate feedback if your test fails.

.. seealso::

   Use :meth:`Logot.assert_not_logged` to fail *immediately* if the expected logs *do* arrive.


Further reading
---------------

Learn more about :mod:`logot` with the following guides:

.. toctree::
   :hidden:
   :maxdepth: 1

   self

.. toctree::
   :maxdepth: 1

   log-message-matching
   log-pattern-matching
   log-capturing
   using-pytest
   using-unittest
   installing
   integrations/index
   api/index

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Project links

   GitHub repository <https://github.com/etianen/logot>
   PyPI project <https://pypi.org/project/logot/>
   Changelog <https://github.com/etianen/logot/releases>
