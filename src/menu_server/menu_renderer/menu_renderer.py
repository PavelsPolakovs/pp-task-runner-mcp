
"""HTML renderer for the standalone menu server.

This module contains the logic previously embedded inside
`src/menu_server/menu_server.py` for generating the full HTML page,
CSS and JS. It exposes a single public function `render_menu_html(tasks)`.
"""
from typing import Dict
from .html_builder import _build_html


# `_build_html` and its helper functions have been moved to
# `html_builder.py`. Import the builder here and keep this module as a
# small public wrapper.


def render_menu_html(tasks: Dict[str, str]) -> str:
	"""Public API: render the full HTML page for the given tasks mapping.

	Returns a string (not bytes) — callers can encode it as needed.
	"""
	return _build_html(tasks)


