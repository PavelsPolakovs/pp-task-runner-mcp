#!/usr/bin/env python3
"""Entry point for PP Task Runner.

This script is intended to be the command referenced from `.claude/commands/pp-task-runner.md`.
By default it opens the Main Menu (runs `menu_server.py` in-process so stdout JSON
events are visible to the caller). It also supports a `menu` subcommand for clarity.
"""
import argparse
import os
import runpy
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pp_task_runner")
    parser.add_argument("command", nargs="?", default="menu", help="Command to run (menu)")
    parser.add_argument("--description", help="Optional description (not shown in Monitor UI)")
    args = parser.parse_args(argv)

    if args.command in ("menu",):
        # Execute the standalone menu server in this process so its stdout is
        # directly visible to Monitor/Claude (prints JSON lines).
        path = os.path.join(os.path.dirname(__file__), "src", "menu_server", "menu_server.py")
        runpy.run_path(path, run_name="__main__")
    else:
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()

