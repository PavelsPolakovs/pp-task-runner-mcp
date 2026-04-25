"""Module-level FastMCP instance for `mcp dev dev_server.py:mcp`.

Run with:
    mcp dev dev_server.py:mcp
    make dev
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mcp.server.fastmcp import FastMCP
from menu_mcp import register_tools

mcp = FastMCP("pp-task-runner")
register_tools(mcp)