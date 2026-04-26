
"""Menu MCP package.

Modules:
- constants.py: MENUS registry loaded from task_config.json (single source of truth)
- state.py: HTTP server state and helpers
- web.py: HTML builder and HTTP handler factory
- tools.py: MCP tool registrations
"""
from .tools import register_tools

__all__ = ["register_tools"]

