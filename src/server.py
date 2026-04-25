import sys
import logging
from contextlib import asynccontextmanager

# Use a relative import so src can be executed as a package (python -m src.main)
# and the top-level `mcp/` shim becomes optional. This resolves imports to
# the implementation in `src/mcp/...` when the package is run as a module.
from .mcp.server.fastmcp import FastMCP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(server):
    print("✅ MCP Server connected and ready!", file=sys.stderr)
    logger.info("Server started successfully.")
    yield
    logger.info("Server shutting down.")


mcp = FastMCP("my-mcp-server", lifespan=lifespan)


@mcp.tool()
async def hello(name: str) -> str:
    """Say hello to someone.

    Args:
        name: The person's name
    """
    return f"Hello, {name}! MCP server is running."
