"""Module entrypoint to run the menu server as a package:

Usage:
    python -m menu_server

This delegates to the existing module implementation so behaviour remains
identical to running the script directly.
"""
from menu_server.menu_server import main


if __name__ == "__main__":
    raise SystemExit(main())

