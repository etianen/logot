from __future__ import annotations

import pytest


def test_config_default(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        """
        def test_level(logot_level):
            assert logot_level == "DEBUG"

        def test_logger(logot_logger):
            assert logot_logger is None
        """
    )
