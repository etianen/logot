Log pattern matching
====================

.. currentmodule:: logot

:mod:`logot` makes it easy to match logs that may arrive in an unpredictable order. This is especially useful in
*threaded* or *asynchronous* code!

Compose your :mod:`logot.logged` calls with special *log pattern operators*:

.. code:: python

   from logot import Logot, logged

   def test_my_app(logot: Logot) -> None:
      app.start()
      logot.wait_for(
         # Wait for the app to start...
         logged.info("App started")
         # ...then wait for the app to stop *or* crash!
         >> (
            logged.info("App stopped")
            | logged.error("App crashed!")
         )
      )

.. note::

   Log pattern operators are *infinitely* composable! Use ``()`` brackets when needed to define complex log patterns.


Available operators
-------------------

Sequential logs
~~~~~~~~~~~~~~~

Use the ``>>`` operator to wait for logs that must arrive in a *sequential* order:

.. code:: python

   from logot import Logot, logged

   def test_my_app(logot: Logot) -> None:
      app.start()
      logot.wait_for(
         logged.info("App started")
         >> logged.info("App stopped")
      )


Parallel logs
~~~~~~~~~~~~~

Use the ``&`` operator to wait for logs that must arrive in *any* order:

.. code:: python

   from logot import Logot, logged

   def test_my_app(logot: Logot) -> None:
      app.start()
      other_app.start()
      logot.wait_for(
         logged.info("App started")
         & logged.info("Other app started")
      )


Any logs
~~~~~~~~

Use the ``|`` operator to wait for *any* matching log pattern:

.. code:: python

   from logot import Logot, logged

   def test_my_app(logot: Logot) -> None:
      app.start()
      logot.wait_for(
         logged.info("App stopped")
         | logged.error("App crashed!")
      )
