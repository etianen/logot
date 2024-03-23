"""
Main :mod:`logot` API for log-based testing.

.. seealso::

    See :doc:`/index` usage guide.
"""

from __future__ import annotations

from logot._capture import Captured as Captured
from logot._logged import Logged as Logged
from logot._logot import Capturer as Capturer
from logot._logot import Logot as Logot
from logot._wait import AsyncWaiter as AsyncWaiter
