API reference
=============

.. currentmodule:: logot

:mod:`logot`
------------

.. module:: logot

.. autoclass:: logot.Logot

   .. automethod:: capturing

   .. automethod:: assert_logged

   .. automethod:: assert_not_logged

   .. automethod:: wait_for

   .. automethod:: await_for

   .. autoattribute:: DEFAULT_LEVEL

   .. autoattribute:: DEFAULT_LOGGER

   .. autoattribute:: DEFAULT_TIMEOUT

.. autoclass:: logot.Logged


:mod:`logot.logged`
-------------------

.. module:: logot.logged

.. autofunction:: logot.logged.log

.. autofunction:: logot.logged.debug

.. autofunction:: logot.logged.info

.. autofunction:: logot.logged.warning

.. autofunction:: logot.logged.error

.. autofunction:: logot.logged.critical
