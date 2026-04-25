from src.server import mcp


@mcp.prompt()
async def greet_user(name: str) -> str:
    """A simple greeting prompt template.

    Args:
        name: The user's name
    """
    return f"Please greet the user named {name} in a friendly and professional manner."
