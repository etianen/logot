3rd-party integrations
======================

.. currentmodule:: logot

:mod:`logot` integrates with a number of 3rd-party frameworks to extend its functionality.

.. note::

   Adding support for additional 3rd-party frameworks is an excellent way of
   `contributing <https://github.com/etianen/logot/blob/main/CONTRIBUTING.md>`_ to :mod:`logot`! 🙇


.. _integrations-async:

Asynchronous frameworks
-----------------------

Integrations with 3rd-party asynchronous frameworks extend :meth:`Logot.await_for`, allowing you to
:ref:`test asynchronous code <index-testing-async>` using your framework of choice. 💪

Supported frameworks:

.. toctree::
   :maxdepth: 1

   trio

.. seealso::

   See :ref:`index-testing-async` usage guide.

   See :class:`AsyncWaiter` API reference for integrating with 3rd-party asynchronous frameworks.


.. _integrations-logging:

Logging frameworks
------------------

Integrations with 3rd-party logging frameworks extend :meth:`Logot.capturing`, allowing you to
:doc:`capture logs </log-capturing>` using your framework of choice. 💪

Supported frameworks:

.. toctree::
   :maxdepth: 1

   loguru
   structlog

.. seealso::

   See :doc:`/log-capturing` usage guide.

   See :class:`Capturer` API reference for integrating with 3rd-party logging frameworks.
