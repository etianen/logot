Using with :mod:`unittest`
==========================

.. currentmodule:: logot

:mod:`logot` is compatible with any testing framework, including :mod:`unittest`:

.. code:: python

   import unittest
   from logot import Logot, logged

   class MyAppTest(unittest.TestCase):

      def test_my_app(self) -> None:
         with Logot().capture() as logot:
            app.start()
            logot.wait_for(logged.info("App started"))
