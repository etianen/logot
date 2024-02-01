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

      def test_my_app(self) -> None:
         app.start()
         self.logot.wait_for(logged.info("App started"))

.. seealso::

   See :mod:`logot.unittest` API reference.


Customizing log capturing
-------------------------

Override :mod:`logot`-prefixed attributes in your :class:`logot.unittest.LogotTestCase` subclass to customize automatic
:doc:`log capturing </log-capturing>`:

.. code:: python

   class MyAppTest(LogotTestCase):

      logot_level = logging.WARNING
