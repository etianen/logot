.. currentmodule:: logot

.. note::

   Use the ``timeout`` argument to :meth:`Logot.await_for` to configure how long to wait before the test fails. This can
   be configured globally with the ``timeout`` argument to :class:`Logot`, defaulting to :attr:`Logot.DEFAULT_TIMEOUT`.

.. seealso::

   See :doc:`/log-pattern-matching` for examples of how to wait for logs that may arrive in an unpredictable order.
