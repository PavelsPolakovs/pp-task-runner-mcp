import pytest
from mcp.server.fastmcp import FastMCP
from menu_mcp import register_tools
from menu_mcp.state import _menu


@pytest.fixture()
def mcp_app():
    """Fresh FastMCP instance with all tools registered."""
    app = FastMCP("test-server")
    register_tools(app)
    return app


@pytest.fixture(autouse=True)
def reset_menu():
    """Reset shared _menu state before and after each test."""
    _menu.server = None
    while not _menu.events.empty():
        try:
            _menu.events.get_nowait()
        except Exception:
            break
    yield
    with _menu.lock:
        server = _menu.server
        _menu.server = None
    if server:
        server.shutdown()