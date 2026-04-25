from src.server import mcp


@mcp.resource("info://server")
async def server_info() -> str:
    """Returns basic server information."""
    return "my-mcp-server v0.1.0 — running and healthy."
