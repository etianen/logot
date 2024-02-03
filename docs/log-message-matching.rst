Log message matching
====================

.. currentmodule:: logot

:mod:`logot` makes it easy to match log messages using ``%``-style placeholders:

.. code:: python

   from logot import Logot, logged

   def test_something(logot: Logot) -> None:
      do_something()
      logot.assert_logged(logged.info("Something %s done"))

In this case, the ``%s`` placeholder will match *any* string!


Available placeholders
----------------------

The following placeholders are available, each corresponding to a formatting option from the stdlib :mod:`logging`
module:

===========  ===========================================================================================================
Placeholder  Matches
===========  ===========================================================================================================
``%d``       Signed integer decimal.
``%i``       Signed integer decimal.
``%o``       Signed octal value.
``%u``       Signed integer decimal.
``%x``       Signed hexadecimal (lowercase).
``%X``       Signed hexadecimal (uppercase).
``%e``       Floating point exponential format (lowercase).
``%E``       Floating point exponential format (uppercase).
``%f``       Floating point decimal format (lowercase).
``%F``       Floating point decimal format (uppercase).
``%g``       Floating point format. Uses lowercase exponential format if exponent is less than -4 or not less than precision, decimal format otherwise.
``%G``       Floating point format. Uses uppercase exponential format if exponent is less than -4 or not less than precision, decimal format otherwise.
``%c``       Single character.
``%r``       Any string (non-greedy).
``%s``       Any string (non-greedy).
``%a``       Any string (non-greedy).
``%%``       Escape sequence, results in a ``%`` character in the result.
===========  ===========================================================================================================
