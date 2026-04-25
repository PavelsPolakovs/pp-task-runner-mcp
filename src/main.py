import argparse
from .deps import check_required_packages


def main():
    # Validate packages before importing modules that expect prompt_toolkit
    check_required_packages()

    # Run the menu-based FastMCP instance. The menu logic lives in
    # `src.menu_mcp_server` and handles showing the interactive start menu.
    from .mcp.server.fastmcp import FastMCP
    from .menu_mcp_server import register_tools

    parser = argparse.ArgumentParser(description="MCP Menu Runner")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport layer to use (stdio recommended for interactive menu)",
    )
    args = parser.parse_args()

    m = FastMCP("skill-menu-main")
    register_tools(m)
    m.run(transport=args.transport)


if __name__ == "__main__":
    main()
