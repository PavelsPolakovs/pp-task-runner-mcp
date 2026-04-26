"""Package shim for the menu HTML renderer.

Expose a single public function `render_menu_html` so callers can import
`from menu_server.menu_renderer import render_menu_html`.
"""
from .menu_renderer import render_menu_html

__all__ = ["render_menu_html"]

