import argparse


def main():
    # Minimal menu runner: do not perform extra dependency checks — assume
    # the environment has the required interactive packages installed.
    from mcp.server.fastmcp import FastMCP
    from .menu_mcp import register_tools

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
