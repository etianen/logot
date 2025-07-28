from __future__ import annotations

from datetime import date
from pathlib import Path

import tomllib

_root = Path(__file__).parent.parent
_project = tomllib.loads((_root / "pyproject.toml").read_text())["project"]

project = _project["name"]
release = version = _project["version"]
author = ", ".join(f"{author['name']} <{author['email']}>" for author in _project["authors"])
copyright = f"{date.today().year} Dave Hall"

exclude_patterns = ["_build"]

html_theme = "furo"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
]

autodoc_member_order = "bysource"

autodoc_preserve_defaults = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "loguru": ("https://loguru.readthedocs.io/en/latest/", None),
    "pytest": ("https://docs.pytest.org/en/latest/", None),
    "structlog": ("https://www.structlog.org/en/latest/", None),
    "trio": ("https://trio.readthedocs.io/en/latest/", None),
}

nitpicky = True
