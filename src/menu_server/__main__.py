"""Module entrypoint to run the menu server as a package:

Usage:
    python -m menu_server

This delegates to the existing module implementation so behaviour remains
identical to running the script directly.
"""
import runpy


if __name__ == "__main__":
    # Execute the module so that package-relative imports work correctly.
    runpy.run_module("menu_server.menu_server", run_name="__main__")

