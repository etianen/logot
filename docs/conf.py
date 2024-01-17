from __future__ import annotations

from datetime import date
from pathlib import Path

import tomli

_root = Path(__file__).parent.parent
_poetry = tomli.loads((_root / "pyproject.toml").read_text())["tool"]["poetry"]

project = _poetry["name"]
release = version = _poetry["version"]
author = ", ".join(author[0] for author in _poetry["authors"])
copyright = f"{date.today().year} Dave Hall"

exclude_patterns = ["_build"]

html_theme = "furo"
html_title = _poetry["name"]

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
]

autoclass_content = "both"
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
}
autodoc_member_order = "groupwise"
autodoc_typehints = "both"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}