"""Compatibility shim — re-export shared button rendering from menu_mcp.

The original implementation lived here; it has been moved to
`src/menu_mcp/menu_renderer/components/button.py` so `menu_mcp` is the
single source of truth for UI components. Keep a tiny shim here so code
that still imports the old module path keeps working until the directory
is removed manually.
"""
from menu_mcp.menu_renderer.components.button import _render_button

__all__ = ["_render_button"]




