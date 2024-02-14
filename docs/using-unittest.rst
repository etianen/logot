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

      def test_something(self) -> None:
         do_something()
         self.logot.assert_logged(logged.info("App started"))


Comparison to :meth:`assertLogs() <unittest.TestCase.assertLogs>`
-----------------------------------------------------------------

:mod:`unittest` includes a :meth:`assertLogs() <unittest.TestCase.assertLogs>` method that supports log capture and
testing. The above example can be rewritten using :meth:`assertLogs() <unittest.TestCase.assertLogs>` as:

.. code:: python

   class MyAppTest(TestCase):

      def test_something(self) -> None:
         with self.assertLogs(level=logging.DEBUG) as cm:
            do_something()
         assert any(
            record.levelno == logging.INFO and record.message == "Something was done"
            for record in cm.records
         )

:mod:`logot` improves on :meth:`assertLogs() <unittest.TestCase.assertLogs>` with:

- Support for :doc:`log message matching </log-message-matching>` using ``%``-style placeholders.
- Support for :doc:`log pattern matching </log-pattern-matching>` using *log pattern operators*.
- Support for testing :ref:`threaded <index-testing-threaded>` and :ref:`async <index-testing-async>` code.
- Support for :ref:`3rd-party logging frameworks <integrations-logging>` (e.g. :doc:`loguru </integrations/loguru>`,
  :doc:`structlog </integrations/structlog>`).
- A cleaner, clearer syntax.


Configuring
-----------

Override ``logot``-prefixed attributes in your test case to configure the
:attr:`logot <logot.unittest.LogotTestCase.logot>` attribute:

.. code:: python

   class MyAppTest(LogotTestCase):
      logot_level = "WARNING"
      logot_name = "app"
      logot_timeout = 10.0

.. seealso::

   See :mod:`logot.unittest.LogotTestCase` API reference.
