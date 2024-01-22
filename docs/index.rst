Log-based testing 🪵
====================

.. automodule:: logot

:mod:`logot` makes it easy to test your application is logging as expected:

.. code:: python

   from logot import Logot, logged

   def test_my_app(logot: Logot) -> None:
      app.start()
      logot.wait_for(logged.info("App started"))


Why test logging? 🤔
--------------------

Good logging ensures your application is debuggable at runtime, but why bother actually *testing* your logs? After
all... surely the worst that can happen is your logs are a bit *wonky*? 🥴

Sometimes, testing logs is the only *reasonable* way to known your code has actually run correctly! This is particularly
the case in *threaded* or *async* applications where work is carried out at unpredictable times by background workers.

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

It's certainly *possible* to rewrite this code in a way that can be tested without :mod:`logot`, but that often makes
the code less clear and more verbose. For complex threaded or async applications, this can quickly become burdensome. 👎

Meanwhile, testing this code with :mod:`logot` is easy!

.. code:: python

   def test_poll_daemon(logot: Logot) -> None:
      app.start_poll()
      for _ in range(3):
         logot.wait_for(logged.info("Poll started"))
         logot.wait_for(logged.info("Poll finished"))


.. toctree::
   :caption: Contents
   :hidden:
   :maxdepth: 1

   self
   match
   logged
