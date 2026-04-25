#!/usr/bin/env python3
"""Simple wrapper to run the menu-based MCP server from the repository root.

This script ensures the local `src` package is importable and then calls
the existing `src.main` entrypoint. It is intentionally minimal so it can be
referenced directly by external tools (for example: `claude mcp add ...`).
"""
import os
import sys


REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# Ensure local `src` directory is importable as a package
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

# Change working directory to repository root to make relative paths stable
os.chdir(REPO_ROOT)


def main():
    # Defer imports until after PYTHONPATH is configured above
    from src.main import main as src_main

    return src_main()


if __name__ == "__main__":
    main()

