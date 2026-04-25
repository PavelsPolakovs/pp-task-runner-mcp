from src.server import mcp


@mcp.tool()
async def add(a: float, b: float) -> float:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number
    """
    return a + b
