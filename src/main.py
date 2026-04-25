import argparse
from .deps import check_required_packages


def main():
    # Validate packages before importing server code that expects prompt_toolkit
    check_required_packages()

    # Import the MCP server after dependency check so the process only starts
    # when required interactive dependencies are available.
    from src.server import mcp

    parser = argparse.ArgumentParser(description="MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport layer to use",
    )
    args = parser.parse_args()
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
