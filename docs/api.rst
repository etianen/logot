API reference
=============

.. currentmodule:: logot

Import the :mod:`logot` API in your tests:

.. code:: python

   from logot import Logot, logged


:mod:`logot`
------------

.. module:: logot

.. autoclass:: logot.Logot

   .. automethod:: capturing

   .. automethod:: capture

   .. automethod:: wait_for

   .. automethod:: await_for

   .. automethod:: assert_logged

   .. automethod:: assert_not_logged

   .. automethod:: clear

   .. autoattribute:: DEFAULT_LEVEL

   .. autoattribute:: DEFAULT_LOGGER

   .. autoattribute:: DEFAULT_TIMEOUT

.. autoclass:: logot.Logged

.. autoclass:: logot.Captured


:mod:`logot.logged`
-------------------

.. module:: logot.logged

.. autofunction:: logot.logged.log

.. autofunction:: logot.logged.debug

.. autofunction:: logot.logged.info

.. autofunction:: logot.logged.warning

.. autofunction:: logot.logged.error

.. autofunction:: logot.logged.critical
