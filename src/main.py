import argparse
import os

_INSTRUCTIONS = """
PP Task Runner — Interactive Browser Menu

## Menus

All menus are defined in task_config.json (single source of truth):
- "main" — default menu (shown on /pp-task-runner)
- "qa"   — testing/linting tasks

## Preferred usage — Monitor tool (non-blocking)

Use this approach so Claude stays free while waiting for browser input.

When the user invokes /pp-task-runner or asks to open the task menu:

1. Call `get_menu_command` to get the shell command for the menu server.
   For QA tasks call `get_menu_command(menu="qa")`.
2. Run the returned command with the Monitor tool:
   persistent=false, timeout_ms=300000, description="pp-task-runner menu"
3. Handle each JSON notification line emitted to stdout.
   The server stays alive after each skill selection, so do NOT restart Monitor after greet:
   - {"action": "greet", "name": "...", "message": "..."} → print the message and keep listening
   - {"action": "exit"} → print "Goodbye !!!" and stop
   - {"action": "close"} → tell the user the browser was closed
   - {"action": "timeout"} → tell the user the menu timed out

## Alternative — blocking MCP tool

`open_menu(menu=None)` does the same but blocks Claude until the user acts.
Use only when Monitor is unavailable.

## Other tools

- `get_menu_command(menu=None)` — return Monitor-ready shell command for the menu server
- `list_skills(menu=None)` — list tasks for a menu (default: main)
- `select_skill(name, menu=None)` — activate a task by name without opening the browser
- `get_active_skill` — return the currently active task name and description
- `update` — pull the latest changes from the remote repo, then reconnect the MCP server
"""

_SKILL_CONTENT = """\
1. Call `get_menu_command` from the `pp-task-runner` MCP server.
2. Run the returned command with Monitor (persistent=false, timeout_ms=300000, description="pp-task-runner menu").
"""


def main():
    parser = argparse.ArgumentParser(description="PP Task Runner MCP server")
    subparsers = parser.add_subparsers(dest="command")

    serve_parser = subparsers.add_parser("serve", help="Run the MCP server (default)")
    serve_parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport layer (stdio recommended)",
    )

    install_parser = subparsers.add_parser(
        "install",
        help="Install the /pp-task-runner Claude Code skill into a project",
    )
    install_parser.add_argument(
        "--project-dir",
        default=".",
        help="Project root directory (default: current working directory)",
    )

    # Keep --transport at top level for backwards compatibility:
    #   python3 server.py --transport stdio
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help=argparse.SUPPRESS,
    )

    args = parser.parse_args()

    if args.command == "install":
        _install_skill(args.project_dir)
    else:
        _serve(args.transport)


def _install_skill(project_dir: str) -> None:
    commands_dir = os.path.join(os.path.abspath(project_dir), ".claude", "commands")
    os.makedirs(commands_dir, exist_ok=True)
    skill_path = os.path.join(commands_dir, "pp-task-runner.md")
    with open(skill_path, "w", encoding="utf-8") as f:
        f.write(_SKILL_CONTENT)
    print(f"Installed: {skill_path}")
    print("Restart Claude Code to pick up the new /pp-task-runner command.")


def _serve(transport: str) -> None:
    from mcp.server.fastmcp import FastMCP

    from .menu_mcp import register_tools

    m = FastMCP("pp-task-runner", instructions=_INSTRUCTIONS)
    register_tools(m)
    m.run(transport=transport)


if __name__ == "__main__":
    main()