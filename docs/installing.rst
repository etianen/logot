Installing
==========

Install :mod:`logot` like any other Python library:

.. code:: bash

   pip install 'logot'

.. important::

   It's good practice to install libraries in a virtual environment using :mod:`venv`. This ensures your dependencies
   are isolated from your system Python and other projects.


.. _installing-extras:

Installing package ``extras``
-----------------------------

:mod:`logot` provides package ``extras`` to ensure compatibility with supported
:doc:`3rd-party integrations </integrations/index>`.

.. code:: bash

   pip install 'logot[loguru,pytest,trio]'

Use the following package ``extras`` for supported 3rd-party integrations:

- ``loguru`` - :doc:`/integrations/loguru`
- ``pytest`` - :doc:`/using-pytest`
- ``trio`` - :doc:`/integrations/trio`

.. seealso::

   See :doc:`/integrations/index` usage guide.


Installing with Poetry
----------------------

`Poetry <https://python-poetry.org/>`_ is an excellent Python packaging and dependency management tool. It takes care of
installing dependencies and automatically manages virtual environments. 💪

.. code:: bash

   poetry add 'logot'

.. note::

   Installation examples in these docs use ``pip install`` for clarity, but Poetry is still a *highly recommended*
   alternative! Simply replace ``pip install`` with ``poetry add`` in all installation examples.
