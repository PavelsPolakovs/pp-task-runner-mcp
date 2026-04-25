"""Minimal local shim for the `mcp` package used by this project.

This shim is intended for local testing when the real `mcp` package
is not installed. It implements a very small subset of the API used
by the repository (FastMCP, tool decorator, run).

If you later install the real `mcp` package, that package will take
precedence when running in environments where the real package is
available on sys.path before this local module.
"""

from .server.fastmcp import FastMCP  # re-export

__all__ = ["FastMCP"]

