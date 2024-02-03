Using with :mod:`unittest`
==========================

.. currentmodule:: logot

:mod:`logot` includes :class:`logot.unittest.LogotTestCase` for easy integration with :mod:`unittest`.

The :attr:`logot <logot.unittest.LogotTestCase.logot>` attribute automatically :doc:`captures logs </log-capturing>`
during tests and can be used to make log assertions:

.. code:: python

   from logot import logged
   from logot.unittest import LogotTestCase

   class MyAppTest(LogotTestCase):

      def test_app(self) -> None:
         do_something()
         self.logot.assert_logged(logged.info("App started"))


Configuring
-----------

Override ``logot``-prefixed attributes in your test case to configure the
:attr:`logot <logot.unittest.LogotTestCase.logot>` attribute:

.. code:: python

   class MyAppTest(LogotTestCase):
      logot_level = logging.WARNING
      logot_logger = "app"
      logot_timeout = 10.0

.. seealso::

   See :mod:`logot.unittest.LogotTestCase` API reference.
