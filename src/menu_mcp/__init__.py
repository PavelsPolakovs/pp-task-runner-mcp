"""Menu MCP package exposing register_tools.

This package contains modularized parts of the original
`menu_mcp_server.py` split into small files:
- constants.py: SKILLS and timeouts
- state.py: server state and helpers
- web.py: HTML builder and HTTP handler factory
- tools.py: register_tools implementation
"""
from .tools import register_tools

__all__ = ["register_tools"]

